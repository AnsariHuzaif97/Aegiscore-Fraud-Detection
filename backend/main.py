from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import io
import os
import uuid
from typing import Dict, Any
from datetime import datetime
from backend.db import init_db, get_db
from backend.ml import FraudModel
import json

app = FastAPI(title="AegisCore FIP API")
init_db()
fraud_model = FraudModel()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
BRAIN_DIR = r"C:\Users\ansar\.gemini\antigravity\brain\b2b0f120-cb76-4865-bfe2-630ccd88d51f"

app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
app.mount("/images", StaticFiles(directory=os.path.join(FRONTEND_DIR, "images")), name="images")

@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/dashboard")
async def dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))

@app.get("/api/stats")
async def get_stats():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM transactions")
    tx_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM predictions WHERE prediction=1")
    alerts = c.fetchone()[0]
    
    c.execute('''SELECT SUM(t.amount) 
                 FROM transactions t 
                 JOIN predictions p ON t.id = p.transaction_id 
                 WHERE p.prediction = 1''')
    savings = c.fetchone()[0]
    if savings is None:
        savings = 0.0
        
    c.execute("SELECT probability FROM predictions")
    probs = [float(r[0])*100 for r in c.fetchall()]
    
    buckets = [0] * 10
    for p in probs:
        idx = int(p // 10)
        if idx >= 10: idx = 9
        buckets[idx] += 1
        
    chart_data = buckets
        
    conn.close()
    
    anomaly_ratio = (alerts / tx_count * 100) if tx_count > 0 else 0.0
    
    return {
        "activeAlerts": alerts,
        "transactionsScanned": f"{tx_count:,}",
        "financialSavings": f"₹{savings:,.2f}",
        "anomalyRatio": f"{anomaly_ratio:.2f}%",
        "chartData": chart_data
    }

class TransactionPayload(BaseModel):
    features: Dict[str, float]

@app.post("/api/predict")
async def predict_fraud(payload: TransactionPayload):
    import traceback
    try:
        tx_id = str(uuid.uuid4())
        pred_id = str(uuid.uuid4())
        
        amount = payload.features.get("Amount", 0.0)
        
        # ML Prediction
        prob, pred, shap_dict = fraud_model.predict(payload.features)
        risk_level = "CRITICAL" if prob > 0.8 else "HIGH" if prob > 0.5 else "LOW"
        
        # Save to DB
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO transactions VALUES (?, ?, ?, ?)", 
                  (tx_id, datetime.now().isoformat(), amount, json.dumps(payload.features)))
        
        c.execute("INSERT INTO predictions VALUES (?, ?, ?, ?, ?)",
                  (pred_id, tx_id, prob, pred, risk_level))
                  
        for feat, s_val in shap_dict.items():
            c.execute("INSERT INTO explanations (prediction_id, feature, shap_value) VALUES (?, ?, ?)",
                      (pred_id, feat, s_val))
        conn.commit()
        conn.close()
        
        return {
            "transactionId": tx_id,
            "fraudProbability": prob,
            "isFraud": bool(pred),
            "riskLevel": risk_level,
            "shapValues": shap_dict
        }
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.post("/api/batch-predict")
async def batch_predict(file: UploadFile = File(...)):
    import traceback
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        probs, preds = fraud_model.predict_batch(df)
        
        df['Fraud_Probability'] = probs
        df['Is_Fraud'] = preds
        
        flagged_df = df[df['Is_Fraud'] == 1].copy()
        flagged_df = flagged_df.sort_values(by='Fraud_Probability', ascending=False)
        
        results = {
            "totalProcessed": len(df),
            "fraudDetected": len(flagged_df),
            "capitalAtRisk": float(df.get('Amount', pd.Series([0.0])).sum()),
            "capitalSaved": float(flagged_df.get('Amount', pd.Series([0.0])).sum()),
            "flaggedTransactions": []
        }
        
        # Sort all transactions by probability to show top 100 regardless of threshold
        display_df = df.sort_values(by='Fraud_Probability', ascending=False)
        
        for idx, row in display_df.head(100).iterrows():
            tx_data = {
                "time": float(row.get("Time", 0)),
                "amount": float(row.get("Amount", 0)),
                "probability": float(row.get("Fraud_Probability", 0)),
                "features": {f"V{i}": float(row.get(f"V{i}", 0)) for i in range(1, 29)}
            }
            results["flaggedTransactions"].append(tx_data)
            
        anomaly_df = df[df['Is_Fraud'] == 1].sort_values(by='Fraud_Probability', ascending=False)
        safe_df = df[df['Is_Fraud'] == 0].sort_values(by='Fraud_Probability', ascending=False)
        
        import zipfile
        zip_path = os.path.join(BASE_DIR, "batch_reports.zip")
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("critical_anomalies_report.csv", anomaly_df.to_csv(index=False))
            zf.writestr("safe_transactions_report.csv", safe_df.to_csv(index=False))
            
        return results
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/api/download-batch")
async def download_batch_report():
    zip_path = os.path.join(BASE_DIR, "batch_reports.zip")
    if os.path.exists(zip_path):
        return FileResponse(zip_path, filename="Enterprise_Fraud_Reports.zip", media_type="application/zip")
    return {"error": "No recent batch report found."}

@app.get("/avatar.jpg")
async def get_avatar():
    import os
    avatar_path = os.path.join(FRONTEND_DIR, "avatar.jpg")
    if os.path.exists(avatar_path):
        return FileResponse(avatar_path, media_type="image/jpeg")
    return {"error": "Avatar not found"}

@app.get("/logo.png")
async def get_logo():
    import os
    logo_path = os.path.join(FRONTEND_DIR, "logo.png")
    if os.path.exists(logo_path):
        return FileResponse(logo_path, media_type="image/png")
    return {"error": "Logo not found"}

@app.get("/api/debug")
async def debug_model_load():
    import traceback
    import joblib
    import shap
    try:
        model_path = r"d:\dataset\ImbalanceDatasetHandling\fraud_detection_model.pkl"
        import os
        if not os.path.exists(model_path):
            return {"error": "File not found at path", "path": model_path}
            
        model = joblib.load(model_path)
        
        info = {
            "type": str(type(model)),
            "is_pipeline": hasattr(model, "named_steps")
        }
        
        if hasattr(model, "named_steps"):
            info["steps"] = list(model.named_steps.keys())
            classifier = model.named_steps[info["steps"][-1]]
            info["classifier_type"] = str(type(classifier))
        
        return {"success": True, "info": info}
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/api/transactions")
async def get_transactions():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT t.id, t.timestamp, t.amount, p.probability, p.risk_level 
                 FROM transactions t JOIN predictions p ON t.id = p.transaction_id 
                 ORDER BY t.timestamp DESC LIMIT 10''')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
