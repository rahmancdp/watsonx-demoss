import streamlit as st
# from code_editor import code_editor

from pptx import Presentation
from pptx.enum.lang import MSO_LANGUAGE_ID

from docx import Document

from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.extensions.langchain import WatsonxLLM

import tempfile
import pathlib
import re
import json

import sqlite3

import logging
import os
from dotenv import load_dotenv

def executesqlscript(sql):
    try:
        connection.executescript(sql)
        connection.commit()
    except sqlite3.OperationalError:
        print("Oops! This was an operational error. Try again...")

# logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

load_dotenv()

api_key = st.secrets["API_KEY"]
project_id = st.secrets["PROJECT_ID"]

api_key = os.getenv("API_KEY", None)
project_id = os.getenv("PROJECT_ID", None)

creds = {
    "url"    : "https://us-south.ml.cloud.ibm.com",
    "apikey" : api_key
}

params = {
    GenParams.DECODING_METHOD:"greedy",
    GenParams.MAX_NEW_TOKENS:1000,
    GenParams.MIN_NEW_TOKENS:1,
    GenParams.TOP_K:50,
    GenParams.TOP_P:1,
    GenParams.STOP_SEQUENCES:['"}','\n\n'],
}


llmllama = Model("meta-llama/llama-2-70b-chat",creds, params, project_id)

connection = sqlite3.connect("sample.db")

sql_script = open("static/Chinook_Sqlite.sql.txt",'r').read()

context = """
CREATE TABLE [Album]
(
    [AlbumId] INTEGER  NOT NULL,
    [Title] NVARCHAR(160)  NOT NULL,
    [ArtistId] INTEGER  NOT NULL,
    CONSTRAINT [PK_Album] PRIMARY KEY  ([AlbumId]),
    FOREIGN KEY ([ArtistId]) REFERENCES [Artist] ([ArtistId]) 
		ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE TABLE [Artist]
(
    [ArtistId] INTEGER  NOT NULL,
    [Name] NVARCHAR(120),
    CONSTRAINT [PK_Artist] PRIMARY KEY  ([ArtistId])
);

CREATE TABLE [Customer]
(
    [CustomerId] INTEGER  NOT NULL,
    [FirstName] NVARCHAR(40)  NOT NULL,
    [LastName] NVARCHAR(20)  NOT NULL,
    [Company] NVARCHAR(80),
    [Address] NVARCHAR(70),
    [City] NVARCHAR(40),
    [State] NVARCHAR(40),
    [Country] NVARCHAR(40),
    [PostalCode] NVARCHAR(10),
    [Phone] NVARCHAR(24),
    [Fax] NVARCHAR(24),
    [Email] NVARCHAR(60)  NOT NULL,
    [SupportRepId] INTEGER,
    CONSTRAINT [PK_Customer] PRIMARY KEY  ([CustomerId]),
    FOREIGN KEY ([SupportRepId]) REFERENCES [Employee] ([EmployeeId]) 
		ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE TABLE [Employee]
(
    [EmployeeId] INTEGER  NOT NULL,
    [LastName] NVARCHAR(20)  NOT NULL,
    [FirstName] NVARCHAR(20)  NOT NULL,
    [Title] NVARCHAR(30),
    [ReportsTo] INTEGER,
    [BirthDate] DATETIME,
    [HireDate] DATETIME,
    [Address] NVARCHAR(70),
    [City] NVARCHAR(40),
    [State] NVARCHAR(40),
    [Country] NVARCHAR(40),
    [PostalCode] NVARCHAR(10),
    [Phone] NVARCHAR(24),
    [Fax] NVARCHAR(24),
    [Email] NVARCHAR(60),
    CONSTRAINT [PK_Employee] PRIMARY KEY  ([EmployeeId]),
    FOREIGN KEY ([ReportsTo]) REFERENCES [Employee] ([EmployeeId]) 
		ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE TABLE [Genre]
(
    [GenreId] INTEGER  NOT NULL,
    [Name] NVARCHAR(120),
    CONSTRAINT [PK_Genre] PRIMARY KEY  ([GenreId])
);

CREATE TABLE [Invoice]
(
    [InvoiceId] INTEGER  NOT NULL,
    [CustomerId] INTEGER  NOT NULL,
    [InvoiceDate] DATETIME  NOT NULL,
    [BillingAddress] NVARCHAR(70),
    [BillingCity] NVARCHAR(40),
    [BillingState] NVARCHAR(40),
    [BillingCountry] NVARCHAR(40),
    [BillingPostalCode] NVARCHAR(10),
    [Total] NUMERIC(10,2)  NOT NULL,
    CONSTRAINT [PK_Invoice] PRIMARY KEY  ([InvoiceId]),
    FOREIGN KEY ([CustomerId]) REFERENCES [Customer] ([CustomerId]) 
		ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE TABLE [InvoiceLine]
(
    [InvoiceLineId] INTEGER  NOT NULL,
    [InvoiceId] INTEGER  NOT NULL,
    [TrackId] INTEGER  NOT NULL,
    [UnitPrice] NUMERIC(10,2)  NOT NULL,
    [Quantity] INTEGER  NOT NULL,
    CONSTRAINT [PK_InvoiceLine] PRIMARY KEY  ([InvoiceLineId]),
    FOREIGN KEY ([InvoiceId]) REFERENCES [Invoice] ([InvoiceId]) 
		ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY ([TrackId]) REFERENCES [Track] ([TrackId]) 
		ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE TABLE [MediaType]
(
    [MediaTypeId] INTEGER  NOT NULL,
    [Name] NVARCHAR(120),
    CONSTRAINT [PK_MediaType] PRIMARY KEY  ([MediaTypeId])
);

CREATE TABLE [Playlist]
(
    [PlaylistId] INTEGER  NOT NULL,
    [Name] NVARCHAR(120),
    CONSTRAINT [PK_Playlist] PRIMARY KEY  ([PlaylistId])
);

CREATE TABLE [PlaylistTrack]
(
    [PlaylistId] INTEGER  NOT NULL,
    [TrackId] INTEGER  NOT NULL,
    CONSTRAINT [PK_PlaylistTrack] PRIMARY KEY  ([PlaylistId], [TrackId]),
    FOREIGN KEY ([PlaylistId]) REFERENCES [Playlist] ([PlaylistId]) 
		ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY ([TrackId]) REFERENCES [Track] ([TrackId]) 
		ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE TABLE [Track]
(
    [TrackId] INTEGER  NOT NULL,
    [Name] NVARCHAR(200)  NOT NULL,
    [AlbumId] INTEGER,
    [MediaTypeId] INTEGER  NOT NULL,
    [GenreId] INTEGER,
    [Composer] NVARCHAR(220),
    [Milliseconds] INTEGER  NOT NULL,
    [Bytes] INTEGER,
    [UnitPrice] NUMERIC(10,2)  NOT NULL,
    CONSTRAINT [PK_Track] PRIMARY KEY  ([TrackId]),
    FOREIGN KEY ([AlbumId]) REFERENCES [Album] ([AlbumId]) 
		ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY ([GenreId]) REFERENCES [Genre] ([GenreId]) 
		ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY ([MediaTypeId]) REFERENCES [MediaType] ([MediaTypeId]) 
		ON DELETE NO ACTION ON UPDATE NO ACTION
);
"""

