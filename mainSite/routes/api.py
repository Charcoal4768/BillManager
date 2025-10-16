import sqlite3
import os
from flask import Flask, Blueprint, jsonify, request
from flask_login import current_user
from mainSite import socket, csrf
from mainSite.models import User, Store, Product, Bill, BillItem
from secrets import token_urlsafe
import datetime
from datetime import timedelta, datetime, timezone

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
    created_at = datetime.now(timezone.utc)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO publish_tokens (token, created_at) VALUES (?, ?)" , (token, created_at))
    return token

def verify_publish_token(token: str) -> bool:
    if not token:
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=EXPIRATION_MINUTES)
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
        conn.execute("INSERT INTO otp_codes (otp, email, created_at) VALUES (?, ?, ?)" , (otp, email, datetime.now(timezone.utc)))

def verify_otp(email: str, otp: str, expiry_minutes=10) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=expiry_minutes)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT id FROM otp_codes WHERE email=? AND otp=? AND created_at >= ?", (email, otp, cutoff))
        if cur.fetchone() is not None:
            conn.execute("DELETE FROM otp_codes WHERE email=? AND otp=?", (email, otp))
            return True
        return False

@api_bp.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok", "message": "API is working!"}), 200

@api_bp.route('/request_token', methods=['GET'])
def unauth_token():
    token = issue_publish_token()
    return jsonify({"publish_token": token, "status": "ok"}), 200

@api_bp.route('/get_stores', methods=['GET'])
def stores_by_user():
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "message":"User not authenticcated. Log In first."})
    stores = current_user.stores
    return jsonify({"stores":stores, "status": "ok"}), 200

@csrf.exempt
@api_bp.route('/new_store', methods=['POST'])
def add_store():
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "message":"User not authenticcated. Log In first."}), 401
    publish_token = request.form.get("publish_token")
    if not verify_publish_token(publish_token):
        return jsonify({"status": "error", "message": "Invalid or expired token."}), 403
    store_name = request.form["storeName"]
    owner = request.form["ownerName"]
    phone = request.form["phoneNum"]
    addr1 = request.form["address1"]
    addr2 = request.form["address2"]
    gstno = request.form["gstNo"]
    telcode = request.form.get("telCode", "+91")
    processStatus = "none"
    try:
        store = Store.create_store(current_user.id,store_name, email=None, phone=phone, addr=addr1+'\n'+addr2, gst_no=gstno, owner=owner, tel_code=telcode)
        processStatus = "ok"
        return jsonify({"store":store.to_dict(), "status":processStatus}), 200
    except Exception as e:
        processStatus = "error"
        return jsonify({"status":processStatus, "message":str(e)}), 500
    
@api_bp.route('/stores_paginated', methods=['GET'])
def stores_by_user_paginated():
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "message":"User not authenticated. Log In first."}), 401

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 9, type=int)

    # Correct way to get a query and paginate it
    stores_pagination = Store.query.filter_by(user_id=current_user.id).order_by(Store.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    stores_list = [store.to_dict() for store in stores_pagination.items]
    
    return jsonify({
        "stores": stores_list,
        "has_next": stores_pagination.has_next,
        "page": stores_pagination.page,
        "status": "ok"
    }), 200