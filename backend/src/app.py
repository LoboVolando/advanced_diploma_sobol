from app_tweets import router as app_tweets_router
from app_users import router as app_users_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CLI-ter", description="Импортозамещение in action", version="0.01a")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app_tweets_router)
app.include_router(app_users_router)
# app.mount('/static', StaticFiles(directory=Path(settings.media_root)), name='static')
