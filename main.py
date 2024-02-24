import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import jinja2
import datetime
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_LAYOUT_FILE = "website/layout.html"
TEMPLATE_INDEX_FILE = "website/index.html"
TEMPLATE_INDEX_BASIC_FILE = "website/text2sql.html"
template_layout = templateEnv.get_template(TEMPLATE_LAYOUT_FILE)
template_index = templateEnv.get_template(TEMPLATE_INDEX_FILE)
template_index_basic = templateEnv.get_template(TEMPLATE_INDEX_BASIC_FILE)

HTMLRESPONSE_index = template_layout.render({
    "render_body": template_index.render({
        "basic": template_index_basic.render()
    })
})

async def set_index():
    pass

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLRESPONSE_index

app.mount("/website", StaticFiles(directory="website"), name="web")
if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=5000)