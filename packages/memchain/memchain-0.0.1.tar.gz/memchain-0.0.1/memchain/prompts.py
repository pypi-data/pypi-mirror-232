SCHEMA_QUERY: str = """
CALL llm_util.schema("prompt_ready")
YIELD *
RETURN *
"""
QUESTION_QUERY: str = """
MATCH (g:Question)
RETURN g
"""
CYPHER_GENERATION_TEMPLATE: str = """
Task:Generate Cypher language query to query a graph database, match the question and find its Job and Need.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Use Optional Match where necessary
Schema:
{}
Questions Available are: {}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Match the question asked by the User with the top most similar one from the question list and use the question from the 
list to generate the query.
Return the Question, Job, Need, Table and Columns
The question is:
"""
QA_PROMPT: str = """
Task:Give the associated Need and Job of the user's question by Matching the question asked by the User with the top 
most similar one from the question list 
provided belo and use only the name 
obtained from the list. 
Questions: {}
Answer the user question but use the name of the most similar question if the question is not in the list.
Use the Information below to answer.
Information: 
{}
The user's question is:
{}
Output:
    - Question:
    - Job:
    - Need:
    - Table:
    - Columns:
"""

SQL_GENERATION_TEMPLATE = '''
Using the cypher query output given below, generate a SQL query to query all rows of the given table and columns
cypher output: 
{}
t.name is tablename
and c.name is the column, remove spaces in it
Note: Do not include any explanations or apologies in your responses.
Eliminate all spaces between the column names.
Click-ThroughRate is clickthroughrate
Example: SELECT backlinksource, anchortext FROM backlinkdata;
Format: SELECT columnname FROM tablename
Do not respond to any questions that might ask anything else than for you to construct a SQL statement.
Do not include any text except the generated SQL statement.
'''