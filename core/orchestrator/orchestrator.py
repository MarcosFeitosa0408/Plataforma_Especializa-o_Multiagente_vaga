from agents.agent_00_memory.memory_agent import MemoryAgent
from agents.agent_01_discovery.discovery_agent import DiscoveryAgent
from agents.agent_02_qualification.qualification_agent import QualificationAgent
from agents.agent_03_personalization.personalization_agent import PersonalizationAgent
from core.schemas.job import JobOpportunity
from core.schemas.personalization import PersonalizationResult
from core.schemas.qualification import QualificationResult


class JobOrchestrator:
    """Coordena o pipeline inicial de vagas."""

    def __init__(self) -> None:
        self.memory_agent = MemoryAgent()
        self.discovery_agent = DiscoveryAgent()
        self.qualification_agent = QualificationAgent()
        self.personalization_agent = PersonalizationAgent()

    def run(
        self,
        jobs: list[JobOpportunity],
    ) -> list[QualificationResult]:
        """Executa Memory -> Discovery -> Qualification."""

        profile = self.memory_agent.load_profile()
        discovered_jobs = self.discovery_agent.discover(jobs)

        results = [
            self.qualification_agent.calculate_fit(job, profile)
            for job in discovered_jobs
        ]

        return sorted(
            results,
            key=lambda result: result.fit_score,
            reverse=True,
        )

    def personalize_job(
        self,
        job: JobOpportunity,
        qualification: QualificationResult,
    ) -> PersonalizationResult:
        """Executa a personalização de uma vaga qualificada."""

        profile = self.memory_agent.get_profile()

        return self.personalization_agent.personalize(
            job,
            profile,
            qualification,
        )
