import sqlite3
import os
from flask import Flask, Blueprint, jsonify, request
from mainSite import socket
from secrets import token_urlsafe
import datetime
from datetime import timedelta

api_bp = Blueprint('api', __name__, url_prefix='/api')

DB_PATH = os.path.join(os.path.dirname(__file__), 'tokens.db')
EXPIRATION_MINUTES = 60

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS publish_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE,
            created_at DATETIME
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            otp TEXT,
            email TEXT,
            created_at DATETIME
        )''')

init_db()

def issue_publish_token():
    token = token_urlsafe(32)
    created_at = datetime.utcnow()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO publish_tokens (token, created_at) VALUES (?, ?)" , (token, created_at))
    return token

def verify_publish_token(token: str) -> bool:
    if not token:
        return False
    cutoff = datetime.utcnow() - timedelta(minutes=EXPIRATION_MINUTES)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM publish_tokens WHERE created_at < ?", (cutoff,))
        cur = conn.execute("SELECT id FROM publish_tokens WHERE token=?", (token,))
        if cur.fetchone() is not None:
            # Token is valid, now delete it
            conn.execute("DELETE FROM publish_tokens WHERE token=?", (token,))
            return True
        else:
            return False

def store_otp(email: str, otp: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO otp_codes (otp, email, created_at) VALUES (?, ?, ?)" , (otp, email, datetime.utcnow()))

def verify_otp(email: str, otp: str, expiry_minutes=10) -> bool:
    cutoff = datetime.utcnow() - timedelta(minutes=expiry_minutes)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT id FROM otp_codes WHERE email=? AND otp=? AND created_at >= ?", (email, otp, cutoff))
        if cur.fetchone() is not None:
            conn.execute("DELETE FROM otp_codes WHERE email=? AND otp=?", (email, otp))
            return True
        return False

@api_bp.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok", "message": "API is working!"}), 200

@api_bp.route('/request_token')
def unauth_token():
    token = issue_publish_token()
    return jsonify({"publish_token": token})