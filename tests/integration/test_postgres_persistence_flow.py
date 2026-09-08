from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.models import Base
from core.orchestrator.orchestrator import JobOrchestrator
from core.repositories.postgres_job_application_repository import (
    PostgreSQLJobApplicationRepository,
)
from core.schemas.job import JobOpportunity, WorkModel


def test_orchestrator_persists_and_recovers_job_application():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
    )

    Base.metadata.create_all(engine)

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    repository = PostgreSQLJobApplicationRepository(
        session_factory
    )

    orchestrator = JobOrchestrator()
    orchestrator.job_application_repository = repository

    job = JobOpportunity(
        job_id="vaga-persistencia-001",
        title="Analista de Dados Júnior",
        company="Empresa Teste",
        source="TESTE",
        location="São Paulo",
        work_model=WorkModel.HYBRID,
        employment_type="CLT",
        requirements=[
            "Power BI",
            "SQL",
            "Excel",
            "Python",
        ],
    )

    application = orchestrator.create_job_application(
        job=job,
        application_id="app-persistencia-001",
    )

    orchestrator.save_job_application(application)

    recovered_application = (
        orchestrator.job_application_repository.get(
            "app-persistencia-001"
        )
    )

    assert recovered_application is not None
    assert (
        recovered_application.application_id
        == "app-persistencia-001"
    )
    assert recovered_application.job.job_id == "vaga-persistencia-001"
    assert recovered_application.job.title == "Analista de Dados Júnior"
