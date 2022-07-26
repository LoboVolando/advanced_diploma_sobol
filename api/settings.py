from pydantic import BaseSettings


class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 5555
    # db_url = ""
    # async_db_url = ""
    # connect_args = {"check_same_thread": False}
    # jwt_secret: str
    # jwt_algorithm: str = "HS256"
    # jwt_expiration: int = 3600


settings = Settings(_env_file="./.env", _env_file_encoding="UTF-8")
