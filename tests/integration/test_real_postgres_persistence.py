import os

import pytest

from core.database import (
    create_database_engine,
    create_session_factory,
)
from core.models import Base
from core.repositories.postgres_job_application_repository import (
    PostgreSQLJobApplicationRepository,
)
from core.schemas.job import JobOpportunity, WorkModel
from core.schemas.job_application import JobApplicationObject


def test_real_postgres_persists_job_application():
    database_url = os.getenv("DATABASE_URL")

    if not database_url or not database_url.startswith(
        "postgresql"
    ):
        pytest.skip(
            "PostgreSQL real não configurado para este ambiente."
        )

    engine = create_database_engine()

    Base.metadata.create_all(engine)

    session_factory = create_session_factory()

    repository = PostgreSQLJobApplicationRepository(
        session_factory
    )

    application = JobApplicationObject(
        application_id="app-real-postgres-001",
        job=JobOpportunity(
            job_id="vaga-real-postgres-001",
            title="Analista de Dados Júnior",
            company="Empresa Teste PostgreSQL",
            source="TESTE",
            location="São Paulo",
            work_model=WorkModel.HYBRID,
            employment_type="CLT",
            requirements=[
                "Power BI",
                "SQL",
                "Python",
                "Excel",
            ],
        ),
    )

    repository.save(application)

    recovered_application = repository.get(
        "app-real-postgres-001"
    )

    assert recovered_application is not None
    assert (
        recovered_application.application_id
        == "app-real-postgres-001"
    )
    assert (
        recovered_application.job.job_id
        == "vaga-real-postgres-001"
    )
    assert (
        recovered_application.job.title
        == "Analista de Dados Júnior"
    )

    repository.delete(
        "app-real-postgres-001"
    )

    engine.dispose()
