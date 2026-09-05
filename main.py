from fastapi import FastAPI


app = FastAPI(
    title="Plataforma Especialização Multiagente Vaga",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "multiagent-job-platform",
        "version": "0.1.0",
    }
