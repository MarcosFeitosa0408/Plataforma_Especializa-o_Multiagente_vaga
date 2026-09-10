from agents.agent_01_discovery.discovery_agent import DiscoveryAgent
from core.schemas.job import JobOpportunity, WorkModel


def test_discovery_agent_removes_duplicate_jobs():
    jobs = [
        JobOpportunity(
            job_id="vaga-001",
            title="Analista de Dados Júnior",
            company="Empresa A",
            source="TESTE",
            work_model=WorkModel.HYBRID,
        ),
        JobOpportunity(
            job_id="vaga-002",
            title="Analista de BI Júnior",
            company="Empresa B",
            source="TESTE",
            work_model=WorkModel.REMOTE,
        ),
        JobOpportunity(
            job_id="vaga-001",
            title="Analista de Dados Júnior",
            company="Empresa A",
            source="DUPLICADO",
            work_model=WorkModel.HYBRID,
        ),
    ]

    agent = DiscoveryAgent()
    result = agent.discover(jobs)

    assert len(result) == 2
    assert result[0].job_id == "vaga-001"
    assert result[1].job_id == "vaga-002"


def test_discovery_agent_keeps_unique_jobs():
    jobs = [
        JobOpportunity(
            job_id="vaga-010",
            title="Analista de Dados",
            company="Empresa X",
            source="TESTE",
        ),
        JobOpportunity(
            job_id="vaga-011",
            title="Analista de BI",
            company="Empresa Y",
            source="TESTE",
        ),
    ]

    agent = DiscoveryAgent()
    result = agent.discover(jobs)

    assert len(result) == 2


def test_discovery_agent_normalizes_raw_job():
    raw_job = {
        "job_id": "vaga-020",
        "title": "Analista de Dados Júnior",
        "company": "Empresa Teste",
        "source": "TESTE",
        "url": "https://example.com/vagas/020",
        "location": "São Paulo/SP",
        "work_model": "HYBRID",
        "employment_type": "CLT",
        "description": "Atuação com análise de dados e indicadores.",
        "requirements": [
            "Power BI",
            "SQL",
            "Excel",
        ],
        "desirable_requirements": [
            "Python",
        ],
    }

    agent = DiscoveryAgent()

    result = agent.normalize_job(raw_job)

    assert isinstance(result, JobOpportunity)
    assert result.job_id == "vaga-020"
    assert result.title == "Analista de Dados Júnior"
    assert result.company == "Empresa Teste"
    assert result.source == "TESTE"
    assert result.location == "São Paulo/SP"
    assert result.work_model == WorkModel.HYBRID
    assert result.employment_type == "CLT"
    assert result.requirements == [
        "Power BI",
        "SQL",
        "Excel",
    ]
    assert result.desirable_requirements == [
        "Python",
    ]


def test_discovery_agent_normalizes_and_deduplicates_raw_jobs():
    raw_jobs = [
        {
            "job_id": "vaga-030",
            "title": "Analista de Dados Júnior",
            "company": "Empresa A",
            "source": "FONTE_A",
            "work_model": "HYBRID",
        },
        {
            "job_id": "vaga-031",
            "title": "Analista de BI Júnior",
            "company": "Empresa B",
            "source": "FONTE_B",
            "work_model": "REMOTE",
        },
        {
            "job_id": "vaga-030",
            "title": "Analista de Dados Júnior",
            "company": "Empresa A",
            "source": "FONTE_DUPLICADA",
            "work_model": "HYBRID",
        },
    ]

    agent = DiscoveryAgent()

    result = agent.discover_raw(raw_jobs)

    assert len(result) == 2
    assert all(
        isinstance(job, JobOpportunity)
        for job in result
    )
    assert result[0].job_id == "vaga-030"
    assert result[1].job_id == "vaga-031"


def test_discovery_agent_removes_cross_source_duplicates():
    jobs = [
        JobOpportunity(
            job_id="linkedin-123",
            title="Analista de Dados Júnior",
            company="Empresa Alpha",
            source="LINKEDIN",
            location="São Paulo/SP",
            work_model=WorkModel.HYBRID,
        ),
        JobOpportunity(
            job_id="gupy-987",
            title="  analista de dados júnior  ",
            company="EMPRESA ALPHA",
            source="GUPY",
            location="são paulo/sp",
            work_model=WorkModel.HYBRID,
        ),
        JobOpportunity(
            job_id="gupy-988",
            title="Analista de BI Júnior",
            company="Empresa Beta",
            source="GUPY",
            location="São Paulo/SP",
            work_model=WorkModel.REMOTE,
        ),
    ]

    agent = DiscoveryAgent()

    result = agent.discover(jobs)

    assert len(result) == 2
    assert result[0].job_id == "linkedin-123"
    assert result[1].job_id == "gupy-988"


def test_discovery_agent_normalizes_job_with_optional_fields_missing():
    raw_job = {
        "job_id": "vaga-040",
        "title": "Analista de Dados",
        "company": "Empresa Teste",
        "source": "FONTE_TESTE",
    }

    agent = DiscoveryAgent()

    result = agent.normalize_job(raw_job)

    assert result.job_id == "vaga-040"
    assert result.title == "Analista de Dados"
    assert result.company == "Empresa Teste"
    assert result.source == "FONTE_TESTE"
    assert result.location == "NAO_IDENTIFICADO"
    assert result.work_model == WorkModel.UNKNOWN
    assert result.employment_type == "NAO_IDENTIFICADO"
    assert result.description == ""
    assert result.requirements == []
    assert result.desirable_requirements == []
