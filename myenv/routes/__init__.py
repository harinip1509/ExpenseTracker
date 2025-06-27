from flask import Blueprint
from .users import users_bp
from .expenses import expenses_bp

api_bp = Blueprint('api', __name__, url_prefix='/api')

# nest the blueprints
api_bp.register_blueprint(users_bp)
api_bp.register_blueprint(expenses_bp)
