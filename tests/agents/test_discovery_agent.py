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
