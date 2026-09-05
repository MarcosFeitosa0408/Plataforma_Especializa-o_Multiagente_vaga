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
