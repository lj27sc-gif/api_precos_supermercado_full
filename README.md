Plataforma de API de Preços - Repositório Inicial
Este repositório contém um modelo inicial para uma plataforma de coleta e consulta de preços:

API Django + Django REST Framework (produtos, lojas, preços)
Microsserviço FastAPI (endpoint de previsão por aprendizado de máquina) — exemplo de stub usando placeholders PyCaret/H2O
Exemplo de consumidor Kafka para normalização de ingestão de preços
docker-compose para desenvolvimento local (Postgres, Redis, Kafka (via imagens wurstmeister), Zookeeper)
Manifestos básicos do Kubernetes (deployments/services) em k8s/
O arquivo README contém o runbook e um resumo da arquitetura.

O que está incluído (resumo)
backend/ — Projeto e aplicativo Django (price_api)
ml_service/ — Microsserviço FastAPI expondo /predict
consumers/ — Exemplo kafka_consumer.py usando aiokafka
docker-compose.yml — Stack de desenvolvimento local
requirements.txt — Requisitos de alto nível para referência
k8s/ — Manifestos simples do Kubernetes (exemplo)
Como usar (desenvolvimento local)
Instale o Docker e o Docker Compose.

A partir da raiz do repositório, execute: docker-compose up --build
A API do Django estará disponível em http://localhost:8000/api/
Swagger/OpenAPI: http://localhost:8000/api/docs/
Serviço de ML em http://localhost:8001/predict/
NOTA: Este é um modelo inicial. O endpoint de ML retorna uma previsão fictícia — substitua-a pelo seu modelo e ambiente.
