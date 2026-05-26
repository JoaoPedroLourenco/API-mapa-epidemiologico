from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from database import db as database


class Denuncia(database.Model):
  __tablename__ = "denuncia"
  ID_Denuncia = database.Column(database.Integer, primary_key = True, autoincrement=True)
  usuario_id = database.Column(database.Integer, database.ForeignKey(
    'usuario.ID_Usuario',
    ondelete='RESTRICT',
    onupdate='CASCADE'
  ),nullable=False)
  latitude = database.Column(database.Numeric(10,8), nullable=False)
  longitude = database.Column(database.Numeric(11,8), nullable=False)
  rua = database.Column(database.String(150), nullable=False)
  bairro = database.Column(database.String(100), nullable=False)

  descricao = database.Column(database.Text, nullable=False)

  status = database.Column(
      database.Enum('PENDENTE', 'EM_ANALISE', 'RESOLVIDO', name='status_enum'),
      nullable=False,
      default='PENDENTE'
  )

  data_registro = database.Column(
      database.DateTime,
      nullable=False
  )

  data_resolucao = database.Column(
      database.DateTime,
      nullable=True
  )