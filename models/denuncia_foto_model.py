from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from database import db as database


class DenunciaFoto(database.Model):
  __tablename__ = "denuncia_foto"
  ID_Denuncia_Foto = database.Column(database.Integer, primary_key = True, autoincrement=True)
  denuncia_id = database.Column(database.Integer, database.ForeignKey(
    "denuncia.ID_Denuncia",
    ondelete='CASCADE',
    onupdate='CASCADE'
  ),nullable=False)
  foto_url = database.Column(database.String(255), nullable = False)
  created_at = database.Column(database.DateTime, nullable=False)