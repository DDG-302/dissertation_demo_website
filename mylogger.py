import logging
import time
import random
from datetime import datetime
from typing import Any
import streamlit as st

st.cache_resource
def get_logger():
    print("new logger!")
    logger = logging.getLogger("streamlit logger")
    logger.setLevel(1)
    file_handler = logging.FileHandler("streamlit.log")
    logger.addHandler(file_handler)
    return logger

logger = get_logger()

class PerformanceLog:
    def __init__(self, streamlit_running_time:float, ai_type: str, ai_running_time:float=0, db_running_time:float=0,exec_datetime:datetime = datetime.now() ) -> None:
        self.exec_datetime = exec_datetime
        self.streamlit_running_time = streamlit_running_time
        self.ai_type = ai_type
        self.ai_running_time = ai_running_time
        self.db_running_time = db_running_time
    
    def get_dict(self):
        return {
            "exec_datetime": self.exec_datetime.strftime("%Y-%b-%d %H:%M:%S"),
            "streamlit_running_time": self.streamlit_running_time,
            "ai_type": self.ai_type,
            "ai_running_time": self.ai_running_time,
            "db_running_time": self.db_running_time
        }

    def __str__(self) -> str:
        import json
        return json.dumps(self.get_dict())

def streamlit_performance_log(func):
    '''the function will add function running time at the end of the original result: (return of func, running time: float)
    '''
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        # print(f"exec time: {end-start}")
        return result, end-start
    return wrapper

if __name__ == "__main__":
    @streamlit_performance_log
    def ddfunc(id):
        sleep_time = 2 * random.random()
        # raise Exception("手动异常")
        time.sleep(sleep_time)
        print(f"{id}")
        return sleep_time
    ddfunc(4)
    logger.info("logger debug test")