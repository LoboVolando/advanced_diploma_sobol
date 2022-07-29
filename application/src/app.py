from .app_tweets import router as app_tweets_router
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="CLI-ter", description="Импортозамещение in action", version="0.01a"
)
app.mount('/static', StaticFiles(directory='src/static'), name='static')

app.include_router(app_tweets_router)

templates = Jinja2Templates(directory='src/templates')


@app.get('/')
async def main(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})
