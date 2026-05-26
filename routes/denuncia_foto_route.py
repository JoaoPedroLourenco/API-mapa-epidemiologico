from flask import Flask, request, jsonify, Blueprint
from database import db as database
from datetime import datetime

from models.denuncia_foto_model import DenunciaFoto
from models.denuncia_model import Denuncia

data_criacao = datetime.now()
created_at = data_criacao.strftime("%Y-%m-%d %H:%M:%S")

denuncia_foto_bp = Blueprint("denuncia_foto", __name__)



@denuncia_foto_bp.route("/denuncia/fotos/cadastro", methods=["POST", "GET"])
def include_photos():
   data = request.json

   if request.method == "POST":
      foto_url = data.get("foto_url")
      denuncia_id = data.get("denuncia_id")

      denuncia = database.session.query(Denuncia).filter_by(ID_Denuncia = denuncia_id).first()

      if denuncia:
         new_report_photo = DenunciaFoto(
         denuncia_id = denuncia_id,
         foto_url = foto_url,
         created_at = created_at
         )

         database.session.add(new_report_photo)
         database.session.commit()

         return jsonify({
            "foto_url": new_report_photo.foto_url,
            "denuncia_id": new_report_photo.denuncia_id,
            "criado em": new_report_photo.created_at
         }), 201
      else:
         return jsonify({"mensagem": "denúncia não encontrada!"}), 404
      
@denuncia_foto_bp.route("/denuncia/fotos/remover/<id>", methods=["DELETE", "GET"])
def delete_report_photo(id):
   denuncia_foto = database.session.query(DenunciaFoto).filter_by(ID_Denuncia_Foto = id).first()
   related_report = denuncia_foto.denuncia_id

   if denuncia_foto:
      if request.method == "DELETE":
         database.session.delete(denuncia_foto)
         database.session.commit()
         database.session.close()

         return jsonify({"Mensagem": f"Foto removida da denúncia de ID: {related_report} com sucesso"}), 200
   else:
      return jsonify({"Mensagem": "Foto não encontrada!"}), 404
   

@denuncia_foto_bp.route("/denuncia/foto/editar/<id>", methods=["PUT"])
def edit_report_photo(id):
   data = request.json
   denuncia_foto = database.session.query(DenunciaFoto).filter_by(ID_Denuncia_Foto = id).first()

   if denuncia_foto:
      if request.method == "PUT":
         denuncia_foto.foto_url = data.get("foto_url")

         database.session.commit()
         database.session.close()

         return jsonify({
            "Mensagem": "Alterado"
         })




@denuncia_foto_bp.route("/denuncia/foto/<id>")
def search_report_photo(id):
   denuncia_foto = database.session.query(DenunciaFoto).filter_by(ID_Denuncia_Foto = id).first()

   if denuncia_foto:
      return jsonify ({
         "ID_Denuncia_Foto": denuncia_foto.ID_Denuncia_Foto,
         "denuncia_id": denuncia_foto.denuncia_id,
         "foto_url": denuncia_foto.foto_url,
         "created_at": denuncia_foto.created_at
      })


@denuncia_foto_bp.route("/denuncia/fotos")
def get_all_report_photos():
   denuncias = DenunciaFoto.query.all()

   retorno = [{
      "foto_url": foto_denuncia.foto_url,
      "denuncia_id": foto_denuncia.denuncia_id,
      "createdAt": foto_denuncia.created_at
   } for foto_denuncia in denuncias]


   return jsonify(retorno), 200