# executesqlscript(context)

# context = '''table:
# cs_customers (
#  c_id int
#  c_name varchar
# )
# cs_products (
#  p_id int
#  p_name varchar
#  p_price float
#  p_SKU varchar
# )
# cs_orders (
#  o_id int
#  c_id int
#  p_id int
#  o_date datetime)'''

def buildpromptforquery(query,context):
    return f"""[INST]as database admin of sqlite, please generate SQL for following query in backquoted.
<<SYS>>
notes:
- please follow the scheme.
- please show the SQL only.
- dont show explanation.
- end with double newlines.
scheme:`{context}`
<<SYS>>
query:`{query}`
json:{{
sql:
explaination:
}}
[/INST]
json:"""

def executesql(sql):
    try:
        print(sql)
        cursor = connection.execute(sql)
        connection.commit()
        results = cursor.fetchall()
        return results
    except sqlite3.OperationalError:
        print("Oops! This was an operational error. Try again...")

def querytosql(query,context):
    prompts = [buildpromptforquery(query,context)]
    SQL = ""
    for response in llmllama.generate_text(prompts):
        SQL += response
    return SQL

temp_dir = tempfile.TemporaryDirectory()

# st.set_page_config(layout="wide")
st.header("SQL assistant powered by watsonx")

with st.sidebar:
    st.title("SQL assistant")
    st.write("SQL-to-SQL migration (TODO)")
    st.write("Text-to-SQL generation")
    st.write("SQL-to-Text understanding (TODO)")
    # ip_address = st.text_input("ip address")
    # user_name = st.text_input("user name")
    # password = st.text_input("password")
    # database_name = st.text_input("database name")
    if st.button("populate data"):
        with st.spinner(text="In progress...", cache=False):
            executesqlscript(sql_script)
    st.code(f"table scheme {context}",language="SQL")

with st.chat_message("system"):
    st.write("please input your query")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("your query"):
    with st.chat_message("user"):
        st.markdown(query)

    st.session_state.messages.append({"role": "user", "content": query})
    with st.spinner(text="In progress...", cache=False):
        answer = querytosql(query,context)

    sqlexec = json.loads(answer)['sql']
    explaination = json.loads(answer)['explaination']

    st.session_state.messages.append({"role": "sql assistant", "content": sqlexec}) 
    st.session_state.messages.append({"role": "sql assistant", "content": explaination}) 
    with st.chat_message("sql assistant"):
        st.markdown(f'sql:{sqlexec}')
        st.markdown(f'explaination:{explaination}')

    
    # if st.button("execute"):
    st.write(f"execute: -{sqlexec}-")
    with st.spinner(text="In progress...", cache=False):
        results = executesql(sqlexec)
        st.write('result---')
        st.table(results)