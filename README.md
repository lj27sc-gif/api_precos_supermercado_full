# Price API Platform - Starter Repository

This repository contains a starter template for a price-collection and price-query platform:
- Django + Django REST Framework API (products, stores, prices)
- FastAPI microservice (ML predict endpoint) — example stub using PyCaret/H2O placeholders
- Kafka consumer example for price ingestion normalization
- docker-compose for local development (Postgres, Redis, Kafka (via wurstmeister images), Zookeeper)
- basic Kubernetes manifests (deployments/services) in `k8s/`
- README contains runbook and architecture summary.

## What is included (quick)
- `backend/` — Django project and app (`price_api`)
- `ml_service/` — FastAPI microservice exposing `/predict`
- `consumers/` — kafka_consumer.py example using aiokafka
- `docker-compose.yml` — local dev stack
- `requirements.txt` — top-level requirements for reference
- `k8s/` — simple k8s manifests (example)

## How to use (local dev)
1. Install Docker and Docker Compose.
2. From repo root run: `docker-compose up --build`
3. Django API will be available at `http://localhost:8000/api/`
4. Swagger/OpenAPI: `http://localhost:8000/api/docs/`
5. ML service at `http://localhost:8001/predict/`

NOTE: This is a starter template. The ML endpoint returns a dummy prediction — replace with your model and environment.
