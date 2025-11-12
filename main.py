from fastapi import FastAPI
from pydantic import BaseModel
import pickle, os, pathlib

app = FastAPI(title="ML Service - Previsão de Preços")

MODEL_PATH = os.environ.get("MODEL_PATH", "/app/ml_service/temp/model.pkl")
pathlib.Path(os.path.dirname(MODEL_PATH)).mkdir(parents=True, exist_ok=True)

class PredictRequest(BaseModel):
    product_id: int
    store_id: int
    features: dict = {}

@app.get("/")
async def root():
    return {"message": "Serviço de Machine Learning ativo."}

@app.post("/predict/")
async def predict(req: PredictRequest):
    if not os.path.exists(MODEL_PATH):
        base_price = req.features.get("base_price", 10.0)
        return {
            "product_id": req.product_id,
            "store_id": req.store_id,
            "predicted_price": round(base_price * 1.02, 2),
            "model": "fallback"
        }
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        X = req.features.get("X", [[1.0]])
        pred = model.predict([X])[0]
        return {
            "product_id": req.product_id,
            "store_id": req.store_id,
            "predicted_price": float(pred),
            "model": "user_model"
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/train_stub/")
async def train_stub(payload: dict):
    from sklearn.linear_model import LinearRegression
    import numpy as np
    X = payload.get("X", [[1.0], [2.0], [3.0]])
    y = payload.get("y", [2.0, 4.0, 6.0])
    model = LinearRegression()
    model.fit(X, y)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    return {"status": "Modelo treinado", "model_path": MODEL_PATH}
