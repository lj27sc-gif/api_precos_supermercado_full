from fastapi import FastAPI
from pydantic import BaseModel
import pickle, os, pathlib, requests

app = FastAPI(title="ML Service - Previsão de Preços")

MODEL_PATH = os.environ.get("MODEL_PATH", "/tmp/ml_model/model.pkl")
pathlib.Path(os.path.dirname(MODEL_PATH)).mkdir(parents=True, exist_ok=True)
print(f"Modelo path: {MODEL_PATH}")

class PredictRequest(BaseModel):
    product_id: int
    store_id: int
    features: dict = {}

@app.get('/')
def root():
    return {'message':'Serviço de ML ativo'}

@app.post('/predict/')
def predict(req: PredictRequest):
    if not os.path.exists(MODEL_PATH):
        base = req.features.get('base_price', 10.0)
        return {'product_id': req.product_id, 'store_id': req.store_id, 'predicted_price': round(base*1.02,2), 'model':'fallback'}
    with open(MODEL_PATH,'rb') as f:
        model = pickle.load(f)
    X = req.features.get('X', [[1.0]])
    pred = model.predict([X])[0]
    return {'product_id': req.product_id, 'store_id': req.store_id, 'predicted_price': float(pred), 'model':'user_model'}
