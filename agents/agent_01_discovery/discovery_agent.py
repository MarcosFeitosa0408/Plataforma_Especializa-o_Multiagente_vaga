from collections.abc import Iterable

from core.schemas.job import JobOpportunity


class DiscoveryAgent:
    """Normaliza e consolida vagas descobertas por diferentes fontes."""

    def deduplicate(
        self,
        jobs: Iterable[JobOpportunity],
    ) -> list[JobOpportunity]:
        """Remove vagas duplicadas usando job_id como chave principal."""

        unique_jobs: dict[str, JobOpportunity] = {}

        for job in jobs:
            if job.job_id not in unique_jobs:
                unique_jobs[job.job_id] = job

        return list(unique_jobs.values())

    def discover(
        self,
        jobs: Iterable[JobOpportunity],
    ) -> list[JobOpportunity]:
        """Executa a primeira etapa do pipeline de descoberta."""

        return self.deduplicate(jobs)
