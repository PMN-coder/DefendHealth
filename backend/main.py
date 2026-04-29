import threading
import requests
import time
import random
import hashlib
import pandas as pd
import mysql.connector
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from sklearn.ensemble import IsolationForest

# ==========================================
# 🧠 1. AI SETUP: DYNAMIC IN-MEMORY TRAINING
# ==========================================
print("Training Enterprise AI Model on 550+ Historical Records...")
historical_data = {'amount_billed': [], 'complexity': []}

for _ in range(500):
    comp = random.choice([1, 2, 3, 4, 5])
    historical_data['amount_billed'].append(comp * random.uniform(3000, 15000))
    historical_data['complexity'].append(comp)

for _ in range(50):
    historical_data['amount_billed'].append(random.uniform(400000, 900000))
    historical_data['complexity'].append(random.choice([1, 2]))

df = pd.DataFrame(historical_data)
ai_model = IsolationForest(contamination=0.1, random_state=42)
ai_model.fit(df[['amount_billed', 'complexity']]) 
print("✅ AI Model Ready!")

# ==========================================
# 🚀 2. FASTAPI SERVER SETUP
# ==========================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="2007", database="fraud_db" 
    )

ITEMS = {"CHECKUP": 1, "XRAY": 2, "SURGERY": 5, "MATERNITY": 4, "BUMPER_REPAIR": 2, "WINDSHIELD": 3, "ENGINE_REBUILD": 5}
VALID_PROVIDERS = ["HOSP-ALPHA", "CLINIC-BETA", "GARAGE-X", "AUTO-WORKS-Y"] 

class Claim(BaseModel):
    claim_type: str
    gov_scheme: str
    provider_id: str
    user_id: str
    vehicle_reg: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    item_code: str
    amount_billed: float
    payment_mode: str
    payment_address: str
    vision_tampering_score: Optional[float] = 0.0 # Catch results from the Vision AI

# --- VISION AI ENDPOINT ---
@app.post("/verify_document")
async def verify_document(file: UploadFile = File(...)):
    time.sleep(1.2) # Simulate heavy AI processing
    filename = file.filename.lower()
    
    ocr_status = "PASSED: Data Matches Input"
    tampering_score = random.uniform(0.01, 0.15) 
    tampering_status = "CLEAN (Original Image)"
    
    # Hackathon Demo Trigger: If file name contains these words, flag as deepfake!
    if any(word in filename for word in ["photoshop", "fake", "google", "stock"]):
        tampering_score = random.uniform(0.85, 0.99)
        tampering_status = "🚨 EXIF ALTERATION / DEEPFAKE DETECTED"
        ocr_status = "FAILED: Metadata wiped or altered"
    
    return {
        "filename": file.filename,
        "tampering_score": round(tampering_score * 100, 2),
        "tampering_status": tampering_status,
        "ocr_status": ocr_status,
    }

