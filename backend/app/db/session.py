
from fastapi import HTTPException, status
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import settings


def create_database_engine(database_url: str):
    is_mysql = database_url.startswith("mysql")

    connect_args = {}

    if is_mysql:
        connect_args = {
            "connect_timeout": 10,
            "read_timeout": 30,
            "write_timeout": 30,
        }

    database_engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_timeout=30,
        connect_args=connect_args,
        echo=False,
    )

    if is_mysql:

        @event.listens_for(database_engine, "connect")
        def set_mysql_query_timeout(
            dbapi_connection,
            connection_record,
        ):
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute(
                    "SET SESSION MAX_EXECUTION_TIME=5000"
                )
            finally:
                cursor.close()

    return database_engine


# Existing application database connection.
engine = create_database_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# Separate database connection for AI analytics.
ai_engine = None
AIReadOnlySessionLocal = None

if settings.AI_DATABASE_URL:
    ai_engine = create_database_engine(
        settings.AI_DATABASE_URL
    )

    AIReadOnlySessionLocal = sessionmaker(
        bind=ai_engine,
        autoflush=False,
        autocommit=False,
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_ai_db():
    if AIReadOnlySessionLocal is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI read-only database is not configured",
        )

    db = AIReadOnlySessionLocal()

    try:
        yield db
    finally:
        db.close()
