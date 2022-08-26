from loguru import logger
from pydantic import BaseSettings


class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8000

    postgres_root_user: str = "postgres"
    postgres_root_password: str = "PostgresPassword"
    postgres_host: str = "localhost"
    postgres_port: int = 5002
    web_db: str = "postgres"
    redis_host: str = "localhost"
    redis_port: str = 5479
    media_root: str = "/home/svv/Изображения/diploma"

    # db_url = ""
    # async_db_url = ""
    # connect_args = {"check_same_thread": False}
    # jwt_secret: str
    # jwt_algorithm: str = "HS256"
    # jwt_expiration: int = 3600


settings = Settings(_env_file="./.env", _env_file_encoding="UTF-8")
logger.info(settings.dict())
