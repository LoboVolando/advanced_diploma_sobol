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
    docker_media_root: str = "/home/svv/projects/data/diploma/static/media"
    media_url: str = "/static/media"

    # db_url = ""
    # async_db_url = ""
    # connect_args = {"check_same_thread": False}
    # jwt_secret: str
    # jwt_algorithm: str = "HS256"
    # jwt_expiration: int = 3600


if os.path.exists("./.env"):
    settings = Settings(_env_file="./.env", _env_file_encoding="UTF-8")
    print(settings.postgres_port)
else:
    settings = Settings()
    print("create")
