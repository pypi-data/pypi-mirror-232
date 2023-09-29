from abc import abstractmethod

from transformers import AutoModel, AutoTokenizer, BitsAndBytesConfig
from typing import List, Union, Dict, Any, Generator, Iterator, Tuple

from gqlalchemy import Memgraph
from gqlalchemy.exceptions import GQLAlchemySubclassNotFoundWarning
import re
import openai
from openai.openai_object import OpenAIObject
from memchain.prompts import SCHEMA_QUERY, QUESTION_QUERY, QA_PROMPT, CYPHER_GENERATION_TEMPLATE, \
    SQL_GENERATION_TEMPLATE
import os
import logging
import warnings
import hashlib
import torch

warnings.filterwarnings("ignore", category=GQLAlchemySubclassNotFoundWarning)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
cypher_cache_dir = 'cache/cypher_cache'
sql_cache_dir = 'cache/sql_cache'


class GraphQuery:
    port: int
    host: str
    memgraph: Memgraph
    schema: str

    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 7687):
        self.port = port
        self.host = host
        self._memgraph = Memgraph(host=self.host, port=self.port)
        self._schema = ' '.join([str(i) for i in self._memgraph.execute_and_fetch(SCHEMA_QUERY)])
        self._questions = ' '.join(self._get_questions(self._memgraph.execute_and_fetch(QUESTION_QUERY)))

    @staticmethod
    def _get_questions(res: Iterator[Dict[str, Any]]) -> List:
        return [re.search(r"'text': '(.*?)'", str(x)).group(1) for x in res]

    @staticmethod
    def _call_llm(question: str, prompt: str, temperature) -> str:
        messages: list[Union[dict[str, Union[str, Any]], dict[str, Union[str, Any]]]] = [{'role': 'system',
                                                                                          'content': prompt},
                                                                                         {'role': "user",
                                                                                          'content': question}]
        ans = openai.ChatCompletion.create(engine="gpt-4-32k", messages=messages, temperature=temperature)
        return ans['choices'][0].message.content

    @staticmethod
    async def _acall_llm(question: str, prompt: str, temperature: int) -> str:
        messages = [{'role': 'system', 'content': prompt},
                    {'role': "user", 'content': question}]
        ans = await openai.ChatCompletion.acreate(engine="gpt-4-32k",
                                                  messages=messages, temperature=temperature)
        return ans['choices'][0].message.content

    async def _agen_cypher(self, question: str, prompt: str, temperature: int) -> str:
        os.makedirs(cypher_cache_dir, exist_ok=True)

        # Define a unique filename for each query based on the user question
        query_hash = hashlib.md5(question.encode()).hexdigest()
        query_filename = os.path.join(cypher_cache_dir, f"query_{query_hash}.cypher")

        # Check if the query is already cached
        if os.path.exists(query_filename):
            with open(query_filename, 'r') as file:
                cached_query = file.read()
                logger.info('Using cypher cache...')
                return cached_query
        cypher_query = await self._acall_llm(question, prompt, temperature)
        logger.info('No cypher cache found...')
        with open(query_filename, 'w') as file:
            file.write(cypher_query)
        return cypher_query

    def _gen_cypher(self, question: str, prompt: str, temperature: int) -> str:
        os.makedirs(cypher_cache_dir, exist_ok=True)

        # Define a unique filename for each query based on the user question
        query_hash = hashlib.md5(question.encode()).hexdigest()
        query_filename = os.path.join(cypher_cache_dir, f"query_{query_hash}.cypher")

        # Check if the query is already cached
        if os.path.exists(query_filename):
            with open(query_filename, 'r') as file:
                cached_query = file.read()
                logger.info('Using cypher cache...')
                return cached_query
        cypher_query = self._call_llm(question, prompt, temperature)
        logger.info('No cypher cache found...')
        with open(query_filename, 'w') as file:
            file.write(cypher_query)
        return cypher_query

    async def _agen_sql(self, question: str, prompt: str, temperature: int) -> str:
        os.makedirs(sql_cache_dir, exist_ok=True)

        # Define a unique filename for each query based on the user question
        query_hash = hashlib.md5(question.encode()).hexdigest()
        query_filename = os.path.join(sql_cache_dir, f"query_{query_hash}.sql")

        # Check if the query is already cached
        if os.path.exists(query_filename):
            with open(query_filename, 'r') as file:
                cached_query = file.read()
                logger.info('Using sql cache...')
                return cached_query
        sql_query = await self._acall_llm(question, prompt, temperature)
        logger.info('No sql cache found...')
        with open(query_filename, 'w') as file:
            file.write(sql_query)
        return sql_query

    def _gen_sql(self, question: str, prompt: str, temperature: int) -> str:
        os.makedirs(sql_cache_dir, exist_ok=True)

        # Define a unique filename for each query based on the user question
        query_hash = hashlib.md5(question.encode()).hexdigest()
        query_filename = os.path.join(sql_cache_dir, f"query_{query_hash}.sql")

        # Check if the query is already cached
        if os.path.exists(query_filename):
            with open(query_filename, 'r') as file:
                cached_query = file.read()
                logger.info('Using sql cache...')
                return cached_query
        sql_query = self._call_llm(question, prompt, temperature)
        logger.info('No sql cache found...')
        with open(query_filename, 'w') as file:
            file.write(sql_query)
        return sql_query

    async def arun(self, question: str, temperature: int = 0.1) -> str:
        cypher = await self._agen_cypher(question, CYPHER_GENERATION_TEMPLATE.format(self._schema, self._questions),
                                         temperature)
        # print(cypher)
        exec_cypher = [x for x in self._memgraph.execute_and_fetch(cypher)]
        # print(exec_cypher)
        return await self._agen_sql(question, SQL_GENERATION_TEMPLATE.format(exec_cypher), temperature)

    def run(self, question: str, temperature: int = 0.1) -> str:
        cypher = self._gen_cypher(question, CYPHER_GENERATION_TEMPLATE.format(self._schema, self._questions), temperature)
        # print(cypher)
        exec_cypher = [x for x in self._memgraph.execute_and_fetch(cypher)]
        # print(exec_cypher)
        return self._gen_sql(question, SQL_GENERATION_TEMPLATE.format(exec_cypher), temperature)

    @staticmethod
    def clear_cache():
        for root, dirs, files in os.walk('cache', topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)  # Remove the file
            for d in dirs:
                dir_path = os.path.join(root, d)
                os.rmdir(dir_path)  # Remove the directory


