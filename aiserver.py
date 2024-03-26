import ai.ddeval
import ai.NatSQL.dd_data_trans
import ai.gpt2.using_gpt2
import datetime
import os
import threading


import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import time

app = FastAPI()


class QueryRequest(BaseModel):
    prompt: str
    preprocessed_data: dict
    original_data: dict

class GPT2Request(BaseModel):
    sql: str
    question: str
    external_knowledge: str = ""

class PreprocessRequest(BaseModel):
    data: dict

@app.post("/post_query")
async def post_query(query: QueryRequest):
    try:
        start = time.time()
        response = await ai.ddeval.get_sql(query.prompt, query.preprocessed_data, query.original_data)
        end = time.time()
    except Exception as e:
        return {"response": e.args, "running_time": -1, "is_success": False}
    return {"response": response, "running_time": end-start, "is_success": True}

@app.post("/gpt2")
async def gpt2(query: GPT2Request):
    try:
        start = time.time()
        response = await ai.gpt2.using_gpt2.get_response(query.sql, query.question, query.external_knowledge)
        end = time.time()
    except IndexError as e:
        return {"response": ("IndexError, too many tokens.",), "running_time": -1, "is_success": False}
    except Exception as e:
        return {"response": e.args, "running_time": -1, "is_success": False}
    return {"response": response, "running_time": end-start, "is_success": True}

@app.post("/preprocess_data")
async def preprocess_data(query: PreprocessRequest):
    response = ai.NatSQL.dd_data_trans.data_trans(query.data)
    return {"response":response}

if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=5000)