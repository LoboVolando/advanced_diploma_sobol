import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True
    postgres_root_user: str = "postgres"
    postgres_root_password: str = "PostgresPassword"
    postgres_host: str = "localhost"
    postgres_port: int = 5002
    web_db: str = "postgres"
    redis_host: str = "localhost"
    redis_port: str = 5479
    docker_media_root: str = "/home/svv/data/test-diploma/static/media"
    media_url: str = "/static/media"


if os.path.exists("./.env"):
    settings = Settings(_env_file="./.env", _env_file_encoding="UTF-8")
else:
    settings = Settings()
