from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import settings

is_mysql = str(settings.DATABASE_URL).startswith("mysql")

connect_args = {}

if is_mysql:
    connect_args = {
        "connect_timeout": 10,
        "read_timeout": 30,
        "write_timeout": 30,
    }

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,
    connect_args=connect_args,
    echo=False,
)


if is_mysql:

    @event.listens_for(engine, "connect")
    def set_mysql_query_timeout(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("SET SESSION MAX_EXECUTION_TIME=5000")
        finally:
            cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
