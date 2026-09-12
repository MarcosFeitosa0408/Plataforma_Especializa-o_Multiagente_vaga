from agents.agent_00_memory.memory_agent import MemoryAgent
from agents.agent_02_qualification.qualification_agent import (
    QualificationAgent,
)
from core.schemas.job import JobOpportunity, WorkModel


def test_qualification_agent_calculates_candidate_fit():
    profile = MemoryAgent().load_profile()

    job = JobOpportunity(
        job_id="vaga-fit-001",
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
            "DAX",
            "Azure",
        ],
    )

    result = QualificationAgent().calculate_fit(
        job,
        profile,
    )

    assert result.job_id == "vaga-fit-001"
    assert 0 <= result.fit_score <= 10
    assert result.recommendation == "FILA_PRINCIPAL"

    assert "power bi" in result.matched_skills
    assert "sql" in result.matched_skills
    assert "python" in result.matched_skills
    assert "azure" in result.missing_skills

    assert result.breakdown.seniority == 10.0
    assert (
        result.breakdown.location_work_model
        == 10.0
    )


def test_qualification_agent_rejects_low_fit_job():
    profile = MemoryAgent().load_profile()

    job = JobOpportunity(
        job_id="vaga-fit-002",
        title="Engenheiro DevOps Sênior",
        company="Empresa Teste",
        source="TESTE",
        location="Outra Localidade",
        work_model=WorkModel.ONSITE,
        employment_type="CLT",
        requirements=[
            "Kubernetes",
            "Terraform",
            "AWS",
            "Jenkins",
        ],
    )

    result = QualificationAgent().calculate_fit(
        job,
        profile,
    )

    assert result.fit_score < 6.5
    assert (
        result.recommendation
        == "NAO_RECOMENDADA"
    )
    assert len(result.matched_skills) == 0
    assert len(result.missing_skills) == 4


def test_qualification_weights_total_one():
    agent = QualificationAgent()

    assert round(
        sum(agent.WEIGHTS.values()),
        2,
    ) == 1.0


def test_qualification_agent_recommendation_thresholds():
    agent = QualificationAgent()

    assert agent._recommend(8.5, []) == "FILA_PRINCIPAL"
    assert agent._recommend(7.0, []) == "FILA_PRINCIPAL"
    assert agent._recommend(6.5, []) == "FILA_SECUNDARIA"
    assert agent._recommend(6.9, []) == "FILA_SECUNDARIA"
    agent._recommend(6.5)
    agent._recommend(6.9)
    agent._recommend(6.49)


def test_qualification_agent_uses_secondary_queue_for_medium_fit():
    agent = QualificationAgent()

    assert (
        agent._recommend(6.5)
        == "FILA_SECUNDARIA"
    )

    assert (
        agent._recommend(6.9)
        == "FILA_SECUNDARIA"
    )


def test_qualification_agent_rejects_medium_fit_with_eliminatory_gap():
    agent = QualificationAgent()

    result = agent._recommend(
        6.8,
        ["Requisito eliminatório ausente"],
    )

    assert result == "NAO_RECOMENDADA"


def test_qualification_agent_rejects_high_fit_with_eliminatory_gap():
    agent = QualificationAgent()

    result = agent._recommend(
        8.5,
        ["Requisito eliminatório ausente"],
    )

    assert result == "NAO_RECOMENDADA"


def test_qualification_agent_rejects_score_below_secondary_queue():
    agent = QualificationAgent()

    assert (
        agent._recommend(6.49)
        == "NAO_RECOMENDADA"
    )


def test_qualification_agent_normalizes_skill_text():
    agent = QualificationAgent()

    assert (
        agent._normalize_text(
            "  Power BI  "
        )
        == "power bi"
    )


def test_qualification_agent_gives_neutral_score_without_requirements():
    agent = QualificationAgent()

    result = agent._score_technical(
        matched=[],
        requirements=set(),
    )

    assert result == 5.0


def test_qualification_agent_scores_remote_preference():
    profile = MemoryAgent().load_profile()

    job = JobOpportunity(
        job_id="vaga-fit-remote",
        title="Analista de Dados",
        company="Empresa Teste",
        source="TESTE",
        location="Brasil",
        work_model=WorkModel.REMOTE,
    )

    result = QualificationAgent()._score_location(
        job,
        profile,
    )

    assert result == 10.0


def test_qualification_agent_scores_responsibilities_independently():
    profile = MemoryAgent().load_profile()

    job = JobOpportunity(
        job_id="vaga-fit-responsibilities-001",
        title="Analista de Dados Júnior",
        company="Empresa Teste",
        source="TESTE",
        location="São Paulo",
        work_model=WorkModel.HYBRID,
        employment_type="CLT",
        requirements=[
            "Power BI",
            "SQL",
        ],
        description=(
            "Responsável por análise de dados, "
            "desenvolvimento de dashboards, KPIs "
            "e tratamento de dados."
        ),
    )

    result = QualificationAgent().calculate_fit(
        job,
        profile,
    )

    assert result.breakdown.technical_skills == 10.0
    assert 0 <= result.breakdown.responsibilities <= 10.0
