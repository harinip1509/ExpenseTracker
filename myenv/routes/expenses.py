from flask import Blueprint, request, jsonify
from db import get_db_connection
from utils.helpers import calculate_total, filter_by_category

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@expenses_bp.route('/', methods=['POST'])
def add_expense():
    data = request.get_json()
    required = ('description','amount','category','user_id')
    if not all(k in data for k in required):
        return jsonify({"error":"missing fields"}),400
    conn=get_db_connection();cur=conn.cursor()
    cur.execute("""INSERT INTO expenses (description,amount,category,user_id)
                   VALUES (%s,%s,%s,%s)""",
                (data['description'],data['amount'],data['category'],data['user_id']))
    conn.commit();cur.close();conn.close()
    return jsonify({"message":"expense added"}),201

@expenses_bp.route('/<int:user_id>', methods=['GET'])
def list_expenses(user_id):
    category=request.args.get('category')
    conn=get_db_connection();cur=conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM expenses WHERE user_id=%s",(user_id,))
    rows=cur.fetchall();cur.close();conn.close()
    if category: rows=filter_by_category(rows,category)
    return jsonify({"total":calculate_total(rows),"expenses":rows}),200

@expenses_bp.route('/<int:exp_id>', methods=['PUT'])
def update_expense(exp_id):
    data=request.get_json()
    allowed={k:v for k,v in data.items() if k in ('description','amount','category')}
    if not allowed: return jsonify({"error":"nothing to update"}),400
    sets=", ".join(f"{k}=%s" for k in allowed)
    conn=get_db_connection();cur=conn.cursor()
    cur.execute(f"UPDATE expenses SET {sets} WHERE id=%s",
                list(allowed.values())+[exp_id])
    conn.commit();cur.close();conn.close()
    return jsonify({"message":"updated"}),200

@expenses_bp.route('/<int:exp_id>', methods=['DELETE'])
def delete_expense(exp_id):
    conn=get_db_connection();cur=conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=%s",(exp_id,))
    conn.commit();cur.close();conn.close()
    return jsonify({"message":"deleted"}),200
