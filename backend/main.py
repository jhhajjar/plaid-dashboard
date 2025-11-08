from routes.sync_routes import sync_bp
from routes.transaction_routes import transactions_bp
from flask_cors import CORS
from flask import Flask

app = Flask(__name__)
CORS(app)
app.register_blueprint(sync_bp, url_prefix=f"/{sync_bp.name}")
app.register_blueprint(transactions_bp, url_prefix=f"/{transactions_bp.name}")

app.run()

