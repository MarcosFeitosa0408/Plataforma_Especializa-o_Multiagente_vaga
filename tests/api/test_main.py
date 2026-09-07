from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "multiagent-job-platform",
        "version": "0.2.0",
    }


def test_analyze_job():
    payload = {
        "job_id": "teste-api-001",
        "title": "Analista de Dados Júnior",
        "company": "Empresa Teste",
        "source": "API",
        "location": "São Paulo",
        "work_model": "HYBRID",
        "employment_type": "CLT",
        "description": "Vaga para análise de dados e criação de dashboards.",
        "requirements": [
            "Power BI",
            "SQL",
            "Excel",
            "Python",
            "DAX",
        ],
        "desirable_requirements": [],
    }

    response = client.post("/analyze-job", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == "teste-api-001"
    assert data["recommendation"] == "RECOMENDADA"
    assert data["fit_score"] >= 7.0
    assert "power bi" in data["matched_skills"]
    assert "sql" in data["matched_skills"]


def test_personalize_job():
    payload = {
        "job_id": "teste-personalize-001",
        "title": "Analista de Dados Júnior",
        "company": "Empresa Teste",
        "source": "API",
        "location": "São Paulo",
        "work_model": "HYBRID",
        "employment_type": "CLT",
        "description": "Vaga para análise de dados.",
        "requirements": [
            "Power BI",
            "SQL",
            "Python",
            "Excel",
            "DAX",
            "Apache Spark",
        ],
        "desirable_requirements": [],
    }

    response = client.post("/personalize-job", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["qualification"]["job_id"] == "teste-personalize-001"
    assert data["personalization"]["job_id"] == "teste-personalize-001"
    assert data["personalization"]["evidence_verified"] is True

    assert "Power BI" in data["personalization"]["selected_skills"]
    assert "SQL" in data["personalization"]["selected_skills"]

    assert "Apache Spark" not in data["personalization"]["selected_skills"]
    assert "apache spark" in data["personalization"]["unsupported_requirements"]


def test_prepare_application():
    response = client.post(
        "/prepare-application",
        json={
            "job_id": "api-prepare-001",
            "title": "Analista de Dados Júnior",
            "company": "Empresa Teste",
            "source": "API",
            "location": "São Paulo",
            "work_model": "HYBRID",
            "employment_type": "CLT",
            "description": "Vaga para análise de dados.",
            "requirements": [
                "Power BI",
                "SQL",
                "Excel",
                "Python",
                "DAX",
            ],
            "desirable_requirements": [],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["application"]["approved_for_human_review"] is True
    assert data["application"]["decision"] == "PENDING_HUMAN_APPROVAL"
    assert data["application"]["ready_to_apply"] is False


def test_approve_application():
    response = client.post(
        "/approve-application",
        json={
            "application": {
                "job_id": "api-approve-001",
                "approved_for_human_review": True,
                "decision": "PENDING_HUMAN_APPROVAL",
                "ready_to_apply": False,
                "blocking_issues": [],
                "warnings": [],
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"] == "APPROVED_BY_HUMAN"
    assert data["ready_to_apply"] is True


def test_reject_application():
    response = client.post(
        "/reject-application",
        json={
            "application": {
                "job_id": "api-reject-001",
                "approved_for_human_review": True,
                "decision": "PENDING_HUMAN_APPROVAL",
                "ready_to_apply": False,
                "blocking_issues": [],
                "warnings": [],
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"] == "REJECTED_BY_HUMAN"
    assert data["ready_to_apply"] is False


def test_update_tracking_status():
    payload = {
        "tracking": {
            "job_id": "api-tracking-001",
            "current_status": "READY_TO_APPLY",
            "history": [
                {
                    "status": "READY_TO_APPLY",
                    "note": "Acompanhamento da candidatura iniciado.",
                }
            ],
        },
        "new_status": "APPLIED",
        "note": "Candidatura enviada.",
    }

    response = client.post(
        "/update-tracking-status",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == "api-tracking-001"
    assert data["current_status"] == "APPLIED"
    assert len(data["history"]) == 2
    assert data["history"][-1]["status"] == "APPLIED"
    assert data["history"][-1]["note"] == "Candidatura enviada."


def test_create_job_application():
    payload = {
        "application_id": "api-application-001",
        "job": {
            "job_id": "api-job-001",
            "title": "Analista de Dados Júnior",
            "company": "Empresa Teste",
            "source": "API",
            "location": "São Paulo",
            "work_model": "HYBRID",
            "employment_type": "CLT",
            "description": "Vaga para análise de dados.",
            "requirements": [
                "Power BI",
                "SQL",
                "Python",
                "Excel",
            ],
            "desirable_requirements": [],
        },
    }

    response = client.post(
        "/job-applications",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["application_id"] == "api-application-001"
    assert data["job"]["job_id"] == "api-job-001"
    assert data["job"]["title"] == "Analista de Dados Júnior"

    assert data["qualification"] is None
    assert data["personalization"] is None
    assert data["preparation"] is None
    assert data["tracking"] is None

def test_get_job_application():
    create_payload = {
        "application_id": "api-get-001",
        "job": {
            "job_id": "api-get-job-001",
            "title": "Analista de Dados Júnior",
            "company": "Empresa Teste",
            "source": "API",
        },
    }

    create_response = client.post(
        "/job-applications",
        json=create_payload,
    )

    assert create_response.status_code == 200

    response = client.get(
        "/job-applications/api-get-001"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["application_id"] == "api-get-001"
    assert data["job"]["job_id"] == "api-get-job-001"
    assert data["job"]["title"] == "Analista de Dados Júnior"


def test_get_unknown_job_application():
    response = client.get(
        "/job-applications/api-inexistente-001"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"]["message"] == "Candidatura não encontrada."
    assert (
        data["detail"]["application_id"]
        == "api-inexistente-001"
    )


def test_list_job_applications():
    first_payload = {
        "application_id": "api-list-001",
        "job": {
            "job_id": "api-list-job-001",
            "title": "Analista de Dados Júnior",
            "company": "Empresa Teste A",
            "source": "API",
        },
    }

    second_payload = {
        "application_id": "api-list-002",
        "job": {
            "job_id": "api-list-job-002",
            "title": "Analista de BI Júnior",
            "company": "Empresa Teste B",
            "source": "API",
        },
    }

    first_response = client.post(
        "/job-applications",
        json=first_payload,
    )

    second_response = client.post(
        "/job-applications",
        json=second_payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    response = client.get("/job-applications")

    assert response.status_code == 200

    data = response.json()

    application_ids = {
        application["application_id"]
        for application in data
    }

    assert "api-list-001" in application_ids
    assert "api-list-002" in application_ids


def test_qualify_stored_job_application():
    create_payload = {
        "application_id": "api-qualify-001",
        "job": {
            "job_id": "api-qualify-job-001",
            "title": "Analista de Dados Júnior",
            "company": "Empresa Teste",
            "source": "API",
            "location": "São Paulo",
            "work_model": "HYBRID",
            "employment_type": "CLT",
            "description": "Vaga para análise de dados.",
            "requirements": [
                "Power BI",
                "SQL",
                "Python",
                "Excel",
                "DAX",
            ],
            "desirable_requirements": [],
        },
    }

    create_response = client.post(
        "/job-applications",
        json=create_payload,
    )

    assert create_response.status_code == 200

    qualify_response = client.post(
        "/job-applications/api-qualify-001/qualify"
    )

    assert qualify_response.status_code == 200

    qualified_data = qualify_response.json()

    assert qualified_data["application_id"] == "api-qualify-001"
    assert qualified_data["qualification"] is not None
    assert qualified_data["qualification"]["job_id"] == "api-qualify-job-001"
    assert qualified_data["qualification"]["fit_score"] >= 7.0

    get_response = client.get(
        "/job-applications/api-qualify-001"
    )

    assert get_response.status_code == 200

    saved_data = get_response.json()

    assert saved_data["qualification"] is not None
    assert saved_data["qualification"]["job_id"] == "api-qualify-job-001"


