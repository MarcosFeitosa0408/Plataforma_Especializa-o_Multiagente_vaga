import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL")


def create_database_engine():
    """Cria a engine do banco configurado pela variável DATABASE_URL."""

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL não configurada."
        )

    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )


def create_session_factory():
    """Cria a fábrica de sessões do banco de dados."""

    engine = create_database_engine()

    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
