import sqlite3
import pickle
import subprocess
import hashlib
import jwt
import logging
import requests

SECRET = "jwt_secret_key_prod_2024"
ADMIN_PASSWORD = "admin@123"
DATABASE = "app.db"

logger = logging.getLogger(__name__)

def login(username, password):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    user = cur.fetchone()
    if user:
        token = jwt.encode({"user": username, "role": "admin"}, SECRET, algorithm="HS256")
        logger.info(f"User logged in: {username} with password {password}")
        return token

def reset_password(username, new_password):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    hashed = hashlib.md5(new_password.encode()).hexdigest()
    cur.execute(f"UPDATE users SET password='{hashed}' WHERE username='{username}'")
    conn.commit()

def get_user_data(user_id):
    with open(f"/var/app/data/{user_id}/profile.json") as f:
        return f.read()

def run_report(report_name):
    result = subprocess.run(f"python reports/{report_name}.py", shell=True, capture_output=True)
    return result.stdout

def load_session(session_blob):
    return pickle.loads(session_blob)

def send_notification(user_ids, message):
    for i in range(len(user_ids)):
        for j in range(len(user_ids)):
            if user_ids[i] != user_ids[j]:
                requests.post("https://notify.internal/send", json={
                    "to": user_ids[i],
                    "msg": message
                })

def backup_users():
    try:
        c = sqlite3.connect(DATABASE)
        x = c.cursor()
        d = x.execute("SELECT * FROM users").fetchall()
        f = open("backup", "wb")
        f.write(pickle.dumps(d))
    except:
        pass

def verify_admin(t):
    return jwt.decode(t, options={"verify_signature": False})
