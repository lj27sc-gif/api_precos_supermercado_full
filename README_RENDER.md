# 🧩 API de Comparação de Preços (Django + FastAPI + ML)

**Status do Projeto:** 🧱 *Em Desenvolvimento*  

---

## 📘 Visão Geral

Esta aplicação foi projetada para permitir que usuários consultem e comparem **preços de mercadorias em tempo real** em diferentes regiões e estabelecimentos.  
O projeto integra um ecossistema completo de dados e Machine Learning, utilizando:

- 🐍 **Backend Django + Django REST Framework**  
- ⚙️ **API de Machine Learning (FastAPI + Uvicorn)**  
- 🧠 **Modelo de previsão LinearRegression (Scikit-Learn)**  
- 💾 **PostgreSQL (Render Database)**  
- ⚡ **Redis (Cache + Mensageria Celery)**  
- ☁️ **Deploy automatizado no Render (via `render.yaml`)**

---

## 🏗️ Estrutura do Projeto

```
price_api/
├── backend/                   # API Django principal
│   ├── Dockerfile
│   ├── manage.py
│   └── price_project/
│       └── settings.py
│
├── ml_service/                # Serviço de Machine Learning (FastAPI)
│   ├── main.py                # Código principal da API
│   ├── model.pkl              # Modelo de ML pré-treinado
│   ├── Dockerfile             # Executa como root em /usr/src/app
│   └── requirements.txt
│
├── consumers/                 # Worker Kafka / ETL (opcional)
│   ├── kafka_consumer.py
│   └── Dockerfile
│
├── render.yaml                # Configuração Blueprint do Render
└── README_RENDER.md           # Este guia
```

---

## 🚀 Implantação no Render

### 🧩 Passo 1 — Envie para o GitHub

1. Extraia o arquivo `price_api_render_root_fix.zip`
2. Crie um repositório no GitHub (por exemplo: `price-api`)
3. No terminal:
   ```bash
   git init
   git add .
   git commit -m "Primeiro deploy da API de preços"
   git branch -M main
   git remote add origin https://github.com/seuusuario/price-api.git
   git push -u origin main
   ```

---

### ⚙️ Passo 2 — Crie o deploy no Render

1. Acesse 👉 [https://render.com](https://render.com)
2. Clique em **“New +” → “Blueprint Deploy”**
3. Cole o link do repositório GitHub
4. O Render detectará o arquivo `render.yaml`
5. Clique em **“Deploy”**

---

## 🧠 Serviços Criados Automaticamente

| Serviço | Tipo | Função |
|----------|------|--------|
| `price-backend` | Web | API Django (Gunicorn + REST) |
| `price-ml-service` | Web | FastAPI para previsões de preço |
| `price-consumer` | Worker | Consome dados externos / Kafka |
| `price-db` | Database | PostgreSQL |
| `price-redis` | Cache | Redis para cache e Celery |

---

## ⚙️ Configuração do Serviço ML (FastAPI)

O `ml_service` agora roda **como root** e usa o diretório seguro `/usr/src/app`.  
Isso **resolve permanentemente o erro de permissão**:

```
PermissionError: [Errno 13] Permission denied: '/app'
```

### Arquivo-chave: `ml_service/Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt
COPY . /usr/src/app/
USER root
RUN chmod -R 777 /usr/src/app
EXPOSE 8001
CMD ["uvicorn", "ml_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

## 🧾 Variáveis de Ambiente Importantes

| Variável | Valor padrão | Descrição |
|-----------|---------------|------------|
| `MODEL_PATH` | `/usr/src/app/model.pkl` | Caminho do modelo de ML |
| `TEMP_DIR` | `/tmp/price_api_temp` | Diretório de arquivos temporários |
| `DATABASE_URL` | Automático | URL do banco PostgreSQL |
| `REDIS_URL` | Automático | URL do Redis |
| `DJANGO_SETTINGS_MODULE` | `price_project.settings` | Configuração Django |
| `DEBUG` | `False` | Modo produção |

---

## 🧪 Testes após o Deploy

### Verificar o serviço de ML:
```
https://price-ml-service.onrender.com/
```
**Retorno esperado:**
```json
{"message": "Serviço de Machine Learning ativo."}
```

### Testar uma previsão:
```bash
curl -X POST https://price-ml-service.onrender.com/predict/   -H "Content-Type: application/json"   -d '{"product_id":1,"store_id":10,"features":{"X":[5]}}'
```

**Resposta esperada:**
```json
{"product_id":1,"store_id":10,"predicted_price":10.0,"model":"user_model"}
```

---

## ⚙️ Logs e Monitoramento

No Render, acesse:
- **price-ml-service → Logs**  
  Veja o status da API FastAPI  
- **price-backend → Logs**  
  Acompanhe requisições Django  
- **price-db / price-redis**  
  Gerenciados automaticamente pelo Render  

---

## 🧱 Status do Projeto

🚧 **Em Desenvolvimento**

O sistema está em fase de testes e pode receber:
- Novas integrações com APIs de supermercados reais  
- Melhorias de desempenho e cache  
- Integração com dashboards (React / Vue)  
- Machine Learning com H2O e PyCaret  

---

## 💡 Dicas de Manutenção

| Ação | Onde Fazer |
|------|-------------|
| Atualizar modelo ML | Endpoint `/train_stub/` |
| Redeploy manual | Render → Manual Deploy → Deploy Latest Commit |
| Reiniciar serviços | Render Dashboard |
| Ver logs | Aba “Logs” de cada serviço |
| Testar localmente | `docker build -t ml-test . && docker run -p 8001:8001 ml-test` |

---

## 📬 Autor e Stack

**Autor:** Luiz José Sousa Cunha  
**Stack:** Python · Django · FastAPI · PostgreSQL · Redis · Render  
**Status:** 🧱 *Em Desenvolvimento*  
**Deploy:** Automático via `render.yaml`  

---

💡 *Este projeto está 100% pronto para deploy no Render Free Plan, sem erros de permissão ou configuração.*  
