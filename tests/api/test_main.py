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


def test_personalize_stored_job_application():
    create_payload = {
        "application_id": "api-personalize-001",
        "job": {
            "job_id": "api-personalize-job-001",
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
        },
    }

    create_response = client.post(
        "/job-applications",
        json=create_payload,
    )

    assert create_response.status_code == 200

    qualify_response = client.post(
        "/job-applications/api-personalize-001/qualify"
    )

    assert qualify_response.status_code == 200

    personalize_response = client.post(
        "/job-applications/api-personalize-001/personalize"
    )

    assert personalize_response.status_code == 200

    personalized_data = personalize_response.json()

    assert personalized_data["application_id"] == "api-personalize-001"
    assert personalized_data["qualification"] is not None
    assert personalized_data["personalization"] is not None

    assert (
        personalized_data["personalization"]["job_id"]
        == "api-personalize-job-001"
    )

    assert (
        personalized_data["personalization"]["evidence_verified"]
        is True
    )

    assert (
        "Power BI"
        in personalized_data["personalization"]["selected_skills"]
    )

    assert (
        "Apache Spark"
        not in personalized_data["personalization"]["selected_skills"]
    )

    get_response = client.get(
        "/job-applications/api-personalize-001"
    )

    assert get_response.status_code == 200

    saved_data = get_response.json()

    assert saved_data["personalization"] is not None
    assert (
        saved_data["personalization"]["job_id"]
        == "api-personalize-job-001"
    )


