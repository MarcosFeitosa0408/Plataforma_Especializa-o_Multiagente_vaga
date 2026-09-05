from core.schemas.job import JobStatus
from core.schemas.tracking import ApplicationTracking, TrackingEvent


class TrackingAgent:
    """Registra e acompanha a evolução de uma candidatura."""

    def start_tracking(
        self,
        job_id: str,
        initial_status: JobStatus = JobStatus.READY_TO_APPLY,
    ) -> ApplicationTracking:
        event = TrackingEvent(
            status=initial_status,
            note="Acompanhamento da candidatura iniciado.",
        )

        return ApplicationTracking(
            job_id=job_id,
            current_status=initial_status,
            history=[event],
        )

    def update_status(
        self,
        tracking: ApplicationTracking,
        new_status: JobStatus,
        note: str = "",
    ) -> ApplicationTracking:
        event = TrackingEvent(
            status=new_status,
            note=note,
        )

        return tracking.model_copy(
            update={
                "current_status": new_status,
                "history": tracking.history + [event],
            }
        )
