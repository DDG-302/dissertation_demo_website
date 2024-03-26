import os
import requests
import config
import streamlit as st
import json
from options import ModelOptions


@st.cache_data
def get_database_schema() -> dict:
    with open(config.table_json_file, "r") as f:
        raw_database_info = json.load(f)
    raw_database_info_dict = {}
    for data in raw_database_info:
        raw_database_info_dict[data["db_id"]] = data
    return raw_database_info_dict

@st.cache_data
def get_resdsql_preprocessed_data() -> dict:
    with open(config.resdsql_preprocessed_database_dir, "r") as f:
        preprocessed_data = json.load(f)
    preprocessed_data_dict = {}
    for data in preprocessed_data:
        preprocessed_data_dict[data["db_id"]] = data
    return preprocessed_data_dict

@st.cache_data
def get_create_statement(db_choice):
    '''TODO: load create statement

    Args:
        db_choice (_type_): _description_
    Return:
        result, is_success
    '''
    sql_file_path =os.path.join(os.path.join(config.database_dir, db_choice), f"{db_choice}.sql")
    with open(sql_file_path, "r") as f:
        data = f.read()
    return data


def ai_call(model_choice: str, prompt: str, db_choice: str, external_knowledge: str = None):
    '''_summary_

    Args:
        model_choice (str): ModelOptions.xxx
        prompt (str): user input
        db_choice (str): db_id
        external_knowledge (str, optional): _description_. Defaults to None.

    Returns:
        tuple: (ai response, request_ok), if request_ok is False, ai response will be Exception
    '''
    rtn = ""
    request_ok = False
    ai_running_time = -1
    try:
        if model_choice == ModelOptions.RESDSQL:
            db_schema_dict = get_database_schema()
            preprocessed_data_dict = get_resdsql_preprocessed_data()
            raw_data = db_schema_dict[db_choice]
            preprocessed_data = preprocessed_data_dict[db_choice]
            response = requests.post("http://127.0.0.1:5000/post_query",  json={"prompt": prompt, "preprocessed_data": preprocessed_data, "original_data": raw_data})
            if response.status_code == 200:
                response_json = response.json()
                rtn = response_json["response"]
                request_ok = response_json["is_success"]
                ai_running_time = response_json["running_time"]
            else:
                rtn = (response.text,)
        else:
            create_statements = get_create_statement(db_choice)
            create_statements = create_statements[0:int(len(create_statements)/2)]
            response = requests.post("http://127.0.0.1:5000/gpt2",  json={"question": prompt, "sql": create_statements, "external_knowledge": external_knowledge})
            if response.status_code == 200:
                response_json = response.json()
                rtn = response_json["response"]
                request_ok = response_json["is_success"]
                ai_running_time = response_json["running_time"]
            else:
                rtn = (response.text,)
    except Exception as e:
        rtn = e.args

    return rtn, request_ok, ai_running_time

