# Plataforma_Especialização_Multiagente_Vaga

## Objetivo

Construir uma plataforma multiagente para busca, qualificação, personalização, candidatura, acompanhamento e otimização de oportunidades profissionais.

O sistema deve priorizar oportunidades CLT compatíveis com o perfil profissional armazenado em:

data/master_profile/MASTER_PROFILE.json

Esse arquivo é a fonte oficial de verdade sobre o candidato.

## Regra fundamental

Nunca inventar:

- competências
- experiências
- empresas
- cargos
- formação
- certificações
- resultados
- salários
- projetos
- tecnologias
- informações pessoais

Quando uma informação não estiver comprovada no MASTER_PROFILE:

NAO_IDENTIFICADO

## Arquitetura de agentes

Implementar os seguintes agentes:

### Agent 00 — Memory

Responsável por:

- carregar MASTER_PROFILE.json
- validar estrutura
- disponibilizar dados confiáveis aos demais agentes
- impedir uso de informação não comprovada

### Agent 01 — Discovery

Responsável por descobrir vagas compatíveis com:

- Analista de Dados
- Analista de Dados Júnior
- Analista de Dados I
- Analista de BI
- Analista de BI Júnior
- Business Intelligence
- Data Analytics
- cargos relacionados definidos no MASTER_PROFILE

Não realizar candidatura.

### Agent 02 — Qualification

Avaliar compatibilidade entre candidato e vaga.

Score de 0 a 10.

Pesos:

- competências técnicas: 35%
- experiência profissional: 20%
- atividades da vaga: 15%
- senioridade: 10%
- localização/modelo de trabalho: 10%
- compatibilidade ATS: 10%

Regras:

- score >= 7.0: recomendada
- score 6.5 até 6.9: fila secundária
- abaixo de 6.5: baixa prioridade

Requisitos eliminatórios devem ser identificados separadamente.

### Agent 03 — Personalization

Criar versões personalizadas de:

- currículo
- resumo profissional
- competências
- carta de apresentação

Somente com informações comprovadas no MASTER_PROFILE.

Nunca fabricar experiência para aumentar o fit.

### Agent 04 — Application

Preparar candidatura.

A candidatura exige aprovação humana antes de envio.

Nunca realizar candidatura em massa sem aprovação.

### Agent 05 — Tracking

Controlar pipeline:

DISCOVERED
QUALIFIED
VALIDATION_REVIEW
APPROVED
READY_TO_APPLY
APPLIED
SCREENING
INTERVIEW
FINAL
OFFER
HIRED

Estados finais adicionais:

REJECTED
WITHDRAWN
NO_RESPONSE
EXPIRED
APPLICATION_FAILED

### Agent 06 — Follow-up

Gerenciar acompanhamento após candidatura.

Padrão:

- primeiro follow-up aproximadamente 5 a 7 dias depois
- segundo follow-up 7 a 10 dias depois
- máximo de 2 contatos

Evitar mensagens repetitivas ou insistentes.

### Agent 07 — Optimization

Analisar resultados reais do pipeline.

Métricas:

- vagas descobertas
- vagas qualificadas
- vagas com fit >= 8
- candidaturas
- respostas
- entrevistas
- etapas finais
- ofertas
- contratações
- taxas de conversão
- tempo médio entre etapas

O agente pode recomendar mudanças de estratégia.

Nunca alterar fatos do MASTER_PROFILE.

## Componentes transversais

Implementar:

- Orchestrator
- Validation Gate
- Human Approval
- Event system
- schemas compartilhados
- logging
- tratamento de erros

## Objeto central

Criar um modelo:

JOB_APPLICATION_OBJECT

Ele deve acompanhar uma oportunidade durante todo o pipeline.

Campos mínimos:

- job_id
- title
- company
- source
- url
- location
- work_model
- employment_type
- description
- requirements
- desirable_requirements
- discovered_at
- qualification
- fit_score
- eliminatory_gaps
- matched_skills
- missing_skills
- ats_keywords
- status
- human_approval
- application_data
- followups
- events
- created_at
- updated_at

## Stack

Backend:

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL

IA:

- OpenAI Agents SDK
- agentes com ferramentas e handoffs
- guardrails
- Human-in-the-Loop

Frontend posteriormente:

- React
- TypeScript

Infraestrutura:

- Docker
- GitHub
- GitHub Codespaces

Testes:

- pytest

## Estrutura existente

agents/
  agent_00_memory/
  agent_01_discovery/
  agent_02_qualification/
  agent_03_personalization/
  agent_04_application/
  agent_05_tracking/
  agent_06_followup/
  agent_07_optimization/

core/
  schemas/
  validation/
  orchestrator/
  events/

data/
  master_profile/
  raw/
  processed/
  applications/

documents/
  base/
  personalized/
  cover_letters/

tests/
  agents/
  validation/
  integration/

config/

## Estratégia de implementação

Não tentar implementar tudo de uma vez.

Implementar por fases.

### Fase 1 — Foundation

Criar:

- pyproject.toml
- dependências
- configurações
- schemas Pydantic
- loader do MASTER_PROFILE
- Validation Gate
- JOB_APPLICATION_OBJECT
- testes

### Fase 2 — Agent 00

Implementar Memory Agent.

Testar carregamento e validação do MASTER_PROFILE.

### Fase 3 — Agents 01 e 02

Discovery e Qualification.

Discovery deve utilizar interfaces abstratas/providers para permitir múltiplas fontes posteriormente.

Não criar scraping frágil como núcleo da aplicação.

### Fase 4 — Agent 03

Personalização baseada exclusivamente nas evidências do candidato.

### Fase 5 — Agents 04, 05 e 06

Application, Tracking e Follow-up.

Exigir aprovação humana antes da candidatura.

### Fase 6 — Agent 07

Analytics e feedback loop.

### Fase 7 — API

Criar endpoints FastAPI.

### Fase 8 — persistência

Integrar PostgreSQL.

### Fase 9 — frontend

Criar interface React/TypeScript.

## Qualidade

Todo código deve:

- possuir type hints
- possuir docstrings onde agregarem valor
- ser modular
- possuir tratamento de erros
- evitar duplicação
- possuir testes
- usar variáveis de ambiente para segredos

Nunca colocar API keys no Git.

Adicionar .env ao .gitignore.

Criar .env.example somente com nomes das variáveis.

## Processo de trabalho do Codex

Antes de implementar:

1. inspecionar todo o repositório
2. ler MASTER_PROFILE.json
3. verificar git status
4. produzir plano de implementação
5. implementar fase por fase
6. executar testes após cada fase
7. corrigir falhas antes de avançar
8. mostrar resumo das alterações
9. não apagar dados existentes sem justificativa
10. não alterar informações factuais do MASTER_PROFILE sem autorização humana

## Critério de conclusão inicial

A primeira entrega é considerada funcional quando:

- MASTER_PROFILE é validado por Pydantic
- Agent 00 funciona
- JOB_APPLICATION_OBJECT funciona
- Qualification Agent consegue avaliar uma vaga de exemplo
- Orchestrator consegue executar Memory -> Qualification
- Validation Gate bloqueia informação inventada
- testes passam
- FastAPI possui health check
- README explica como executar o projeto

Não implementar candidatura real em plataformas externas nesta primeira entrega.

