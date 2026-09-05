from fastapi import FastAPI

from core.orchestrator.orchestrator import JobOrchestrator
from core.schemas.api import JobAnalysisRequest
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