def test_prepare_stored_job_application():
    create_payload = {
        "application_id": "api-prepare-stored-001",
        "job": {
            "job_id": "api-prepare-stored-job-001",
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
        "/job-applications/api-prepare-stored-001/qualify"
    )

    assert qualify_response.status_code == 200

    personalize_response = client.post(
        "/job-applications/api-prepare-stored-001/personalize"
    )

    assert personalize_response.status_code == 200

    prepare_response = client.post(
        "/job-applications/api-prepare-stored-001/prepare"
    )

    assert prepare_response.status_code == 200

    prepared_data = prepare_response.json()

    assert prepared_data["application_id"] == "api-prepare-stored-001"
    assert prepared_data["qualification"] is not None
    assert prepared_data["personalization"] is not None
    assert prepared_data["preparation"] is not None

    assert (
        prepared_data["preparation"]["decision"]
        == "PENDING_HUMAN_APPROVAL"
    )

    assert (
        prepared_data["preparation"]["ready_to_apply"]
        is False
    )

    get_response = client.get(
        "/job-applications/api-prepare-stored-001"
    )

    assert get_response.status_code == 200

    saved_data = get_response.json()

    assert saved_data["preparation"] is not None
    assert (
        saved_data["preparation"]["decision"]
        == "PENDING_HUMAN_APPROVAL"
    )


def test_approve_stored_job_application():
    create_payload = {
        "application_id": "api-approve-stored-001",
        "job": {
            "job_id": "api-approve-stored-job-001",
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
        "/job-applications/api-approve-stored-001/qualify"
    )
    assert qualify_response.status_code == 200

    personalize_response = client.post(
        "/job-applications/api-approve-stored-001/personalize"
    )
    assert personalize_response.status_code == 200

    prepare_response = client.post(
        "/job-applications/api-approve-stored-001/prepare"
    )
    assert prepare_response.status_code == 200

    approve_response = client.post(
        "/job-applications/api-approve-stored-001/approve"
    )

    assert approve_response.status_code == 200

    approved_data = approve_response.json()

    assert (
        approved_data["preparation"]["decision"]
        == "APPROVED_BY_HUMAN"
    )
    assert approved_data["preparation"]["ready_to_apply"] is True

    get_response = client.get(
        "/job-applications/api-approve-stored-001"
    )

    assert get_response.status_code == 200

    saved_data = get_response.json()

    assert (
        saved_data["preparation"]["decision"]
        == "APPROVED_BY_HUMAN"
    )
    assert saved_data["preparation"]["ready_to_apply"] is True


def test_reject_stored_job_application():
    create_payload = {
        "application_id": "api-reject-stored-001",
        "job": {
            "job_id": "api-reject-stored-job-001",
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
        "/job-applications/api-reject-stored-001/qualify"
    )
    assert qualify_response.status_code == 200

    personalize_response = client.post(
        "/job-applications/api-reject-stored-001/personalize"
    )
    assert personalize_response.status_code == 200

    prepare_response = client.post(
        "/job-applications/api-reject-stored-001/prepare"
    )
    assert prepare_response.status_code == 200

    reject_response = client.post(
        "/job-applications/api-reject-stored-001/reject"
    )

    assert reject_response.status_code == 200

    rejected_data = reject_response.json()

    assert (
        rejected_data["preparation"]["decision"]
        == "REJECTED_BY_HUMAN"
    )
    assert rejected_data["preparation"]["ready_to_apply"] is False

    get_response = client.get(
        "/job-applications/api-reject-stored-001"
    )

    assert get_response.status_code == 200

    saved_data = get_response.json()

    assert (
        saved_data["preparation"]["decision"]
        == "REJECTED_BY_HUMAN"
    )
    assert saved_data["preparation"]["ready_to_apply"] is False


def test_start_tracking_stored_job_application():
    application_payload = {
    "application_id": "api-tracking-start-001",
    "job": {
        "job_id": "job-tracking-start-001",
        "title": "Analista de Dados Júnior",
        "company": "Empresa Teste",
        "source": "Teste API",
        "location": "São Paulo",
        "work_model": "HYBRID",
        "employment_type": "CLT",
        "description": "Vaga de teste para início de tracking.",
        "requirements": [
            "Power BI",
            "SQL",
            "Python",
            "Excel",
        ],
        "desirable_requirements": [],
    },
}

    create_response = client.post(
        "/job-applications",
        json=application_payload,
    )
    assert create_response.status_code == 200

    qualify_response = client.post(
        "/job-applications/api-tracking-start-001/qualify"
    )
    assert qualify_response.status_code == 200

    personalize_response = client.post(
        "/job-applications/api-tracking-start-001/personalize"
    )
    assert personalize_response.status_code == 200

    prepare_response = client.post(
        "/job-applications/api-tracking-start-001/prepare"
    )
    assert prepare_response.status_code == 200

    approve_response = client.post(
        "/job-applications/api-tracking-start-001/approve"
    )
    assert approve_response.status_code == 200
    assert (
        approve_response.json()["preparation"]["ready_to_apply"]
        is True
    )

    tracking_response = client.post(
        "/job-applications/api-tracking-start-001/tracking/start"
    )

    assert tracking_response.status_code == 200

    tracking_data = tracking_response.json()

    assert tracking_data["tracking"] is not None
    assert (
        tracking_data["tracking"]["job_id"]
        == "job-tracking-start-001"
    )

    stored_response = client.get(
        "/job-applications/api-tracking-start-001"
    )

    assert stored_response.status_code == 200

    stored_data = stored_response.json()

    assert stored_data["tracking"] is not None
    assert (
        stored_data["tracking"]["job_id"]
        == "job-tracking-start-001"
    )


def test_update_tracking_status_stored_job_application():
    application_payload = {
        "application_id": "api-tracking-status-001",
        "job": {
            "job_id": "job-tracking-status-001",
            "title": "Analista de Dados Júnior",
            "company": "Empresa Teste",
            "source": "Teste API",
            "location": "São Paulo",
            "work_model": "HYBRID",
            "employment_type": "CLT",
            "description": "Vaga de teste para atualização de tracking.",
            "requirements": [
                "Power BI",
                "SQL",
                "Python",
                "Excel",
            ],
            "desirable_requirements": [],
        },
    }

    create_response = client.post(
        "/job-applications",
        json=application_payload,
    )
    assert create_response.status_code == 200

    qualify_response = client.post(
        "/job-applications/api-tracking-status-001/qualify"
    )
    assert qualify_response.status_code == 200

    personalize_response = client.post(
        "/job-applications/api-tracking-status-001/personalize"
    )
    assert personalize_response.status_code == 200

    prepare_response = client.post(
        "/job-applications/api-tracking-status-001/prepare"
    )
    assert prepare_response.status_code == 200

    approve_response = client.post(
        "/job-applications/api-tracking-status-001/approve"
    )
    assert approve_response.status_code == 200

    tracking_response = client.post(
        "/job-applications/api-tracking-status-001/tracking/start"
    )
    assert tracking_response.status_code == 200

    status_response = client.post(
        "/job-applications/api-tracking-status-001/tracking/status",
        json={
    "new_status": "APPLIED",
    "note": "Candidatura enviada.",
        },
    )

    assert status_response.status_code == 200

    status_data = status_response.json()

    assert status_data["tracking"] is not None
    assert status_data["tracking"]["current_status"] == "APPLIED"

    stored_response = client.get(
        "/job-applications/api-tracking-status-001"
    )

    assert stored_response.status_code == 200

    stored_data = stored_response.json()

    assert stored_data["tracking"] is not None
    assert stored_data["tracking"]["current_status"] == "APPLIED"


def test_check_follow_up_stored_job_application():
    application_payload = {
        "application_id": "api-follow-up-check-001",
        "job": {
            "job_id": "job-follow-up-check-001",
            "title": "Analista de Dados Júnior",
            "company": "Empresa Teste",
            "source": "Teste API",
            "location": "São Paulo",
            "work_model": "HYBRID",
            "employment_type": "CLT",
            "description": "Vaga de teste para verificação de follow-up.",
            "requirements": [
                "Power BI",
                "SQL",
                "Python",
                "Excel",
            ],
            "desirable_requirements": [],
        },
    }

    create_response = client.post(
        "/job-applications",
        json=application_payload,
    )
    assert create_response.status_code == 200

    qualify_response = client.post(
        "/job-applications/api-follow-up-check-001/qualify"
    )
    assert qualify_response.status_code == 200

    personalize_response = client.post(
        "/job-applications/api-follow-up-check-001/personalize"
    )
    assert personalize_response.status_code == 200

    prepare_response = client.post(
        "/job-applications/api-follow-up-check-001/prepare"
    )
    assert prepare_response.status_code == 200

    approve_response = client.post(
        "/job-applications/api-follow-up-check-001/approve"
    )
    assert approve_response.status_code == 200

    tracking_response = client.post(
        "/job-applications/api-follow-up-check-001/tracking/start"
    )
    assert tracking_response.status_code == 200

    status_response = client.post(
        "/job-applications/api-follow-up-check-001/tracking/status",
        json={
            "new_status": "APPLIED",
            "note": "Candidatura enviada.",
        },
    )
    assert status_response.status_code == 200

    follow_up_response = client.post(
        "/job-applications/api-follow-up-check-001/follow-up/check",
        params={
            "followup_count": 0,
            "last_contact_at": "2020-01-01T00:00:00+00:00",
        },
    )

    assert follow_up_response.status_code == 200

    follow_up_data = follow_up_response.json()

    assert (
        follow_up_data["application_id"]
        == "api-follow-up-check-001"
    )
    assert follow_up_data["should_follow_up"] is True


