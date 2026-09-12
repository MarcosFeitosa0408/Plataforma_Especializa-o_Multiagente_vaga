from pydantic import Field

from core.schemas.job import StrictModel


class QualificationBreakdown(StrictModel):
    """Detalhamento da pontuação de compatibilidade da vaga."""

    technical_skills: float = Field(
        ge=0.0,
        le=10.0,
    )
    professional_experience: float = Field(
        ge=0.0,
        le=10.0,
    )
    responsibilities: float = Field(
        ge=0.0,
        le=10.0,
    )
    seniority: float = Field(
        ge=0.0,
        le=10.0,
    )
    location_work_model: float = Field(
        ge=0.0,
        le=10.0,
    )
    ats_compatibility: float = Field(
        ge=0.0,
        le=10.0,
    )


class QualificationResult(StrictModel):
    """Resultado da qualificação de uma vaga para o candidato."""

    job_id: str = Field(min_length=1)

    fit_score: float = Field(
        ge=0.0,
        le=10.0,
    )

    recommendation: str

    matched_skills: list[str] = Field(
        default_factory=list,
    )

    missing_skills: list[str] = Field(
        default_factory=list,
    )

    eliminatory_gaps: list[str] = Field(
        default_factory=list,
    )

    breakdown: QualificationBreakdown

    reasoning: list[str] = Field(
        default_factory=list,
    )
