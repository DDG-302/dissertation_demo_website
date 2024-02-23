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
template_layout = templateEnv.get_template(TEMPLATE_LAYOUT_FILE)

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("website/text2sql.html", "r", encoding="utf8") as f:
        render_text = template_layout.render({
            "render_body": f.read()
        })
    return render_text

app.mount("/website", StaticFiles(directory="website"), name="web")
if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=5000)