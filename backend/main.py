from routes.sync_routes import sync_bp
from routes.transaction_routes import transactions_bp
from flask_cors import CORS
from flask import Flask

app = Flask(__name__)
app.register_blueprint(sync_bp)
app.register_blueprint(transactions_bp)
CORS(app)

app.run()

