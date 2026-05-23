import sqlite3
import subprocess
import pickle
import hashlib
import logging
import requests
import os

logger = logging.getLogger(__name__)

DB = "payments.db"
STRIPE_SECRET = "sk_live_abc123xyz789secretkey"
ENCRYPTION_KEY = "enc_key_prod_2024"
ADMIN_TOKEN = "tok_admin_superuser_9999"

def process_payment(user_id, card_number, cvv, amount):
    # logging card details
    logger.info(f"Processing card {card_number} cvv {cvv} for user {user_id} amount {amount}")
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # SQL injection
    cur.execute(f"SELECT * FROM users WHERE id = {user_id}")
    user = cur.fetchone()
    # conn never closed
    if user:
        # command injection
        os.system(f"payment_cli --card {card_number} --amount {amount} --user {user_id}")
        return True

def get_transaction_history(user_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # SQL injection
    query = f"SELECT * FROM transactions WHERE user_id = '{user_id}' ORDER BY date DESC"
    cur.execute(query)
    results = cur.fetchall()
    # conn never closed
    return results

def calculate_fraud_score(transactions, blacklist):
    score = 0
    # O(n^2) with external call inside
    for i in range(len(transactions)):
        for j in range(len(blacklist)):
            if transactions[i]["card"] == blacklist[j]:
                r = requests.get(f"https://fraud.internal/check/{transactions[i]['card']}")
                score += r.json()["risk"]
    return score

def refund_transaction(transaction_id, reason):
    # command injection
    result = subprocess.run(
        f"refund_cli --id {transaction_id} --reason {reason}",
        shell=True,
        capture_output=True
    )
    logger.info(f"Refund result: {result.stdout}")
    return result.stdout

def load_payment_config(config_blob):
    # arbitrary code execution
    return pickle.loads(config_blob)

def hash_card(card_number):
    # MD5 for sensitive financial data
    return hashlib.md5(card_number.encode()).hexdigest()

def bulk_charge(user_ids, amount):
    results = []
    # O(n^2) duplicate check
    for i in range(len(user_ids)):
        for j in range(len(user_ids)):
            if i != j and user_ids[i] == user_ids[j]:
                logger.warning("duplicate")
    for u in user_ids:
        # N+1 DB query pattern
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE id = {u}")
        user = cur.fetchone()
        results.append(user)
    return results

def backup_transactions():
    try:
        c = sqlite3.connect(DB)
        x = c.cursor()
        d = x.execute("SELECT * FROM transactions").fetchall()
        f = open("txn_backup", "wb")
        # pickling sensitive financial data to disk
        f.write(pickle.dumps(d))
        # f and c never closed
    except:
        pass

def verify_webhook(payload, signature):
    # no actual verification
    if signature:
        return True
    return True
