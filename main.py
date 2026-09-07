from fastapi import FastAPI, HTTPException
from datetime import datetime
from core.orchestrator.orchestrator import JobOrchestrator
from core.schemas.api import (
    ApplicationDecisionRequest,
    JobAnalysisRequest,
    JobApplicationCreateRequest,
    StoredTrackingStatusUpdateRequest,
    TrackingStatusUpdateRequest,
)
from core.schemas.job import JobOpportunity


app = FastAPI(
    title="Plataforma Especialização Multiagente Vaga",
    version="0.2.0",
)

orchestrator = JobOrchestrator()


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "multiagent-job-platform",
        "version": "0.2.0",
    }


@app.post("/analyze-job")
def analyze_job(request: JobAnalysisRequest):
    job = JobOpportunity(
        job_id=request.job_id,
        title=request.title,
        company=request.company,
        source=request.source,
        location=request.location,
        work_model=request.work_model,
        employment_type=request.employment_type,
        description=request.description,
        requirements=request.requirements,
        desirable_requirements=request.desirable_requirements,
    )

    result = orchestrator.run([job])[0]

    return result


@app.post("/personalize-job")
def personalize_job(request: JobAnalysisRequest):
    job = JobOpportunity(
        job_id=request.job_id,
        title=request.title,
        company=request.company,
        source=request.source,
        location=request.location,
        work_model=request.work_model,
        employment_type=request.employment_type,
        description=request.description,
        requirements=request.requirements,
        desirable_requirements=request.desirable_requirements,
    )

    qualification = orchestrator.run([job])[0]

    personalization = orchestrator.personalize_job(
        job,
        qualification,
    )

    return {
        "qualification": qualification,
        "personalization": personalization,
    }


@app.post("/prepare-application")
def prepare_application(request: JobAnalysisRequest):
    job = JobOpportunity(
        job_id=request.job_id,
        title=request.title,
        company=request.company,
        source=request.source,
        location=request.location,
        work_model=request.work_model,
        employment_type=request.employment_type,
        description=request.description,
        requirements=request.requirements,
        desirable_requirements=request.desirable_requirements,
    )

    qualification = orchestrator.run([job])[0]

    preparation = orchestrator.prepare_application(
        job,
        qualification,
    )

    return {
        "qualification": qualification,
        "application": preparation,
    }
@app.post("/approve-application")
def approve_application(request: ApplicationDecisionRequest):
    approved = orchestrator.approve_application(
        request.application
    )

    return approved


@app.post("/reject-application")
def reject_application(request: ApplicationDecisionRequest):
    rejected = orchestrator.reject_application(
        request.application
    )

    return rejected


@app.post("/update-tracking-status")
def update_tracking_status(request: TrackingStatusUpdateRequest):
    updated = orchestrator.update_tracking_status(
        request.tracking,
        request.new_status,
        request.note,
    )

    return updated


@app.post("/job-applications")
def create_job_application(
    request: JobApplicationCreateRequest,
):
    application = orchestrator.create_job_application(
        job=request.job,
        application_id=request.application_id,
    )

    saved_application = orchestrator.save_job_application(
        application
    )

    return saved_application


@app.get("/job-applications")
def list_job_applications():
    return orchestrator.list_job_applications()


@app.get("/job-applications/{application_id}")
def get_job_application(application_id: str):
    application = orchestrator.get_job_application(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Candidatura não encontrada.",
                "application_id": application_id,
            },
        )

    return application


@app.post("/job-applications/{application_id}/qualify")
def qualify_job_application(application_id: str):
    application = orchestrator.get_job_application(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Candidatura não encontrada.",
                "application_id": application_id,
            },
        )

    qualified_application = (
        orchestrator.qualify_job_application(
            application
        )
    )

    saved_application = orchestrator.save_job_application(
        qualified_application
    )

    return saved_application


@app.post("/job-applications/{application_id}/personalize")
def personalize_job_application(application_id: str):
    application = orchestrator.get_job_application(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Candidatura não encontrada.",
                "application_id": application_id,
            },
        )

    personalized_application = (
        orchestrator.personalize_job_application(
            application
        )
    )

    saved_application = orchestrator.save_job_application(
        personalized_application
    )

    return saved_application


@app.post("/job-applications/{application_id}/prepare")
def prepare_job_application(application_id: str):
    application = orchestrator.get_job_application(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Candidatura não encontrada.",
                "application_id": application_id,
            },
        )

    prepared_application = (
        orchestrator.prepare_job_application(
            application
        )
    )

    saved_application = orchestrator.save_job_application(
        prepared_application
    )

    return saved_application


@app.post("/job-applications/{application_id}/approve")
def approve_stored_job_application(application_id: str):
    application = orchestrator.get_job_application(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Candidatura não encontrada.",
                "application_id": application_id,
            },
        )

    approved_application = (
        orchestrator.approve_job_application(
            application
        )
    )

    saved_application = orchestrator.save_job_application(
        approved_application
    )

    return saved_application


@app.post("/job-applications/{application_id}/reject")
def reject_stored_job_application(application_id: str):
    application = orchestrator.get_job_application(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Candidatura não encontrada.",
                "application_id": application_id,
            },
        )

    rejected_application = (
        orchestrator.reject_job_application(
            application
        )
    )

    saved_application = orchestrator.save_job_application(
        rejected_application
    )

    return saved_application


@app.post("/job-applications/{application_id}/tracking/start")
def start_stored_job_application_tracking(application_id: str):
    application = orchestrator.get_job_application(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Candidatura não encontrada.",
                "application_id": application_id,
            },
        )

    tracked_application = (
        orchestrator.start_job_application_tracking(
            application
        )
    )

    saved_application = orchestrator.save_job_application(
        tracked_application
    )

    return saved_application


@app.post("/job-applications/{application_id}/tracking/status")
def update_stored_job_application_status(
    application_id: str,
    request: StoredTrackingStatusUpdateRequest,
):
    application = orchestrator.get_job_application(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Candidatura não encontrada.",
                "application_id": application_id,
            },
        )

    updated_application = (
        orchestrator.update_job_application_status(
            application,
            request.new_status,
            request.note,
        )
    )

    saved_application = orchestrator.save_job_application(
        updated_application
    )

    return saved_application


@app.post("/job-applications/{application_id}/follow-up/check")
def check_stored_job_application_follow_up(
    application_id: str,
    followup_count: int,
    last_contact_at: datetime,
):
    application = orchestrator.get_job_application(
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Candidatura não encontrada.",
                "application_id": application_id,
            },
        )

    should_follow_up = (
        orchestrator.should_follow_up_job_application(
            application=application,
            followup_count=followup_count,
            last_contact_at=last_contact_at,
        )
    )

    return {
        "application_id": application_id,
        "should_follow_up": should_follow_up,
    }

