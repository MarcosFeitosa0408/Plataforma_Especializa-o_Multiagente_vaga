from collections.abc import Iterable

from core.schemas.candidate import MasterProfile
from core.schemas.job import JobOpportunity
from core.schemas.qualification import (
    QualificationBreakdown,
    QualificationResult,
)


class QualificationAgent:
    """Avalia a compatibilidade entre o perfil do candidato e uma vaga."""

    WEIGHTS = {
        "technical_skills": 0.35,
        "professional_experience": 0.20,
        "responsibilities": 0.15,
        "seniority": 0.10,
        "location_work_model": 0.10,
        "ats_compatibility": 0.10,
    }

    MAIN_QUEUE_THRESHOLD = 7.0
    SECONDARY_QUEUE_THRESHOLD = 6.5

    def calculate_fit(
        self,
        job: JobOpportunity,
        profile: MasterProfile,
    ) -> QualificationResult:
        """Calcula o fit geral da vaga e produz uma justificativa auditável."""

        candidate_skills = self._candidate_skills(profile)
        job_requirements = self._normalized_values(
            job.requirements
        )

        matched = sorted(
            candidate_skills & job_requirements
        )
        missing = sorted(
            job_requirements - candidate_skills
        )

        technical_score = self._score_technical_skills(
            matched=matched,
            requirements=job_requirements,
        )

        experience_score = self._score_experience(
            job,
            profile,
        )

        responsibilities_score = self._score_responsibilities(
            job,
            profile,
        )

        seniority_score = self._score_seniority(
            job,
            profile,
        )

        location_score = self._score_location(
            job,
            profile,
        )

        ats_score = self._score_ats_compatibility(
            job,
            profile,
            matched,
        )

        eliminatory_gaps = self._identify_eliminatory_gaps(
            job,
            profile,
        )

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

        fit_score = self._calculate_weighted_score(
            breakdown
        )

        recommendation = self._recommend(
            fit_score,
            eliminatory_gaps,
        )

        reasoning = self._build_reasoning(
            fit_score=fit_score,
            matched=matched,
            missing=missing,
            eliminatory_gaps=eliminatory_gaps,
            breakdown=breakdown,
        )

        return QualificationResult(
            job_id=job.job_id,
            fit_score=fit_score,
            recommendation=recommendation,
            matched_skills=matched,
            missing_skills=missing,
            eliminatory_gaps=eliminatory_gaps,
            breakdown=breakdown,
            reasoning=reasoning,
        )

    def _candidate_skills(
        self,
        profile: MasterProfile,
    ) -> set[str]:
        """Consolida as competências comprovadas do Master Profile."""

        return self._normalized_values(
            profile.skills.core
            + profile.skills.database
            + profile.skills.python
            + profile.skills.analytics
            + profile.skills.tools
            + profile.skills.automation
        )

    def _normalized_values(
        self,
        values: Iterable[str],
    ) -> set[str]:
        """Normaliza textos para comparações consistentes."""

        return {
            value.strip().casefold()
            for value in values
            if value and value.strip()
        }

    def _score_technical_skills(
        self,
        matched: list[str],
        requirements: set[str],
    ) -> float:
        """Calcula aderência aos requisitos técnicos identificados."""

        if not requirements:
            return 5.0

        return (
            len(matched)
            / len(requirements)
        ) * 10

    def _score_experience(
        self,
        job: JobOpportunity,
        profile: MasterProfile,
    ) -> float:
        """Avalia evidências de experiência profissional relacionadas."""

        if not profile.experience:
            return 0.0

        job_text = self._job_text(job)

        experience_terms: set[str] = set()

        for experience in profile.experience:
            experience_terms.update(
                self._normalized_values(
                    experience.technologies
                )
            )
            experience_terms.update(
                self._normalized_values(
                    experience.responsibilities
                )
            )

        if not job_text.strip():
            return 7.0

        matches = sum(
            1
            for term in experience_terms
            if term in job_text
        )

        if matches >= 5:
            return 10.0

        if matches >= 3:
            return 8.5

        if matches >= 1:
            return 7.0

        return 5.0

    def _score_responsibilities(
        self,
        job: JobOpportunity,
        profile: MasterProfile,
    ) -> float:
        """Compara o conteúdo da vaga com responsabilidades comprovadas."""

        job_text = self._job_text(job)

        if not job_text.strip():
            return 5.0

        responsibility_terms: set[str] = set()

        for experience in profile.experience:
            responsibility_terms.update(
                self._normalized_values(
                    experience.responsibilities
                )
            )

        matches = sum(
            1
            for responsibility in responsibility_terms
            if responsibility in job_text
        )

        if matches >= 5:
            return 10.0

        if matches >= 3:
            return 8.0

        if matches >= 1:
            return 6.5

        return 4.0

    def _score_seniority(
        self,
        job: JobOpportunity,
        profile: MasterProfile,
    ) -> float:
        """Avalia se a senioridade da vaga está alinhada ao objetivo."""

        title = job.title.casefold()

        for seniority in profile.candidate.career_target.seniority:
            if seniority.casefold() in title:
                return 10.0

        junior_terms = (
            "júnior",
            "junior",
            "analista i",
            "assistente",
        )

        if any(
            term in title
            for term in junior_terms
        ):
            return 10.0

        senior_terms = (
            "sênior",
            "senior",
            "especialista",
            "lead",
            "líder",
            "principal",
        )

        if any(
            term in title
            for term in senior_terms
        ):
            return 2.0

        mid_terms = (
            "pleno",
            "mid level",
            "mid-level",
        )

        if any(
            term in title
            for term in mid_terms
        ):
            return 5.0

        return 7.0

    def _score_location(
        self,
        job: JobOpportunity,
        profile: MasterProfile,
    ) -> float:
        """Avalia modelo de trabalho e localização."""

        preferences = profile.candidate.work_preferences

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

        normalized_job_location = (
            job.location
            .casefold()
            .replace("/", " ")
            .replace(",", " ")
        )

        for preferred_location in preferences.preferred_location:
            normalized_preference = (
                preferred_location
                .casefold()
                .replace("/", " ")
                .replace(",", " ")
            )

            preference_parts = [
                part
                for part in normalized_preference.split()
                if len(part) > 2
            ]

            if any(
                part in normalized_job_location
                for part in preference_parts
            ):
                return 8.0

        if job.location == "NAO_IDENTIFICADO":
            return 5.0

        return 4.0

    def _score_ats_compatibility(
        self,
        job: JobOpportunity,
        profile: MasterProfile,
        matched: list[str],
    ) -> float:
        """
        Estima a aderência textual entre vaga e evidências do perfil.

        Não representa a probabilidade real de aprovação em um ATS externo.
        """

        job_text = self._job_text(job)
        candidate_skills = self._candidate_skills(
            profile
        )

        if not job_text.strip():
            if not job.requirements:
                return 5.0

            return self._score_technical_skills(
                matched,
                self._normalized_values(
                    job.requirements
                ),
            )

        relevant_skills = [
            skill
            for skill in candidate_skills
            if skill in job_text
        ]

        if not candidate_skills:
            return 0.0

        raw_score = (
            len(relevant_skills)
            / len(candidate_skills)
        ) * 20

        requirement_score = self._score_technical_skills(
            matched,
            self._normalized_values(
                job.requirements
            ),
        )

        combined_score = (
            raw_score * 0.40
            + requirement_score * 0.60
        )

        return min(combined_score, 10.0)

    def _identify_eliminatory_gaps(
        self,
        job: JobOpportunity,
        profile: MasterProfile,
    ) -> list[str]:
        """Identifica incompatibilidades objetivas conhecidas."""

        gaps: list[str] = []
        preferences = profile.candidate.work_preferences

        title = job.title.casefold()

        senior_terms = (
            "sênior",
            "senior",
            "principal",
        )

        if any(
            term in title
            for term in senior_terms
        ):
            gaps.append(
                "Senioridade acima do foco profissional informado."
            )

        if (
            job.work_model.value == "ONSITE"
            and not preferences.onsite
        ):
            gaps.append(
                "Modelo presencial incompatível com a preferência informada."
            )

        return gaps

    def _calculate_weighted_score(
        self,
        breakdown: QualificationBreakdown,
    ) -> float:
        """Aplica os pesos oficiais do Agent 2."""

        score = (
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
            * self.WEIGHTS["ats_compatibility"]
        )

        return round(
            min(
                max(score, 0.0),
                10.0,
            ),
            2,
        )

    def _recommend(
        self,
        fit_score: float,
        eliminatory_gaps: list[str] | None = None,
    ) -> str:
        """Define a fila da vaga considerando fit e lacunas eliminatórias."""

        gaps = eliminatory_gaps or []

        if gaps:
            return "NAO_RECOMENDADA"

        if fit_score >= self.MAIN_QUEUE_THRESHOLD:
            return "RECOMENDADA"

        if fit_score >= self.SECONDARY_QUEUE_THRESHOLD:
            return "FILA_SECUNDARIA"

        return "NAO_RECOMENDADA"

    def _job_text(
        self,
        job: JobOpportunity,
    ) -> str:
        """Consolida os textos disponíveis da vaga para análise."""

        parts = [
            job.title,
            job.description,
            *job.requirements,
            *job.desirable_requirements,
        ]

        return " ".join(
            part.casefold()
            for part in parts
            if part
        )

    def _build_reasoning(
        self,
        fit_score: float,
        matched: list[str],
        missing: list[str],
        eliminatory_gaps: list[str],
        breakdown: QualificationBreakdown,
    ) -> list[str]:
        """Produz explicações rastreáveis para o resultado."""

        reasoning = [
            (
                f"{len(matched)} requisito(s) técnico(s) "
                "compatível(is)."
            ),
            (
                f"{len(missing)} requisito(s) técnico(s) "
                "não identificado(s)."
            ),
            (
                "Competências técnicas: "
                f"{breakdown.technical_skills}/10."
            ),
            (
                "Experiência profissional: "
                f"{breakdown.professional_experience}/10."
            ),
            (
                "Responsabilidades: "
                f"{breakdown.responsibilities}/10."
            ),
            (
                "Senioridade: "
                f"{breakdown.seniority}/10."
            ),
            (
                "Localização/modelo de trabalho: "
                f"{breakdown.location_work_model}/10."
            ),
            (
                "Compatibilidade textual ATS estimada: "
                f"{breakdown.ats_compatibility}/10."
            ),
        ]

        if eliminatory_gaps:
            reasoning.append(
                "Lacuna(s) eliminatória(s): "
                + "; ".join(eliminatory_gaps)
            )

        reasoning.append(
            f"Fit final calculado: {fit_score}/10."
        )

        return reasoning
