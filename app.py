from flask import Flask
from flask_cors import CORS


from database import db as database

from routes.usuario_route import user_bp
from routes.denuncia_route import denuncia_bp
from routes.denuncia_foto_route import denuncia_foto_bp

app = Flask(__name__)

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SQL_URI = os.getenv("SQL_URI")


app.config["SQLALCHEMY_DATABASE_URI"] = SQL_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

database.init_app(app)

CORS(app)
app.json.sort_keys = False

app.register_blueprint(user_bp)
app.register_blueprint(denuncia_bp)
app.register_blueprint(denuncia_foto_bp)


if __name__ == '__main__':
  with app.app_context():
    database.create_all()
  app.run(host='0.0.0.0', debug=True)