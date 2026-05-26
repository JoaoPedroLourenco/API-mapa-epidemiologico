from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from database import db as database
import hashlib
from enum import Enum
from datetime import datetime


class Usuario(database.Model):
  __tablename__ = 'usuario'
  ID_Usuario = database.Column(database.Integer, primary_key = True, autoincrement=True)
  nome_completo = database.Column(database.String(150), nullable=False)
  cpf = database.Column(database.String(11), nullable=False, unique=True)
  email = database.Column(database.String(100), nullable=False, unique=True)
  senha_hash = database.Column(database.String(255), nullable=False)
  tipo_perfil = database.Column(database.Enum("MUNICIPE", "ADMIN_SAUDE", name='status_enum'), default= "MUNICIPE", nullable=False)
  data_cadastro = database.Column(database.DateTime, nullable=False, default= datetime.now())

  def __repr__(self):
    return f"{self.nome_completo}, {self.cpf}, {self.email}, {self.senha_hash}, {self.tipo_perfil} - {self.data_cadastro}"