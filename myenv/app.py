from flask import Flask
from db import init_db
from routes import api_bp              # existing API blueprints
from routes.pages import pages_bp      # ← NEW blueprint for HTML pages

def get_currency_symbol(code):
    symbols = {
        "INR": "Rs.",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥"
    }
    return symbols.get(code, code + " ")

def create_app():
    app = Flask(__name__)
    app.jinja_env.globals.update(get_currency_symbol=get_currency_symbol)
    app.secret_key = "change-me-to-a-random-32-char-string"
    init_db()                          # tables guaranteed
    app.register_blueprint(api_bp)     # /api/…
    app.register_blueprint(pages_bp)   # / (HTML)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
