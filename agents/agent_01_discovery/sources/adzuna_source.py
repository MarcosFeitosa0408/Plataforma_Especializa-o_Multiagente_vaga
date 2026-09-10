from agents.agent_01_discovery.sources.base_source import BaseJobSource


class AdzunaJobSource(BaseJobSource):
    """Fonte de vagas baseada na API da Adzuna."""

    def __init__(
        self,
        app_id: str,
        app_key: str,
    ):
        self.app_id = app_id
        self.app_key = app_key

    def fetch_jobs(self):
        """A coleta real da API será implementada na próxima etapa."""

        return []

    def normalize_response(
        self,
        api_response: dict,
    ) -> list[dict]:
        """Converte a resposta da Adzuna para o formato bruto da plataforma."""

        jobs: list[dict] = []

        for item in api_response.get("results", []):
            jobs.append(
                {
                    "job_id": str(item["id"]),
                    "title": item["title"],
                    "company": item["company"]["display_name"],
                    "source": "ADZUNA",
                    "url": item.get("redirect_url"),
                    "location": item.get(
                        "location",
                        {},
                    ).get(
                        "display_name",
                        "NAO_IDENTIFICADO",
                    ),
                    "description": item.get("description", ""),
                }
            )

        return jobs
