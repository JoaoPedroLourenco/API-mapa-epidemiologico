from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from database import db as database
from datetime import datetime

import requests as req

from models.denuncia_model import Denuncia
from models.usuario_model import Usuario
from models.denuncia_foto_model import DenunciaFoto

data_criacao = datetime.now()
created_at = data_criacao.strftime("%Y-%m-%d %H:%M:%S")



import os
from dotenv import load_dotenv

load_dotenv()
access_token_mapbox = os.getenv("access_token_mapbox")

denuncia_bp = Blueprint('denuncia', __name__)


#####################################
# DENUNCIAS
@denuncia_bp.route("/denuncia/registrar", methods=["POST", "GET"])
def register_report():
   data = request.json
   if request.method == "POST":
      id_usuario = data.get("usuario_id")
      usuario = database.session.query(Usuario).filter_by(ID_Usuario = id_usuario).first()
      if usuario:
         try:
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            descricao = data.get("descricao")
            foto_urls = data.get("foto_url", [])
            

            response_mapbox = req.get(f"https://api.mapbox.com/search/geocode/v6/reverse?longitude={longitude}&latitude={latitude}&access_token={access_token_mapbox}")

            info = response_mapbox.json()
            CEP = info['features'][0]['properties']['context']['postcode']['name']
            CEP_formatado = CEP.replace("-", "")

            response_viacep = req.get(f"https://viacep.com.br/ws/{CEP_formatado}/json/")
            info_viacep = response_viacep.json()

            bairro = info_viacep["bairro"]
            rua = info_viacep["logradouro"]
            
            new_report = Denuncia(
               usuario_id = id_usuario,
               latitude = latitude,
               longitude = longitude,
               rua = rua,
               bairro = bairro,
               descricao = descricao,
               status = "PENDENTE",
               data_registro = created_at,
               data_resolucao = None
            )

            database.session.add(new_report)
            database.session.flush()

            for url in foto_urls:
               new_foto = DenunciaFoto(
               denuncia_id = new_report.ID_Denuncia,
               foto_url = url
               )
               database.session.add(new_foto)

            database.session.commit()

            denuncia_fotos = database.session.query(DenunciaFoto.foto_url).join(Denuncia, Denuncia.ID_Denuncia == DenunciaFoto.denuncia_id).filter(DenunciaFoto.denuncia_id == new_report.ID_Denuncia).all()

            fotos = [foto[0] for foto in denuncia_fotos]

            return jsonify({
               "usuario": usuario.nome_completo,
               "endereco": {
                  "coordenadas": {
                     "latitude": new_report.latitude,
                     "longitude": new_report.longitude
                  },
                  "rua": new_report.rua,
                  "bairro": new_report.bairro
               },
               "imagens": fotos,
               "descricao": new_report.descricao,
               "status": new_report.status,
               "data_registro": new_report.data_registro,
               "data_resolucao": new_report.data_resolucao 
            }), 201
         except:
            return jsonify({"mensagem": "Houve um erro, tente novamente mais tarde"}), 500
      
      else:
         return jsonify({"Mensagem": "Usuário não encontrado, se cadastre ou entre em sua conta!"}), 404
      
   database.session.close()
   
@denuncia_bp.route("/denuncias", methods=["GET"])
def fetch_all_reports():
   reports = Denuncia.query.all()

   if reports:
      retorno = [{
            "usuario_id": report.usuario_id,
            "endereco": {
               "coordenadas": {
                  "latitude": report.latitude,
                  "longitude": report.longitude
               },
               "rua": report.rua,
               "bairro": report.bairro
            },
            "descricao": report.descricao,
            "status": report.status,
            "data_registro": report.data_registro,
            "data_resolucao": report.data_resolucao 
         } for report in reports]
   
   return jsonify(retorno), 200

@denuncia_bp.route("/denuncia/<id_denuncia>", methods=["GET"])
def search_report(id_denuncia):
   report = database.session.query(Denuncia).filter_by(ID_Denuncia = id_denuncia).first()

   if report:
      return jsonify({
         "usuario_id": report.usuario_id,
         "endereco": {
            "coordenadas": {
               "latitude": report.latitude,
               "longitude": report.longitude
            },
            "rua": report.rua,
            "bairro": report.bairro
         },
         "descricao": report.descricao,
         "status": report.status,
         "data_registro": report.data_registro,
         "data_resolucao": report.data_resolucao }), 200
   else:
      return jsonify({"mensagem": "Denúncia não encontrada!"}), 404


@denuncia_bp.route("/denuncia/delete/<id_denuncia>", methods=["DELETE", "GET"])
def delete_report(id_denuncia):
   denuncia = database.session.query(Denuncia).filter_by(ID_Denuncia = id_denuncia).first()

   if denuncia:
      if request.method == "DELETE":
         database.session.delete(denuncia)
         database.session.commit()

         database.session.close()

         return jsonify({"Mensagem": "Denúncia deletada com sucesso!"}), 200
   else:
      return jsonify({"mensagem": "Usuário não encontrado"}), 404
   

@denuncia_bp.route("/denuncia/edit/<id_denuncia>", methods=["PUT", "GET"])
def edit_report_put(id_denuncia):
   data = request.json
   denuncia = database.session.query(Denuncia).filter_by(ID_Denuncia = id_denuncia).first()
   denuncia_foto = database.session.query(DenunciaFoto).filter_by(denuncia_id = id_denuncia).first()

   if denuncia:
      if request.method == "PUT":
         denuncia.latitude = data.get("latitude")
         denuncia.longitude = data.get("longitude")
         denuncia.descricao = data.get("descricao")
         denuncia_foto.foto_url = data.get("foto_url")
         response_mapbox = req.get(f"https://api.mapbox.com/search/geocode/v6/reverse?longitude={denuncia.longitude}&latitude={denuncia.latitude}&types=address&access_token={access_token_mapbox}")

         info = response_mapbox.json()
         CEP = info['features'][0]['properties']['context']['postcode']['name']
         CEP_formatado = CEP.replace("-", "")

         response_viacep = req.get(f"https://viacep.com.br/ws/{CEP_formatado}/json/")
         info_viacep = response_viacep.json()

         denuncia.bairro = info_viacep["bairro"]
         denuncia.rua = info_viacep["logradouro"]

         database.session.commit()
         database.session.close()

         return jsonify({"Mensagem": "Dados alterados com sucesso!"}), 200
      
   else:
      return jsonify({"mensagem": "Denúncia não encontrado"}), 404
   

@denuncia_bp.route("/denuncia/get-location")
def get_point_location():
   latitude = request.args.get('lat', '')
   longitude = request.args.get('long', '')
   

   response_mapbox = req.get(f"https://api.mapbox.com/search/geocode/v6/reverse?longitude={longitude}&latitude={latitude}&access_token={access_token_mapbox}")

   info = response_mapbox.json()
   CEP = info['features'][0]['properties']['context']['postcode']['name']
   CEP_formatado = CEP.replace("-", "")

   response_viacep = req.get(f"https://viacep.com.br/ws/{CEP_formatado}/json/")
   info_viacep = response_viacep.json()

   bairro = info_viacep["bairro"]
   rua = info_viacep["logradouro"]
   cidade = info_viacep["localidade"]
   uf = info_viacep["uf"]

   return jsonify({
      "endereco": {
            "rua": rua,
            "bairro": bairro,
            "CEP": CEP,
            "cidade": cidade,
            "uf": uf,
            "coordenadas": {
               "latitude": latitude,
               "longitude": longitude
            },
           
         },
   })