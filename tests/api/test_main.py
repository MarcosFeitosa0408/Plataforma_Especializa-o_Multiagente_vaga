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
