import datetime

import jinja2
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
# from ai import ai_test
from web_model import *

app = FastAPI()
templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_LAYOUT_FILE = "website/layout.html"
TEMPLATE_INDEX_FILE = "website/index.html"
INDEX_BASIC_FILE = "website/text2sql.html"
template_layout = templateEnv.get_template(TEMPLATE_LAYOUT_FILE)
template_index = templateEnv.get_template(TEMPLATE_INDEX_FILE)
with open(INDEX_BASIC_FILE, "r", encoding="utf8") as f: 
    index_basic = f.read()

HTMLRESPONSE_index = template_layout.render({
    "render_body": template_index.render({
        "basic": index_basic
    })
})


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLRESPONSE_index

@app.post("/post_query", response_class=JSONResponse)
async def post_query(query_request: QueryRequest = Body()):
    return {"server": "ok",
            "msg": {
                "query": query_request.query,
                "response": "simple response"
            }}
    result = ai_test.get_ans(query_request.query)
    possible_questions = result[0][0]
    ans = result[1][0]
    response = "YOU MAY WANT TO ASK => \n"
    for pq in possible_questions:
        response += pq + "\n"
    response += "ANS => \n" + ans
    return {"server": "ok",
            "msg": {
                "query": query_request.query,
                "response": response
            }}

@app.get("/get_input_examples", response_class=JSONResponse)
async def get_input_examples(example_idx:int):
    return {
        "examples": ["What was the first publicly-funded post-secondary technical institution in Hong Kong?What was the first publicly-funded post-secondary technical institution in Hong Kong?",
        "What was the first publicly-funded post-secondary technical institution in Hong Kong?What was the first publicly-funded post-secondary technical institution in Hong Kong?",
        "What was the first publicly-funded post-secondary technical institution in Hong Kong?What was the first publicly-funded post-secondary technical institution in Hong Kong?",
        "What was the first publicly-funded post-secondary technical institution in Hong Kong?What was the first publicly-funded post-secondary technical institution in Hong Kong?",
        "What was the first publicly-funded post-secondary technical institution in Hong Kong?What was the first publicly-funded post-secondary technical institution in Hong Kong?"],
        "example_idx": example_idx
    }
    examples = []
    for i in range(5):
        examples.append(ai_test.similar_question_list[example_idx][0])
        example_idx = (example_idx + 1)% len(ai_test.similar_question_list)
    return {
        "examples": examples,
        "example_idx": example_idx
    }

        


app.mount("/website", StaticFiles(directory="website"), name="web")
if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=5000)