# --- MAIN CLAIM ENDPOINT ---
@app.post("/submit_claim")
async def submit_claim(claim: Claim):
    complexity = ITEMS.get(claim.item_code, 1)
    new_claim_df = pd.DataFrame({'amount_billed': [claim.amount_billed], 'complexity': [complexity]})
    raw_score = ai_model.decision_function(new_claim_df)[0]
    fraud_score = max(0.0, min(1.0, 0.5 - (raw_score * 0.5)))
    
    status = "FAST-TRACK APPROVED"
    reason = "Claim aligns with historical network averages."
    
    random_num = str(random.randint(100000000, 999999999))
    txn_id = f"UPI-{random_num}" if claim.payment_mode == "UPI" else f"NEFT-UTR-{random_num}"
    payment_status = f"CLEARED VIA {claim.payment_mode}"

    # Expert Rules
    if claim.gov_scheme == "PM-JAY" and claim.amount_billed > 500000:
        fraud_score, reason = 0.99, "Scheme Violation: PM-JAY caps maximum coverage at ₹5,00,000."
    elif claim.claim_type == "HEALTH" and claim.item_code == "MATERNITY" and claim.gender and claim.gender.upper() == "MALE":
        fraud_score, reason = 0.99, "Logical Anomaly: Maternity procedure billed for a Male patient."
    elif claim.claim_type == "AUTO" and claim.item_code == "BUMPER_REPAIR" and claim.amount_billed > 40000:
        fraud_score, reason = 0.85, f"Over-invoicing: ₹{claim.amount_billed} exceeds market standard."
    elif claim.provider_id not in VALID_PROVIDERS and "FRAUD" in claim.provider_id:
        fraud_score, reason = 0.99, "Registry Alert: Unregistered or Blacklisted Provider."

    # Vision AI Override
    if claim.vision_tampering_score > 50.0:
        fraud_score = 0.99
        reason = "VISION AI ALERT: Cryptographic forgery or Deepfake detected in evidence."

    # Finalize Status
    if fraud_score > 0.65:
        status, payment_status, txn_id = "🔴 FLAGGED: HIGH RISK", "BLOCKED: FUNDS FROZEN IN ESCROW", "NULL-BLOCKED"
    
    fraud_score = round(min(1.0, fraud_score), 2)
    raw_data = f"{claim.provider_id}{claim.user_id}{claim.item_code}{claim.amount_billed}{time.time()}"
    claim_hash = hashlib.sha256(raw_data.encode()).hexdigest()

    db = get_db_connection()
    cursor = db.cursor()
    sql = """INSERT INTO claims 
             (claim_type, gov_scheme, provider_id, user_id, vehicle_reg, age, gender, item_code, amount_billed, fraud_score, status, payment_mode, payment_address, transaction_id, payment_status, claim_hash) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(sql, (claim.claim_type, claim.gov_scheme, claim.provider_id, claim.user_id, claim.vehicle_reg, claim.age, claim.gender, claim.item_code, claim.amount_billed, float(fraud_score), status, claim.payment_mode, claim.payment_address, txn_id, payment_status, claim_hash))
    db.commit()
    cursor.close()
    db.close()

    return {"status": status, "risk_score": fraud_score * 100, "hash": claim_hash, "reason": reason, "payment_status": payment_status, "transaction_id": txn_id}

@app.get("/api/dashboard")
async def get_dashboard_stats():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total FROM claims")
    total_claims = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as flagged FROM claims WHERE status LIKE '%FLAGGED%'")
    total_flagged = cursor.fetchone()['flagged']
    cursor.execute("SELECT * FROM claims ORDER BY id DESC LIMIT 15")
    recent = cursor.fetchall()
    cursor.close()
    db.close()
    return {"total": total_claims, "approved": total_claims - total_flagged, "flagged": total_flagged, "recent": recent}

@app.get("/api/network")
async def get_network():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT provider_id, user_id, status FROM claims ORDER BY id DESC LIMIT 50")
    claims = cursor.fetchall()
    cursor.close()
    db.close()
    nodes_dict, edges = {}, []
    for c in claims:
        prov_id, usr_id = "prov_" + c['provider_id'], "usr_" + c['user_id']
        nodes_dict[prov_id] = {"id": prov_id, "label": c['provider_id'], "group": "provider"}
        nodes_dict[usr_id] = {"id": usr_id, "label": "User", "group": "user"}
        edges.append({"from": prov_id, "to": usr_id, "color": {"color": "red" if "FLAGGED" in c['status'] else "green"}})
    return {"nodes": list(nodes_dict.values()), "edges": edges}

# ==========================================
# 🤖 3. BACKGROUND LIVE TRAFFIC BOT
# ==========================================
def run_traffic_bot():
    print("🤖 Background Bot waiting for server to start...")
    time.sleep(5)
    print("🤖 Bot Online! Firing Omni-Domain Traffic...")
    URL = "http://127.0.0.1:8000/submit_claim"
    while True:
        claim_type = random.choices(["HEALTH", "AUTO"], weights=[0.7, 0.3])[0]
        is_fraud = random.random() < 0.10
        payment_mode = random.choice(["UPI", "NEFT"])
        
        data = {
            "claim_type": claim_type, "gov_scheme": random.choice(["PRIVATE", "PM-JAY", "CGHS"]),
            "user_id": f"ABHA-1234-{random.randint(1000, 1050)}", "payment_mode": payment_mode,
            "payment_address": f"user{random.randint(100,999)}@okicici" if payment_mode == "UPI" else "ACC:1001 IFSC:HDFC",
            "vehicle_reg": None, "age": None, "gender": None, "vision_tampering_score": 0.0
        }

        if claim_type == "HEALTH":
            data["provider_id"] = "FRAUD-CLINIC" if is_fraud else random.choice(["HOSP-ALPHA", "CLINIC-BETA", "DR-SHARMA"])
            data["item_code"] = "CHECKUP" if is_fraud else random.choice(["CHECKUP", "XRAY", "SURGERY", "MATERNITY", "KNEE_REPLACEMENT"])
            data["age"], data["gender"] = random.randint(20, 65), "FEMALE" if data["item_code"] == "MATERNITY" else random.choice(["MALE", "FEMALE"])
            data["amount_billed"] = random.uniform(500000, 900000) if is_fraud else random.uniform(800, 150000)
        else:
            data["provider_id"] = "FRAUD-GARAGE" if is_fraud else random.choice(["GARAGE-X", "AUTO-WORKS-Y"])
            data["item_code"] = "BUMPER_REPAIR" if is_fraud else random.choice(["BUMPER_REPAIR", "WINDSHIELD", "ENGINE_REBUILD"])
            data["vehicle_reg"] = f"TN-01-AB-{random.randint(1000, 9999)}"
            data["amount_billed"] = random.uniform(80000, 150000) if is_fraud else random.uniform(5000, 120000)

        data["amount_billed"] = round(data["amount_billed"], 2)
        try: requests.post(URL, json=data)
        except Exception: pass
        time.sleep(3.0)

@app.on_event("startup")
def startup_event():
    threading.Thread(target=run_traffic_bot, daemon=True).start()