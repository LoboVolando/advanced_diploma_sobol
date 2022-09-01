import typing

from sqlalchemy import create_engine, func, select, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import selectinload, sessionmaker

from app_users.models import Author
from settings import settings

# engine = create_engine(
#     settings.db_url, echo=True, connect_args=settings.connect_args
# )
credentials = dict(
    user=settings.postgres_root_user,
    password=settings.postgres_root_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    db=settings.web_db,
)

engine = create_engine(
    "postgresql://{user}:{password}@{host}:{port}/{db}".format(**credentials),
    echo=False,
)

Base = declarative_base()

SessionLocal = sessionmaker(engine, expire_on_commit=False, autoflush=False, autocommit=False)


if __name__ == "__main__":

    session = SessionLocal()
    result = session.execute(select(Author))
    for row in result.scalars():
        row.follower.append(dict(a="a", b="b"))
        print(row.name, row.id, row.following, row.follower)
        session.add(row)
    session.commit()
    session.flush()
    session.close()
