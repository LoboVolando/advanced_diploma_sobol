from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

credentials = dict(
    user=settings.postgres_root_user,
    password=settings.postgres_root_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    db=settings.web_db,
)

engine = create_async_engine(
    "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}".format(
        **credentials
    ),
    echo=True,
)

Base = declarative_base()
session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
