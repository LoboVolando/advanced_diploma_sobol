"""
db.py
-----

Модуль содержит экземпляры классов для работы с базами данных.

Attributes
----------
credentials : dict
    Словарь настроек, необходимых для подключения к СУБД Postgresql.
engine: AsyncEngine
    Асинхронный движок для подключения к Postgresql.
Base
    Колдунство для декларативного конструирования моделей SqlAlchemy.
session
    Колдунство для выполнения запросов к СУБД.
redis
    Асинхронное подключение к нереляционной СУБД.
"""
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from settings import settings

credentials = dict(
    user=settings.postgres_root_user,
    password=settings.postgres_root_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    db=settings.web_db,
)

engine = create_async_engine(
    "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}".format(**credentials),
    echo=False,
)

Base = declarative_base()
session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# redis = aioredis.from_url(f"redis://{settings.redis_host}:{settings.redis_port}/1")
