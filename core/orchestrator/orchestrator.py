from agents.agent_00_memory.memory_agent import MemoryAgent
from agents.agent_01_discovery.discovery_agent import DiscoveryAgent
from agents.agent_02_qualification.qualification_agent import QualificationAgent
from agents.agent_03_personalization.personalization_agent import PersonalizationAgent
from agents.agent_04_application.application_agent import ApplicationAgent
from agents.agent_05_tracking.tracking_agent import TrackingAgent
from core.schemas.application import ApplicationPreparation
from core.schemas.job import JobOpportunity
from core.schemas.personalization import PersonalizationResult
from core.schemas.qualification import QualificationResult
from core.validation.validation_gate import ValidationGate


class JobOrchestrator:
    """Coordena o pipeline de análise e preparação de candidaturas."""

    def __init__(self) -> None:
        self.memory_agent = MemoryAgent()
        self.discovery_agent = DiscoveryAgent()
        self.qualification_agent = QualificationAgent()
        self.personalization_agent = PersonalizationAgent()
        self.validation_gate = ValidationGate()
        self.application_agent = ApplicationAgent()
        self.tracking_agent = TrackingAgent()

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

    def prepare_application(
        self,
        job: JobOpportunity,
        qualification: QualificationResult,
    ) -> ApplicationPreparation:
        """
        Personaliza, valida e prepara a candidatura.

        Mesmo quando aprovada pela Validation Gate, a candidatura
        permanece aguardando aprovação humana.
        """

        personalization = self.personalize_job(
            job,
            qualification,
        )

        validation = self.validation_gate.validate(
            qualification,
            personalization,
        )

        return self.application_agent.prepare(
            job_id=job.job_id,
            approved_for_human_review=validation[
                "approved_for_human_review"
            ],
            blocking_issues=validation["blocking_issues"],
            warnings=validation["warnings"],
        )

    def approve_application(
        self,
        preparation: ApplicationPreparation,
    ) -> ApplicationPreparation:
        """Registra a aprovação humana da candidatura."""

        return self.application_agent.approve(preparation)

    def reject_application(
        self,
        preparation: ApplicationPreparation,
    ) -> ApplicationPreparation:
        """Registra a rejeição humana da candidatura."""

        return self.application_agent.reject(preparation)
    def start_tracking(
        self,
        preparation: ApplicationPreparation,
    ):
        """Inicia o acompanhamento de uma candidatura pronta."""

        if not preparation.ready_to_apply:
            raise ValueError(
                "A candidatura precisa estar pronta antes do acompanhamento."
            )

        return self.tracking_agent.start_tracking(
            job_id=preparation.job_id,
        )

    def update_tracking_status(
        self,
        tracking,
        new_status,
        note: str = "",
    ):
        """Atualiza o status de uma candidatura em acompanhamento."""

        return self.tracking_agent.update_status(
            tracking,
            new_status,
            note,
        )