class HFGraphQuery(GraphQuery):

    def __init__(self,
                 max_length=2000,
                 repo="microsoft/phi-1_5"):
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(repo, trust_remote_code=True)
        self.generation_params = dict()
        self.generation_params['max_length'] = max_length
        self.generation_params['do_sample'] = True
        self.bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        self.model = AutoModel.from_pretrained(repo, quantization_config=self.bnb_config, trust_remote_code=True).to('cpu')

    @abstractmethod
    def _call_llm(self, question: str, prompt: str, temperature: int) -> str:
        self.generation_params['temperature'] = temperature
        messages = [{'role': 'system', 'content': prompt},
                    {'role': "user", 'content': question}]
        encoded_conversation = self.tokenizer(str(messages), return_tensors="pt").to('mps')
        output_encoded = self.model.generate(**encoded_conversation, max_new_tokens=200)

        ans = self.tokenizer.decode(output_encoded[0], skip_special_tokens=True)
        return ans

    @abstractmethod
    async def _acall_llm(self, question: str, prompt: str, temperature) -> str:
        self.generation_params['temperature'] = temperature
        messages = [{'role': 'system', 'content': prompt},
                    {'role': "user", 'content': question}]
        encoded_conversation = self.tokenizer(str(messages), return_tensors="pt").to('mps')
        output_encoded = self.model.generate(**encoded_conversation, max_new_tokens=200)

        ans = self.tokenizer.decode(output_encoded[0], skip_special_tokens=True)
        return ans
