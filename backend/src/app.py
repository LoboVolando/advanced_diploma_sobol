from .app_tweets import router as app_tweets_router
from fastapi import FastAPI

app = FastAPI(
    title="CLI-ter", description="Импортозамещение in action", version="0.01a"
)

app.include_router(app_tweets_router)

