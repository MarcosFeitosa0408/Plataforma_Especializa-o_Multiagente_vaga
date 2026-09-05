from pydantic import Field

from core.schemas.job import StrictModel, WorkModel


class JobAnalysisRequest(StrictModel):
    """Dados recebidos pela API para análise de uma vaga."""

    job_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)

    source: str = "API"
    location: str = "NAO_IDENTIFICADO"
    work_model: WorkModel = WorkModel.UNKNOWN
    employment_type: str = "NAO_IDENTIFICADO"

    description: str = ""
    requirements: list[str] = Field(default_factory=list)
    desirable_requirements: list[str] = Field(default_factory=list)


from core.schemas.application import ApplicationPreparation


class ApplicationDecisionRequest(StrictModel):
    """Recebe uma candidatura preparada para decisão humana."""

    application: ApplicationPreparation
