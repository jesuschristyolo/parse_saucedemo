from sqlalchemy import create_engine
from database.config import settings
from sqlalchemy.orm import DeclarativeBase, sessionmaker

sync_engine = create_engine(
    url=settings.database_url_psycopg,
    echo=False
)

session_factory = sessionmaker(sync_engine)


class Base(DeclarativeBase):
    pass
