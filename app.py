#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servicio web del recomendador

@author: adrim
"""

from flask import Flask
from flask import request
from recomendador import recomendacion
from Extras.diccionario_objetivos import dic_obj_tem, dic_obj_pib


app = Flask(__name__)

import warnings
warnings.filterwarnings("ignore")



@app.route('/')
def general():
	return "Hola. Recomendador para crossroads"

@app.route('/recomendacion', methods=['POST'])
def post_recomendacion():
    try:
        cuestiones_nombre = ['h1', 'h2', 'h3', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']
        data = request.get_json()
        respuestas = data['respuestas']
        objetivo_temperatura = data['objetivo_temperatura']
        objetivo_temperatura = dic_obj_tem.get(objetivo_temperatura)
        objetivo_pib = data['objetivo_pib']
        objetivo_pib = dic_obj_pib.get(objetivo_pib)
        return recomendacion(respuestas, objetivo_temperatura, objetivo_pib, solo_una_respuesta=False)
    except:
        return "Error interno en el Recomendador"
    
    
if __name__ == '__main__':
    app.run(port=5000)


