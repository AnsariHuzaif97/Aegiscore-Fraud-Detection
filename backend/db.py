import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "fip_database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        timestamp TEXT,
        amount REAL,
        features_json TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS predictions (
        id TEXT PRIMARY KEY,
        transaction_id TEXT,
        probability REAL,
        prediction INTEGER,
        risk_level TEXT,
        FOREIGN KEY(transaction_id) REFERENCES transactions(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS explanations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction_id TEXT,
        feature TEXT,
        shap_value REAL,
        FOREIGN KEY(prediction_id) REFERENCES predictions(id)
    )''')
    
    conn.commit()
    conn.close()
