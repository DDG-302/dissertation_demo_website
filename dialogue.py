import streamlit as st
import random
import pandas as pd
import numpy as np
from enum import Enum
import json, os
import sqlite3
import requests
import utils.file_upload as file_upload
import config

class MessageType(Enum):
    STR = 0
    TABLE = 1
    ERROR = 2

class InputOptions:
    NATURAL_LANGUAGE = "Natural Language"
    SQL = "SQL"

class DatabaseSchemaOptions:
    JSONLIKE = "json like"
    SQL = "CREATE statement"

class ModelOptions:
    RESDSQL = "RESDSQL"
    GPT2 = "GPT-2"

@st.cache_resource
def get_sqlite_connection(db_file):
    conn = None
    print(db_file)
    print(os.path.exists(db_file))
    try:
        conn = sqlite3.connect(db_file)
        print(conn)
    except Exception as e:
        for err in e.args:
            st.warning(err)
    finally:
        return conn


# user input
input_options = (InputOptions.NATURAL_LANGUAGE, InputOptions.SQL)

# 
model_options = (ModelOptions.RESDSQL, ModelOptions.GPT2)

db_schema_options = (DatabaseSchemaOptions.JSONLIKE, DatabaseSchemaOptions.SQL)

@st.cache_data
def get_database_list():
    '''get database path

    Args:
        path (str): _description_
        uid (str): _description_

    Returns:
        _type_: _description_
    '''
    database_name_list = []
    database_name_2_file = {}
    database_raw_dir = config.database_dir
    dir_list = os.listdir(database_raw_dir)
    database_name_list = [] # database name list
    for dir in dir_list:
        db_name = os.path.basename(dir).split(".")[0]
        database_name_list.append(db_name)
        database_name_2_file[db_name] = os.path.join(os.path.join(database_raw_dir,dir), f"{dir}.sqlite")
    return database_name_list, database_name_2_file, database_raw_dir

database_name_list, database_name_2_file, database_raw_dir = get_database_list()

