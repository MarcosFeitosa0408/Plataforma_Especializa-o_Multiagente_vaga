from core.schemas.candidate import MasterProfile
from core.schemas.job import JobOpportunity
from core.schemas.qualification import (
    QualificationBreakdown,
    QualificationResult,
)


class QualificationAgent:
    """Calcula a compatibilidade entre candidato e vaga."""

    WEIGHTS = {
        "technical_skills": 0.35,
        "professional_experience": 0.20,
        "responsibilities": 0.15,
        "seniority": 0.10,
        "location_work_model": 0.10,
        "ats_compatibility": 0.10,
    }

    def calculate_fit(
        self,
        job: JobOpportunity,
        profile: MasterProfile,
    ) -> QualificationResult:
        candidate_skills = {
            self._normalize_text(skill)
            for skill in (
                profile.skills.core
                + profile.skills.database
                + profile.skills.python
                + profile.skills.analytics
                + profile.skills.tools
                + profile.skills.automation
            )
        }

        job_requirements = {
            self._normalize_text(requirement)
            for requirement in job.requirements
        }

        matched = sorted(
            candidate_skills & job_requirements
        )

        missing = sorted(
            job_requirements - candidate_skills
        )

        technical_score = self._score_technical(
            matched=matched,
            requirements=job_requirements,
        )

        experience_score = (
            7.0
            if profile.experience
            else 0.0
        )

        responsibilities_score = (
            self._score_responsibilities(
                job,
                profile,
            )
        )

        seniority_score = self._score_seniority(
            job,
            profile,
        )

        location_score = self._score_location(
            job,
            profile,
        )

        ats_score = technical_score

        eliminatory_gaps: list[str] = []

        breakdown = QualificationBreakdown(
            technical_skills=round(
                technical_score,
                2,
            ),
            professional_experience=round(
                experience_score,
                2,
            ),
            responsibilities=round(
                responsibilities_score,
                2,
            ),
            seniority=round(
                seniority_score,
                2,
            ),
            location_work_model=round(
                location_score,
                2,
            ),
            ats_compatibility=round(
                ats_score,
                2,
            ),
        )

        fit_score = round(
            breakdown.technical_skills
            * self.WEIGHTS["technical_skills"]
            + breakdown.professional_experience
            * self.WEIGHTS["professional_experience"]
            + breakdown.responsibilities
            * self.WEIGHTS["responsibilities"]
            + breakdown.seniority
            * self.WEIGHTS["seniority"]
            + breakdown.location_work_model
            * self.WEIGHTS["location_work_model"]
            + breakdown.ats_compatibility
            * self.WEIGHTS["ats_compatibility"],
            2,
        )

        recommendation = self._recommend(
            fit_score,
            eliminatory_gaps,
        )

        return QualificationResult(
            job_id=job.job_id,
            fit_score=fit_score,
            recommendation=recommendation,
            matched_skills=matched,
            missing_skills=missing,
            eliminatory_gaps=eliminatory_gaps,
            breakdown=breakdown,
            reasoning=[
                (
                    f"{len(matched)} requisito(s) "
                    "técnico(s) compatível(is)."
                ),
                (
                    f"{len(missing)} requisito(s) "
                    "técnico(s) não identificado(s)."
                ),
                f"Fit calculado: {fit_score}/10.",
            ],
        )

    def _normalize_text(
        self,
        value: str,
    ) -> str:
        """Normaliza textos utilizados nas comparações."""

        return " ".join(
            value.strip().casefold().split()
        )

    def _score_technical(
        self,
        matched: list[str],
        requirements: set[str],
    ) -> float:
        """Calcula aderência aos requisitos técnicos."""

        if not requirements:
            return 5.0

        return (
            len(matched)
            / len(requirements)
        ) * 10

    def _score_responsibilities(
        self,
        job: JobOpportunity,
        profile: MasterProfile,
    ) -> float:
        """Compara responsabilidades reais com a descrição da vaga."""

        if not job.description.strip():
            return 5.0

        description = self._normalize_text(
            job.description
        )

        candidate_responsibilities: set[str] = set()

        for experience in profile.experience:
            for responsibility in experience.responsibilities:
                normalized = self._normalize_text(
                    responsibility
                )

                if normalized:
                    candidate_responsibilities.add(
                        normalized
                    )

        if not candidate_responsibilities:
            return 0.0

        matched_responsibilities = [
            responsibility
            for responsibility in candidate_responsibilities
            if responsibility in description
        ]

        if matched_responsibilities:
            return min(
                10.0,
                5.0
                + len(matched_responsibilities),
            )

        return 0.0

    def _score_seniority(
        self,
        job: JobOpportunity,
        profile: MasterProfile,
    ) -> float:
        title = self._normalize_text(
            job.title
        )

        for seniority in (
            profile.candidate.career_target.seniority
        ):
            if (
                self._normalize_text(seniority)
                in title
            ):
                return 10.0

        if (
            "júnior" in title
            or "junior" in title
        ):
            return 10.0

        return 5.0

    def _score_location(
        self,
        job: JobOpportunity,
        profile: MasterProfile,
    ) -> float:
        preferences = (
            profile.candidate.work_preferences
        )

        if (
            job.work_model.value == "REMOTE"
            and preferences.remote
        ):
            return 10.0

        if (
            job.work_model.value == "HYBRID"
            and preferences.hybrid
        ):
            return 10.0

        if (
            job.work_model.value == "ONSITE"
            and preferences.onsite
        ):
            return 10.0

        job_location = self._normalize_text(
            job.location
        )

        if any(
            self._normalize_text(location)
            in job_location
            for location
            in preferences.preferred_location
        ):
            return 8.0

        return 4.0

    def _recommend(
        self,
        fit_score: float,
        eliminatory_gaps: list[str] | None = None,
    ) -> str:
        """Define a recomendação considerando score e lacunas eliminatórias."""

        gaps = eliminatory_gaps or []

        if gaps:
            return "NAO_RECOMENDADA"

        if fit_score >= 7.0:
            return "FILA_PRINCIPAL"

        if fit_score >= 6.5:
            return "FILA_SECUNDARIA"

        return "NAO_RECOMENDADA"
