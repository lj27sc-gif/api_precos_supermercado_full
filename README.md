Status : Em desenvolvimento 


# Plataforma de API de Preços - Repositório Inicial

Este repositório contém um modelo inicial para uma plataforma de coleta e consulta de preços:
- API Django + Django REST Framework (produtos, lojas, preços)
- Microsserviço FastAPI (endpoint de previsão por aprendizado de máquina) — exemplo de stub usando placeholders PyCaret/H2O
- Exemplo de consumidor Kafka para normalização da ingestão de preços
- docker-compose para desenvolvimento local (PostgreSQL, Redis, Kafka (via imagens wurstmeister), Zookeeper)
- Manifestos básicos do Kubernetes (deployments/services) em `k8s/`
- O arquivo README contém o guia de execução e um resumo da arquitetura.

- ## O que está incluído (resumo)
- `backend/` — Projeto e aplicativo Django (`price_api`)
- `ml_service/` — Microsserviço FastAPI que expõe `/predict`
- `consumers/` — Exemplo kafka_consumer.py usando aiokafka
- `docker-compose.yml` — Stack de desenvolvimento local
- `requirements.txt` — Requisitos de alto nível para referência
- `k8s/` — Manifestos simples do Kubernetes (exemplo)

## Como usar (desenvolvimento local)
1. Instale o Docker e o Docker Compose.
2. A partir da raiz do repositório, execute: `docker-compose up --build`
3. A API do Django estará disponível em `http://localhost:8000/api/`
4. Swagger/OpenAPI: `http://localhost:8000/api/docs/`
5. Serviço de ML em `http://localhost:8001/predict/`

NOTA: Este é um modelo inicial. O endpoint de ML retorna uma previsão fictícia — substitua-a pelo seu modelo e ambiente.
