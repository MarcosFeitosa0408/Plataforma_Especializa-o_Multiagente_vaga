from agents.agent_00_memory.memory_agent import MemoryAgent
from agents.agent_02_qualification.qualification_agent import QualificationAgent
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

    result = QualificationAgent().calculate_fit(job, profile)

    assert result.job_id == "vaga-fit-001"
    assert 0 <= result.fit_score <= 10
    assert result.recommendation == "RECOMENDADA"

    assert "power bi" in result.matched_skills
    assert "sql" in result.matched_skills
    assert "python" in result.matched_skills
    assert "azure" in result.missing_skills

    assert result.breakdown.seniority == 10.0
    assert result.breakdown.location_work_model == 10.0


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

    result = QualificationAgent().calculate_fit(job, profile)

    assert result.fit_score < 6.5
    assert result.recommendation == "NAO_RECOMENDADA"
    assert len(result.matched_skills) == 0
    assert len(result.missing_skills) == 4


def test_qualification_agent_scores_responsibilities_independently():
    profile = MemoryAgent().load_profile()

    job = JobOpportunity(
        job_id="vaga-fit-003",
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
            "desenvolvimento de dashboards, "
            "acompanhamento de KPIs e ETL."
        ),
    )

    result = QualificationAgent().calculate_fit(
        job,
        profile,
    )

    assert result.breakdown.technical_skills == 10.0
    assert result.breakdown.responsibilities == 10.0
    assert result.fit_score >= 7.0
    assert result.recommendation == "RECOMENDADA"
    
    
def test_qualification_agent_detects_senior_role_as_gap():
    profile = MemoryAgent().load_profile()

    job = JobOpportunity(
        job_id="vaga-fit-004",
        title="Analista de Dados Sênior",
        company="Empresa Teste",
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
    )

    result = QualificationAgent().calculate_fit(
        job,
        profile,
    )

    assert result.breakdown.technical_skills == 10.0
    assert result.breakdown.seniority < 10.0
    assert "SENIORIDADE_INCOMPATIVEL" in result.eliminatory_gaps
    assert result.recommendation == "NAO_RECOMENDADA"


def test_qualification_agent_uses_secondary_queue_for_medium_fit():
    agent = QualificationAgent()

    assert agent._recommend(
        6.5,
        [],
    ) == "FILA_SECUNDARIA"

    assert agent._recommend(
        6.9,
        [],
    ) == "FILA_SECUNDARIA"


def test_qualification_agent_blocks_secondary_queue_with_eliminatory_gap():
    agent = QualificationAgent()

    assert agent._recommend(
        6.5,
        ["REQUISITO_ELIMINATORIO"],
    ) == "NAO_RECOMENDADA"

    assert agent._recommend(
        6.9,
        ["REQUISITO_ELIMINATORIO"],
    ) == "NAO_RECOMENDADA"


def test_qualification_agent_does_not_recommend_job_with_eliminatory_gap():
    agent = QualificationAgent()

    assert agent._recommend(
        8.0,
        ["Requisito eliminatório não atendido"],
    ) == "NAO_RECOMENDADA"


def test_qualification_agent_responsibilities_do_not_depend_on_technical_skills():
    profile = MemoryAgent().load_profile()

    job = JobOpportunity(
        job_id="vaga-fit-005",
        title="Analista de Dados Júnior",
        company="Empresa Teste",
        source="TESTE",
        location="São Paulo",
        work_model=WorkModel.HYBRID,
        employment_type="CLT",
        requirements=[
            "Azure",
            "Terraform",
        ],
        description=(
            "Responsável por análise de dados, "
            "desenvolvimento de dashboards, "
            "acompanhamento de KPIs e processos de ETL."
        ),
    )

    result = QualificationAgent().calculate_fit(
        job,
        profile,
    )

    assert result.breakdown.technical_skills == 0.0
    assert result.breakdown.responsibilities > 0.0
