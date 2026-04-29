import requests
import time
import random

URL = "http://localhost:8000/submit_claim"

# Data Pools
health_providers = ["HOSP-ALPHA", "CLINIC-BETA", "DR-SHARMA", "FRAUD-CLINIC"]
auto_providers = ["GARAGE-X", "AUTO-WORKS-Y", "FRAUD-GARAGE"]
users = [f"ABHA-1234-{i}" for i in range(1000, 1050)]
schemes = ["PRIVATE", "PM-JAY", "CGHS"]
health_items = ["CHECKUP", "XRAY", "SURGERY", "MATERNITY", "KNEE_REPLACEMENT"]
auto_items = ["BUMPER_REPAIR", "WINDSHIELD", "ENGINE_REBUILD"]
payment_modes = ["UPI", "NEFT"]

print("🤖 Omni-Domain Live Traffic Bot Started! Press Ctrl+C to stop.")

while True:
    # 1. Decide if this is a Health or Auto claim
    claim_type = random.choices(["HEALTH", "AUTO"], weights=[0.7, 0.3])[0]
    
    # 2. Setup universal fields
    scheme = random.choice(schemes)
    user = random.choice(users)
    payment_mode = random.choice(payment_modes)
    
    # Generate fake UPI or NEFT details
    payment_address = f"user{random.randint(100,999)}@okicici" if payment_mode == "UPI" else f"ACC:100{random.randint(1000,9999)} IFSC:HDFC001"
    
    data = {
        "claim_type": claim_type,
        "gov_scheme": scheme,
        "user_id": user,
        "payment_mode": payment_mode,
        "payment_address": payment_address,
        "vehicle_reg": None,
        "age": None,
        "gender": None
    }

    # 10% chance to simulate a blatant Fraud attempt
    is_fraud = random.random() < 0.10

    # 3. Populate Domain-Specific Fields
    if claim_type == "HEALTH":
        data["provider_id"] = "FRAUD-CLINIC" if is_fraud else random.choice(health_providers)
        data["item_code"] = "CHECKUP" if is_fraud else random.choice(health_items)
        data["age"] = random.randint(20, 65)
        data["gender"] = "FEMALE" if data["item_code"] == "MATERNITY" else random.choice(["MALE", "FEMALE"])
        
        if is_fraud:
            data["amount_billed"] = random.uniform(500000, 900000) # Insane amount for a checkup
        else:
            if data["item_code"] == "CHECKUP": data["amount_billed"] = random.uniform(800, 2000)
            elif data["item_code"] == "XRAY": data["amount_billed"] = random.uniform(2500, 6000)
            elif data["item_code"] == "MATERNITY": data["amount_billed"] = random.uniform(40000, 80000)
            elif data["item_code"] == "KNEE_REPLACEMENT": data["amount_billed"] = random.uniform(150000, 300000)
            else: data["amount_billed"] = random.uniform(60000, 150000)

    elif claim_type == "AUTO":
        data["provider_id"] = "FRAUD-GARAGE" if is_fraud else random.choice(auto_providers)
        data["item_code"] = "BUMPER_REPAIR" if is_fraud else random.choice(auto_items)
        data["vehicle_reg"] = f"TN-01-AB-{random.randint(1000, 9999)}"
        
        if is_fraud:
            data["amount_billed"] = random.uniform(80000, 150000) # Over-invoiced bumper repair
        else:
            if data["item_code"] == "BUMPER_REPAIR": data["amount_billed"] = random.uniform(5000, 15000)
            elif data["item_code"] == "WINDSHIELD": data["amount_billed"] = random.uniform(8000, 20000)
            else: data["amount_billed"] = random.uniform(50000, 120000)

    # Clean up the money format
    data["amount_billed"] = round(data["amount_billed"], 2)

    # 4. Fire the request!
    try:
        response = requests.post(URL, json=data)
        if response.status_code == 200:
            res_data = response.json()
            status = "🔴 ESCROW BLOCKED" if "BLOCKED" in res_data['payment_status'] else "🟢 NEFT/UPI CLEARED"
            print(f"[{claim_type}] {data['provider_id']} -> {data['item_code']} for ₹{data['amount_billed']} | {status}")
        else:
            print(f"Server Data Error ({response.status_code}): {response.text}")
    except requests.exceptions.ConnectionError:
        print("Server not responding. Is 'uvicorn main:app --reload' running in your other terminal?")
    
    time.sleep(2.5)