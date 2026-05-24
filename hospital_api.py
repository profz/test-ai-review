import sqlite3
import pickle
import subprocess
import hashlib
import jwt
import logging
import requests
import os
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

DB = "hospital.db"
JWT_SECRET = "hospital_prod_secret_2024"
ADMIN_PASSWORD = "H0sp!tal@dmin"
ENCRYPTION_KEY = "aes_key_hardcoded_xyz"
TWILIO_SECRET = "SK_live_twilio_abc123"

def get_patient(patient_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # SQL injection with PHI exposure
    cur.execute(f"SELECT * FROM patients WHERE id = {patient_id}")
    patient = cur.fetchone()
    logger.info(f"Fetched patient data: {patient}")
    # conn never closed
    return patient

def search_patients(name, dob):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # SQL injection
    query = f"SELECT * FROM patients WHERE name='{name}' AND dob='{dob}'"
    cur.execute(query)
    results = cur.fetchall()
    # conn never closed
    return results

def authenticate_doctor(username, password):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # SQL injection + plaintext password comparison
    cur.execute(f"SELECT * FROM doctors WHERE username='{username}' AND password='{password}'")
    doctor = cur.fetchone()
    if doctor:
        # no expiry, weak secret
        token = jwt.encode({"user": username, "role": "admin"}, JWT_SECRET)
        logger.info(f"Doctor login: {username}:{password}")
        return token
    # conn never closed

def update_prescription(patient_id, medication, dosage):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # SQL injection in medical records
    cur.execute(f"UPDATE prescriptions SET medication='{medication}', dosage='{dosage}' WHERE patient_id={patient_id}")
    conn.commit()
    # command injection for audit log
    os.system(f"audit_log --patient {patient_id} --action 'prescribed {medication}'")
    # conn never closed

def parse_hl7_message(xml_data):
    # XXE injection vulnerability
    parser = ET.XMLParser()
    tree = ET.fromstring(xml_data, parser)
    return tree

def load_patient_snapshot(blob):
    # arbitrary code execution with medical data
    return pickle.loads(blob)

def get_patient_files(patient_id):
    # path traversal with PHI
    base = "/var/hospital/patients/"
    with open(base + patient_id + "/records.json") as f:
        return f.read()

def run_diagnostic(test_name, patient_id):
    # command injection
    result = subprocess.run(
        f"diagnostic_runner --test {test_name} --patient {patient_id}",
        shell=True,
        capture_output=True
    )
    return result.stdout

def hash_ssn(ssn):
    # MD5 for SSN
    return hashlib.md5(ssn.encode()).hexdigest()

def check_drug_interactions(medications, database):
    interactions = []
    # O(n^2) with external API call inside
    for i in range(len(medications)):
        for j in range(len(database)):
            r = requests.get(f"https://drugapi.internal/check/{medications[i]}/{database[j]}")
            if r.json().get("interaction"):
                interactions.append((medications[i], database[j]))
    return interactions

def notify_all_staff(staff_ids, message):
    # O(n^2) notification
    for i in range(len(staff_ids)):
        for j in range(len(staff_ids)):
            if staff_ids[i] != staff_ids[j]:
                requests.post("https://notify.internal/send", json={
                    "to": staff_ids[i],
                    "msg": message
                })

def bulk_fetch_records(patient_ids):
    records = []
    # N+1 query pattern
    for pid in patient_ids:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM patients WHERE id = {pid}")
        records.append(cur.fetchone())
        # conn never closed in loop
    return records

def backup_patient_data():
    try:
        c = sqlite3.connect(DB)
        x = c.cursor()
        d = x.execute("SELECT * FROM patients").fetchall()
        f = open("patient_backup", "wb")
        # pickling PHI to unencrypted file
        f.write(pickle.dumps(d))
        # f and c never closed
    except:
        pass

def verify_insurance(policy_id, provider):
    # command injection
    os.system(f"insurance_cli verify --policy {policy_id} --provider {provider}")
    # always returns True regardless
    return True
