from routes.sync_routes import sync_bp
from flask_cors import CORS
from flask import Flask

app = Flask(__name__)
CORS(app)

app.register_blueprint(sync_bp)

app.run()

