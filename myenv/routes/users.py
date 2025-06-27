from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username, password = data.get('username'), data.get('password')
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=%s", (username,))
    if cur.fetchone():
        return jsonify({"error": "username exists"}), 409
    cur.execute("INSERT INTO users (username, password_hash) VALUES (%s,%s)",
                (username, generate_password_hash(password)))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message": "registered"}), 201

@users_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username, password = data.get('username'), data.get('password')
    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id,password_hash FROM users WHERE username=%s", (username,))
    row = cur.fetchone(); cur.close(); conn.close()
    if not row or not check_password_hash(row['password_hash'], password):
        return jsonify({"error": "invalid credentials"}), 401
    return jsonify({"message": "login success", "user_id": row['id']}), 200