class ChatBot:
    def __init__(self) -> None:
        pass

    def init_history_for_user(self, uid: str):
        st.session_state[uid] = {}

    def init_history_for_id(self, id: str, uid: str)->None:
        if(uid not in st.session_state):
            self.init_history_for_user(uid)
        st.session_state[uid][id] = []
        # each element:
        # {
        #     "prompt": "",
        #     "response": []
        # }
    
    def create_new_history(self, id: str, uid: str):
        if uid not in st.session_state:
            self.init_history_for_user(uid)
        if id not in st.session_state[uid]:
            self.init_history_for_id(id, uid)
        st.session_state[uid][id].append({
            "prompt": "",
            "response": []
        })

    def input_message(self, prompt: str, id: str, uid: str) -> None:
        '''save user input(prompt) to the session_state

        Args:
            prompt (str): _description_
            id (str): conversation id
        '''
        if uid not in st.session_state:
            self.init_history_for_user(uid)
        if id not in st.session_state[uid]:
            self.init_history_for_id(id)
        st.session_state[uid][id][-1]["prompt"] = prompt

    
    def output_response(self, response: tuple, id: str, uid: str) -> None:
        '''save server(AI) response to the session_state

        Args:
            response (tuple): (data: Any, data type: MessageType)
            id (str): conversation id
        '''
        if uid not in st.session_state:
            self.init_history_for_user(uid)
        if id not in st.session_state[uid]:
            self.init_history_for_id(id)
        st.session_state[uid][id][-1]["response"].append(response)

    def upload_database_structure(self, bytes_data: bytes, uid: str, choice: DatabaseSchemaOptions, file_name: str=None, overwrite: bool = False):
        '''store bytes to the disk, request for preprocess data

        Args:
            bytes_data (bytes): data
            uid (str): user id, to determine directory
            choice (DatabaseSchemaOptions): _description_
            file_name (str, optional): Only for SQL file. Defaults to None.
        '''
        if bytes_data is not None:
            if choice == DatabaseSchemaOptions.JSONLIKE:
                file_upload.upload_database_json(bytes_data, uid, overwrite)
            elif choice == DatabaseSchemaOptions.SQL:
                file_upload.upload_database_CREATE_sql(bytes_data, file_name, uid, overwrite)

    def dialogue_page(self, id:str = "TESTID", uid:str = "TESTUSER"):
        with st.sidebar:
            input_mode = st.selectbox(
                "Select Options",
                input_options,
                help="`Natural Language` means to input any text and call the AI model\n`SQL` means to input SQL statements and excute them."
            )

            model_choice = st.selectbox(
                "Select Models",
                model_options
            )
            if model_choice == ModelOptions.RESDSQL:
                schema_type_choice = DatabaseSchemaOptions.JSONLIKE
            else:
                schema_type_choice = DatabaseSchemaOptions.SQL
            

            if database_name_list is not None:
                db_choice = st.selectbox(
                    "Choose Database",
                    database_name_list,
                    index=None,
                    help="You can upload your database in `Database Detail` page, and database schema with .json and .sql are stored seperated."
                )
            if input_mode == InputOptions.NATURAL_LANGUAGE and model_choice == ModelOptions.GPT2:
                external_knowledge = st.text_area("Input external knowledge", help="You may input external knowledge here. This will help LLM to understand your requirements or the structure of your database.")
                st.write(external_knowledge)
        if uid not in st.session_state:
            self.init_history_for_user(uid)
        if id not in st.session_state[uid]:
            self.init_history_for_id(id, uid)
        if input_mode == InputOptions.NATURAL_LANGUAGE:                
            prompt = st.chat_input("Input your query")
        else:
            prompt = st.chat_input("Input your SQL")

        # Display chat messages from history on app rerun

        for item in st.session_state[uid][id]:
            with st.chat_message("user"):
                st.markdown(item["prompt"])
            with st.chat_message("assistant"):
                for data, data_type in item["response"]:
                    if(data_type == MessageType.STR):
                        st.markdown(data)
                    elif(data_type == MessageType.TABLE):
                        with st.container(height=400, border=False):
                            st.table(data)
                    elif(data_type == MessageType.ERROR):
                        for err in data:
                            st.warning(err)
            # React to user input
        
        if prompt and db_choice is not None:
            self.create_new_history(id, uid)
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
                
            # Add user message to chat history
            self.input_message(prompt, id, uid)
            do_sql_query_flag = False
            if(input_mode == InputOptions.NATURAL_LANGUAGE):
                if model_choice == ModelOptions.RESDSQL:
                    if os.path.exists(f"data/nasdsql/database_preprocess/{uid}/{db_choice}.json") and os.path.exists(f"data/nasdsql/database_raw/{uid}/{db_choice}.json"):
                        with open(f"data/nasdsql/database_preprocess/{uid}/{db_choice}.json", "r") as f:
                            content = f.read()
                            preprocessed_database_info = json.loads(content)
                        with open(f"data/nasdsql/database_raw/{uid}/{db_choice}.json", "r") as f:
                            content = f.read()
                            original = json.loads(content)
                        response = requests.post("http://127.0.0.1:5000/post_query",  json={"prompt": prompt, "preprocessed_data": preprocessed_database_info, "original_data": original}).json()["response"]
                        do_sql_query_flag = True
                    else:
                        response = "File Not Exists!"
                elif model_choice == ModelOptions.GPT2:
                    if os.path.exists(f"data/sql/{uid}/{db_choice}.sql"):
                        with open(f"data/sql/{uid}/{db_choice}.sql", "r") as f:
                            create_statements = f.read()

                        response = requests.post("http://127.0.0.1:5000/gpt2",  json={"question": prompt, "sql": create_statements, "external_knowledge": external_knowledge}).json()["response"]
                        # do_sql_query_flag = True
                    else:
                        response = "File Not Exists!"
                else:
                    response = "Model Not Found!"
            else:
                response = prompt
                do_sql_query_flag = True
            self.output_response((response, MessageType.STR), id, uid)

            # Database connection

            

            # Display assistant response in chat message container

            with st.chat_message("assistant"):
                st.markdown(response)
                if do_sql_query_flag:
                    try:
                        conn = get_sqlite_connection(database_name_2_file[db_choice])
                        cursor = None
                        if conn is None:
                            get_sqlite_connection.clear()
                        else:
                            cursor = conn.cursor()
                            df = pd.read_sql_query(response, cursor)
                            self.output_response((df, MessageType.TABLE), id, uid)
                            with st.container(height=400, border=False):
                                st.table(df)
                    except Exception as e:
                        self.output_response((e.args, MessageType.ERROR), id, uid)
                        for err in e.args:
                            st.warning(err)
                    finally:
                        pass
                        # if conn is not None:
                            # conn.commit()
                            # conn.close()
                            
        elif prompt is not None and db_choice is None:
            self.create_new_history(id, uid)
            self.input_message(prompt, id, uid)
            with st.chat_message("user"):
                st.write(prompt)
            self.output_response((["You must choose the database first"], MessageType.ERROR), id, uid)
            with st.chat_message("assistant"):
                st.warning("You must choose the database first")

    def database_detail_page(self, uid: str="TESTUSER"):


        with st.sidebar:
            # user choice database by name
            db_choice = st.selectbox(
                "Choose Database",
                database_name_list,
                index=None
            )
            
                
        # read data.json contents
        if db_choice is not None:
            with open(os.path.join(database_raw_dir, f"{db_choice}.json"), "r") as f:
                detail = json.loads(f.read())

            # 3. load required data
            foreign_key_refrences = {}
            foreign_key_refrenced_by = {}
            for fk in detail["foreign_keys"]:
                if(fk[0] not in foreign_key_refrences):
                    foreign_key_refrences[fk[0]] = [fk[1]]
                else:
                    foreign_key_refrences[fk[0]].append(fk[1])
                if(fk[1] not in foreign_key_refrenced_by):
                    foreign_key_refrenced_by[fk[1]] = [fk[0]]
                else:
                    foreign_key_refrenced_by[fk[1]].append(fk[0])


            st.header(detail["db_id"])
            for idx, table_name in enumerate(detail["table_names_original"]):
                st.subheader(table_name)
                table_details = {
                    "Column": [],
                    "Primary Key": [],
                    "Foreign Key": [],
                    "Type": []
                }
                for col_idx, col in enumerate(detail["column_names_original"]):
                    if(col[0] == idx):
                        if(col_idx in foreign_key_refrences):
                            fk_table_idx, fk_col_name = detail["column_names_original"][foreign_key_refrences[col_idx][0]]
                            table_details["Foreign Key"].append(f'{detail["table_names_original"][fk_table_idx]} => {fk_col_name}')
                        else:
                            table_details["Foreign Key"].append("")
                        if(col_idx in detail["primary_keys"]):
                            table_details["Primary Key"].append("yes")
                        else:
                            table_details["Primary Key"].append("")
                        table_details["Column"].append(col[1])
                        table_details["Type"].append(detail["column_types"][col_idx])
                    elif col[0] > idx:
                        break
                df = pd.DataFrame(table_details)
                st.table(df)

chatBot = ChatBot()