import streamlit as st
import random
import pandas as pd
import numpy as np
from enum import Enum
import json, os
import sqlite3
import requests
# import utils.file_upload as file_upload
import config
import mylogger
import utils.ai_call as ai_call
from options import *

class MessageType(Enum):
    STR = 0
    TABLE = 1
    ERROR = 2
    CAPTION = 3

# @st.cache_resource
def get_sqlite_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
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
        print("chat bot init")
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
        #     "response": [] # [(message or data, MessageType), (message or data, MessageType), ...]
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

    @mylogger.streamlit_performance_log
    def dialogue_page(self, id:str = "TESTID", uid:str = "TESTUSER"):
        # define external knowledge to pretend undefined error
        external_knowledge = None

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
        ###################################################
        # Display chat messages from history on app rerun #
        ###################################################
        for item in st.session_state[uid][id]:
            with st.chat_message("user"):
                st.markdown(item["prompt"])
            with st.chat_message("assistant"):
                for data, data_type in item["response"]:
                    if(data_type == MessageType.CAPTION):
                        caption_markdown = ""
                        for caption in data:
                            caption_markdown += f"`{caption}` "
                        st.markdown(caption_markdown)
                    elif(data_type == MessageType.STR):
                        st.text(data)
                    elif(data_type == MessageType.TABLE):
                        with st.container(height=400, border=False):
                            st.table(data)
                    elif(data_type == MessageType.ERROR):
                        for err in data:
                            st.warning(err)
        #######################                 
        # React to user input #
        #######################
        is_success = True
        ai_running_time = 0
        db_running_time = 0
        current_caption = ""
        if prompt and db_choice is not None:
            self.create_new_history(id, uid)
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
                
            # Add user message to chat history
            self.input_message(prompt, id, uid)
            do_sql_query_flag = False
            if(input_mode == InputOptions.NATURAL_LANGUAGE):
                current_caption = (input_mode, model_choice)
                response, is_success, ai_running_time = ai_call.ai_call(model_choice, prompt, db_choice, external_knowledge)
                if is_success:
                    do_sql_query_flag = True

                ################################
                # this should be removed later #
                if model_choice == ModelOptions.GPT2:
                    do_sql_query_flag = False
                # this should be removed later #
                ################################

            else:
                current_caption = (input_mode, )
                response = prompt
                do_sql_query_flag = True

            

            
            ########################################################
            # Display assistant response in chat message container #
            ########################################################
            with st.chat_message("assistant"):
                if is_success:
                    self.output_response((current_caption, MessageType.CAPTION), id, uid)
                    caption_markdown = ""
                    for caption in current_caption:
                        caption_markdown += f"`{caption}` "
                    st.markdown(caption_markdown)
                    self.output_response((response, MessageType.STR),id, uid)
                    st.text(response)
                else:
                    self.output_response((response, MessageType.ERROR),id, uid)
                    for err in response:
                        st.warning(err)
                if do_sql_query_flag:
                    def execute_sql():
                        db_running_time = -1
                        try:
                            import time
                            # Database connection
                            start = time.time()
                            conn = get_sqlite_connection(database_name_2_file[db_choice])
                            if conn is None:
                                get_sqlite_connection.clear()
                            else:
                                df = pd.read_sql_query(response, conn)
                                if len(df) > config.dataframe_max_rows:
                                    too_many_rows_msg = f"***Too many rows({len(df)}) to display, reduced to {config.dataframe_max_rows} rows.***"
                                    st.markdown(too_many_rows_msg)
                                    self.output_response((too_many_rows_msg, MessageType.STR), id, uid)
                                    df = df.head(config.dataframe_max_rows)
                                end = time.time()
                                db_running_time = end - start
                                self.output_response((df, MessageType.TABLE), id, uid)
                                with st.container(height=400, border=False):
                                    st.table(df)
                        except Exception as e:
                            self.output_response((e.args, MessageType.ERROR), id, uid)
                            for err in e.args:
                                st.warning(err)
                        finally:
                            if conn is not None:
                                conn.commit()
                                conn.close()
                            return db_running_time
                    db_running_time = execute_sql()        
        elif prompt is not None and db_choice is None:
            self.create_new_history(id, uid)
            self.input_message(prompt, id, uid)
            with st.chat_message("user"):
                st.write(prompt)
            self.output_response((["You must choose the database first"], MessageType.ERROR), id, uid)
            with st.chat_message("assistant"):
                st.warning("You must choose the database first")
        from datetime import datetime
        return mylogger.PerformanceLog(0, model_choice, ai_running_time, db_running_time, exec_datetime=datetime.now()), prompt and db_choice is not None

    def database_detail_page(self, uid: str="TESTUSER"):


        with st.sidebar:
            # user choice database by name
            db_choice = st.selectbox(
                "Choose Database",
                database_name_list,
                index=None
            )

            is_pk_only = st.toggle("PK Only")
            
                
        # read data.json contents
        if db_choice is not None:
            if not is_pk_only:
                svg_path = os.path.join(os.path.join(database_raw_dir, db_choice), f"{db_choice}.svg")
            else:
                svg_path = os.path.join(os.path.join(database_raw_dir, db_choice), f"{db_choice}_pk.svg")
            if os.path.exists(svg_path):
                st.image(svg_path, db_choice)
            else:
                st.write("sorry, the schema diagram is not ready yet...")

            

chatBot = ChatBot()