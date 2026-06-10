from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from database import db as database
from datetime import datetime
import hashlib

from models.usuario_model import Usuario

def hash_senha(txt):
   hash_obj = hashlib.sha256(txt.encode('utf-8'))
   return hash_obj.hexdigest()

data_criacao = datetime.now()
created_at = data_criacao.strftime("%Y-%m-%d %H:%M:%S")


user_bp = Blueprint('usuario', __name__)

@user_bp.route("/usuario/login", methods=["POST"])
def login():
   data = request.json
   
   usuario = (database.session.query(Usuario).where(
      Usuario.email == data.get("email"),
      Usuario.senha_hash == hash_senha(data.get("senha_hash"))
   ).first())

   if usuario:
      return jsonify({
          "mensagem": "Usuário encontrado",
          "id": usuario.ID_Usuario
      }), 200
   else:
      return jsonify({"mensagem": "Usuário não encontrado"}), 404
   


@user_bp.route("/usuario/cadastro", methods=["GET", "POST"])
def user_register():
   data = request.json
   if request.method == "POST":
      try:
         new_user= Usuario(
         nome_completo = data.get("nome_completo"),
         cpf = data.get("cpf"),
         email = data.get("email"),
         senha_hash = hash_senha(data.get("senha_hash")),
         data_cadastro = created_at
         )

         database.session.add(new_user)
         database.session.commit()

         return jsonify({
            "mensagem": "Usuário cadastrado com sucesso."
         }), 201
      except:
         return jsonify({"mensagem": "Houve um erro, tente novamente mais tarde."}), 500

   database.session.close()


#########################
# usuario específico
@user_bp.route("/usuario/<id_usuario>", methods=["GET"])
def search_user(id_usuario):
   usuario = database.session.query(Usuario).filter_by(ID_Usuario = id_usuario).first()

   if usuario:
      database.session.close()
      return jsonify({
         "nome_completo": usuario.nome_completo,
         "cpf": usuario.cpf,
         "email": usuario.email,
         "tipo_perfil": usuario.tipo_perfil,
         "data_cadastro": usuario.data_cadastro
      }), 200
   else:
      database.session.close()
      return jsonify({"mensagem": "Usuário não encontrado!"}), 404
   
#########################
# todos usuarios
@user_bp.route("/usuarios", methods=["GET"])
def fetch_users():
   usuarios = Usuario.query.all()
   
   if usuarios:
      retorno = [{"nome_completo": usuario.nome_completo, 
               "cpf": usuario.cpf, 
               "email": usuario.email,
               "tipo_perfil": usuario.tipo_perfil,
               "data_cadastro": usuario.data_cadastro} 
              for usuario in usuarios]
      
      return jsonify(retorno), 200
   else:
      return jsonify({"Mensagem": "Não existe usuários cadastrados."}), 404



@user_bp.route("/usuarios/delete/<id_usuario>", methods=["DELETE"])
def remove_user(id_usuario):
   usuario = database.session.query(Usuario).filter_by(ID_Usuario = id_usuario).first()

   if usuario:
      try:
         database.session.delete(usuario)
         database.session.commit()
         database.session.close()

         return jsonify({"Mensagem": "Usuário deletado!"}), 200
      except:
         return jsonify({"mensagem:": "Houve um erro, tente novamente mais tarde"}), 500
   else:
      return jsonify({"Mensagem": "Usuário não encontrado!"}), 404
   

@user_bp.route("/usuarios/edit/<id_usuario>", methods=["PUT", "GET"])
def edit_user_info(id_usuario):
   data = request.json
   usuario = database.session.query(Usuario).filter_by(ID_Usuario = id_usuario).first()

   if usuario:
      try:
         usuario.nome_completo = data.get("nome_completo")
         usuario.cpf = data.get("cpf")
         usuario.email = data.get("email")
         usuario.senha_hash = hash_senha(data.get("senha_hash"))

         database.session.commit()
         database.session.close()

         return jsonify({"Mensagem": "Dados alterados!"}), 200
      except:
         return jsonify({"Mensagem": "Informe todos os campos!"}),400
      

@user_bp.route("/usuarios/edit/<id_usuario>", methods=["PATCH"])
def edit_user_info_patch(id_usuario):
   data = request.json
   usuario = database.session.query(Usuario).filter_by(ID_Usuario = id_usuario).first()
   
   if usuario:
      if "nome_completo" in data:
         usuario.nome_completo = data.get("nome_completo")

      if "cpf" in data:
         usuario.cpf = data.get("cpf")

      if "email" in data:
         usuario.email = data.get("email")

      if "senha_hash" in data:
         usuario.senha_hash = hash_senha(data.get("senha_hash"))

      database.session.commit()
      database.session.close()

      return jsonify({"Mensagem": "Dados alterados com sucesso!"}), 200
   
   else:
      return jsonify({"Mensagem": "Usuário não encontrado"}), 404
      


      
   
