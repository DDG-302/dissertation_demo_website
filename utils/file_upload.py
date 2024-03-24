import json
import os
import streamlit as st
import requests
from utils import dd_sqlparser 


def upload_database_json(bytes_data, uid: str, overwrite: bool):
    if bytes_data is not None:
        raw_dir = f"data/nasdsql/database_raw/{uid}"
        preprocessed_dir = f"data/nasdsql/database_preprocess/{uid}"
        bytes_data = bytes.decode(bytes_data)

        # 1. get database name
        json_data = json.loads(bytes_data)
        database_name = json_data["db_id"]

        progress_bar = st.progress(0, f"`{database_name}` Upload Progress")

        raw_file = f"data/nasdsql/database_raw/{uid}/{database_name}.json"
        preprocessed_file = f"data/nasdsql/database_preprocess/{uid}/{database_name}.json"

        progress_bar.progress(10, f"`{database_name}` Upload Progress")
        # 2.1. create dir
        if not os.path.exists(raw_dir):
            os.mkdir(raw_dir)
        
        

        progress_bar.progress(20, f"`{database_name}` Upload Progress")

        # 2.2. create dir
        if not os.path.exists(preprocessed_dir):
            os.mkdir(preprocessed_dir)
        progress_bar.progress(50, f"`{database_name}` Preprocessing...")
        if not os.path.exists(preprocessed_file) or overwrite:
            try:
                # 3. request AI to generate preprocessed data
                response = requests.post("http://127.0.0.1:5000/preprocess_data",  json={"data": json_data})
                if response.status_code == 200:
                
                    response = response.json()["response"]
                    progress_bar.progress(80, f"Store `{database_name}`...")
                    with open(preprocessed_file, "w") as f:
                        json.dump(response, f)
                else:
                    progress_bar.progress(0, f"`{database_name}` Preprocessing Failure")
                    st.error(response.text)
                    exit()
            except Exception as e:
                if os.path.exists(preprocessed_file):
                    os.remove(preprocessed_file)
                progress_bar.progress(0, f"`{database_name}` Preprocessing Failure(Server Error)")
                for err in e.args:
                    st.error(err)
                return
        else:
            st.info(f"Database `{database_name}` Preprocessed Information already exists")
        # store raw json file
        if not os.path.exists(raw_file) or overwrite:
            with open(raw_file, "w") as f:
                json.dump(json_data, f)
        else:
            st.info(f"Information of database `{database_name}` already exists")
        progress_bar.progress(100, "Done")


def upload_database_CREATE_sql(bytes_data: bytes, file_name: str, uid: str, overwrite: bool):
    if file_name is None:
        st.error("file_name should not be None")
    if bytes_data is not None:
        try:
            store_dir = f"data/sql/{uid}"
            file_path = f"data/sql/{uid}/{file_name}.json"
            sql_file_path = f"data/sql/{uid}/{file_name}.sql"
            json_schema = dd_sqlparser.get_db_schema(bytes_data.decode(), file_name)
            sql_schema = dd_sqlparser.remove_non_create(bytes_data.decode())
            if not os.path.exists(store_dir):
                os.mkdir(store_dir)
            if not os.path.exists(file_path) or overwrite:
                with open(sql_file_path, "w") as f:
                    for sql in sql_schema:
                        f.write(sql)
                st.success(f"File `{file_name}.sql` saved successfully")
            else:
                st.info(f"File `{file_name}.sql` already exists")

            if not os.path.exists(file_path) or overwrite:
                with open(file_path, "w") as f:
                    json.dump(json_schema, f)
                st.success(f"File `{file_name}.json` saved successfully")
            else:
                st.info(f"File `{file_name}.json` already exists")
            
        except Exception as e:
            for err in e.args:
                st.error(err)
    