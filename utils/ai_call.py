import os
import requests
import config
import mylogger
from dialogue import ModelOptions
import streamlit as st
import json

@st.cache_data
def get_raw_and_preprocessed_data(db_choice:str) -> dict:
    try:
        preprocessed_file = os.path.join(config.preprocessed_database_dir, f"{db_choice}.json")
        raw_file = os.path.join(os.path.join(config.database_dir, db_choice), f"{db_choice}.json")
        if os.path.exists(preprocessed_file) and os.path.exists(raw_file):
            with open(preprocessed_file, "r") as f:
                content = f.read()
                preprocessed_database_info = json.loads(content)
            with open(raw_file, "r") as f:
                content = f.read()
                raw_database_info = json.loads(content)
            return raw_database_info, preprocessed_database_info, None
        return None, None, None
    except Exception as e:
        None, None, e

@st.cache_data
def get_create_statement(db_choice):
    '''TODO: load create statement

    Args:
        db_choice (_type_): _description_
    '''
    pass

@mylogger.streamlit_performance_log
def ai_call(model_choice: str, prompt: str, db_choice: str):
    rtn = ""
    request_ok = False
    try:
        if model_choice == ModelOptions.RESDSQL:
            raw_data, preprocessed_data, e = get_raw_and_preprocessed_data(db_choice)

            if raw_data is not None and preprocessed_data is not None:
                response = requests.post("http://127.0.0.1:5000/post_query",  json={"prompt": prompt, "preprocessed_data": preprocessed_data, "original_data": raw_data})
                if response.status_code == 200:
                    response_json = response.json()
                    rtn = response_json["response"]
                    request_ok = response_json["is_success"]
                else:
                    rtn = response.text
            elif e is not None:
                rtn = e
        else:
            if os.path.exists(f"data/sql/{uid}/{db_choice}.sql"):
                with open(f"data/sql/{uid}/{db_choice}.sql", "r") as f:
                    create_statements = f.read()

                response = requests.post("http://127.0.0.1:5000/gpt2",  json={"question": prompt, "sql": create_statements, "external_knowledge": external_knowledge})
                if response.status_code == 200:
                    response_json = response.json()
                    rtn = response_json["response"]
                    request_ok = response_json["is_success"]
                else:
                    rtn = response.text
    except Exception as e:
        rtn = e
        
    return rtn, request_ok

