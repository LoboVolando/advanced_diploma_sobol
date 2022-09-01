"""
app.py
======

Главный модуль приложения. разделён на 3 приложения: app_users app_tweets app_media. Точка входа для wsgi http сервера.

Examples
--------
Пример запуска приложения через сервер **gunicorn**::

    $ gunicorn app:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind backend:80

Note
----
    Какое-то примечание

Attributes
----------
app : FastAPI
    Экземпляр приложения FastApi, к которому подключаются middleware и роуты приложений
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app_tweets import router as app_tweets_router
from app_users import router as app_users_router

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
