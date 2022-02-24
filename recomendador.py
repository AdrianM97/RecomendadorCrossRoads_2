# -*- coding: utf-8 -*-
"""
Función para realizar la recomendación 


@author: Adrian Manzano Santos
"""



import numpy as np
from collections import Counter
import pandas as pd
import json
import sys
from Extras.informacion_adicional import narrativas
import Extras.config as config





def respuestaMenor(x,y, preg=0):
    dic = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5}
    #print(preg)
    if preg=='m1' or preg=='h3':
        dic = {'a':3, 'b':4, 'c':5, 'd':1, 'e':2}
    x = dic.get(x)
    y = dic.get(y)
    return (x < y)





def recomendacion(cuestiones, temperatura_objetivo, pib_objetivo, solo_una_respuesta=True, MULT=10, error=0.1):
    MSG = ''
    hipos = 'H1'+cuestiones[0]+'H2'+cuestiones[1]+'H3'+cuestiones[2]
    cols = ['h1', 'h2', 'h3', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']
    cols=np.array(cols)
    n_cols = len(cols)
    
    plantilla_estado_obj_maestra = 'La temperatura final está <res tem> de tu objetivo. El PIB está <res pib> de tu objetivo.'
    plantilla_estado_des_maestra = 'La temperatura final <res tem>, y el PIB <res pib>.'
    plantilla_cambio_maestra = 'Para conseguir un resultado <tipo> podrías:'
    plantilla_cambio_preg = '<cambio> el valor de la <HoM> <preg> relativa a <descripcion>.'
    
    
    CL_OBJETIVO_TEM = config.CL_OBJETIVO_TEM
    CL_OBJETIVO_PIB = config.CL_OBJETIVO_PIB
    CL_PIB_IRREAL = config.CL_PIB_IRREAL
    
    
    #--------------------------------------------------------------------------
    #           LECTURA DE LOS DATOS
    #--------------------------------------------------------------------------
    ruta = 'saves'

    #LECTURA DE RESPUESTAS + CLÚSTERES
    escen = pd.read_csv(ruta+"/hipotesis_con_cluster.csv", sep=';')
    escen['Hipos'] = 'H1'+escen.h1+'H2'+escen.h2+'H3'+escen.h3

    #LECTURA DE LOS PATRONES DE TEMPERATURA Y DE PIB
    cen_tem = np.loadtxt(ruta+"/centers_tem", delimiter=';')
    cen_pib = np.loadtxt(ruta+"/centers_pib", delimiter=';')
    NC_TEM = len(cen_tem)
    NC_PIB = len(cen_pib)
    
    #LECTURA DE LA DESCRIPCIÓN DE LOS ESCENARIOS
    desc_escenDF = pd.read_csv(ruta+"/descripcion_escenarios.csv", sep=";")
    descripcion_escenario = {}
    for i in range(desc_escenDF.shape[0]):
        descripcion_escenario.update({int(desc_escenDF.loc[i,'cluster']): desc_escenDF.loc[i, 'descripcion']})
    
    
    #LECTURA DE LA DESCRIPCIÓN DE LA INFORMACIÓN MUTUA
    #info_mutua = pd.read_csv(ruta+"/informacion_mutua.csv", sep=';')
    
    

    

    
    #===============================================================================
    #===============================================================================
    #               ANÁLISIS DEL CUMPLIMIENTO DEL OBJETIVO
    #===============================================================================
    #===============================================================================
    
    #------------------------------------------------------------
    #Establecemos los clústeres válidos con el objetivo
    #------------------------------------------------------------
    
    #Clústeres con temperatura final menor o igual al objetivo 
    clusteres_tem = []
    dtem = []
    for i in range(len(cen_tem)):
        d = cen_tem[i][-1] - (1+error)*temperatura_objetivo
        if d <=0:
            clusteres_tem.append(i)
        dtem.append(d)
    clusteres_tem = np.array(clusteres_tem)
            
    #Clústeres con pib final menor o igual al objetivo 
    clusteres_pib = []
    dpib = []
    for i in range(len(cen_pib)):
        d = cen_pib[i][-1] - (1-error)*pib_objetivo
        if d>= 0:
            clusteres_pib.append(i)
        dpib.append(d)
    clusteres_pib = np.array(clusteres_pib)
        
      
    
    #----------------------------------------------------
    #Comparamos el clúster asignado con el objetivo
    #----------------------------------------------------
    
    escen_preg = escen.copy()
    for i in range(n_cols):
        escen_preg = escen_preg[escen_preg[cols[i]] == cuestiones[i]]
    cluster = int(escen_preg['cluster'])
    
    #Estado actual
    cl_tem_act = int(cluster/10)
    cl_pib_act = int(cluster-cl_tem_act*10)
    
    
    #Diferencia con los objetivos
    if len(clusteres_tem) == 0:
        dtem = -1
    else:
        dif_tem_obj = clusteres_tem - cl_tem_act
        dtem = np.min(dif_tem_obj)
        
    if len(clusteres_pib) == 0:
        dpib = -1
    else:
        dif_tem_obj = clusteres_pib - cl_pib_act
        dpib = np.min(dif_tem_obj)
    
    plantilla_estado = plantilla_estado_obj_maestra
    if   dtem == 0: plantilla_estado = plantilla_estado.replace('<res tem>', 'muy cerca')
    elif dtem == 1: plantilla_estado = plantilla_estado.replace('<res tem>', 'cerca')
    elif dtem == 2: plantilla_estado = plantilla_estado.replace('<res tem>', 'lejos')
    else:           plantilla_estado = plantilla_estado.replace('<res tem>', 'muy lejos')
        
    if   dpib == 0: plantilla_estado = plantilla_estado.replace('<res pib>', 'muy cerca')
    elif dpib == 1: plantilla_estado = plantilla_estado.replace('<res pib>', 'cerca')
    elif dpib == 2: plantilla_estado = plantilla_estado.replace('<res pib>', 'lejos')
    else:           plantilla_estado = plantilla_estado.replace('<res pib>', 'muy lejos')
    
    if dtem == 0 and dpib == 0: plantilla_estado += " ENHORABUENA, lograste tu objetivo."
    
    MSG += plantilla_estado 
    
    #DESCRIPCIÓN DEL ESCENARIO
    MSG +='\n\n'
    MSG += descripcion_escenario.get(cluster) #Añadimos la descripción del escenario
       
    
        
    #===============================================================================
    #===============================================================================
    #               RESULTADOS MEDIOAMBIENTALES Y RECOMENDACION
    #===============================================================================
    #===============================================================================        
    clusteres_objetivo = []
    for ctem in CL_OBJETIVO_TEM:
        for cpib in CL_OBJETIVO_PIB:
            clusteres_objetivo.append(ctem*MULT+cpib)
    
    
    escen_preg = escen.copy()
    
#    print('Cluster asignado:' + str(cluster))
#    print('------------------------------------')
    
    #ACIERTO --> ENORABUENA Y FIN
    if cluster in clusteres_objetivo:
        plantilla_estado = plantilla_estado_des_maestra
        plantilla_estado = plantilla_estado.replace('<res tem>', 'es adecuada')
        plantilla_estado = plantilla_estado.replace('<res pib>', 'es aceptable')
        MSG +='\n\n'
        MSG += plantilla_estado 
        MSG += '\nENHORABUENA'
        return MSG
    
    
    #FALLO EN EL CLUSTER
    #----------------------------------------------
    #Comparamos y generamos el mensaje de estado
    #----------------------------------------------
    
    #Estado actual
    cl_tem_act = int(cluster/10)
    cl_pib_act = int(cluster-cl_tem_act*10)
    
    #Diferencia con los clusteres adecuados
    clusteres_tem = np.array(CL_OBJETIVO_TEM)
    dif_tem_obj = clusteres_tem - cl_tem_act
    dtem = np.min(dif_tem_obj)
    
    clusteres_pib = CL_OBJETIVO_PIB + CL_PIB_IRREAL
    clusteres_pib = np.array(clusteres_pib)
    dif_pib_obj = clusteres_pib - cl_pib_act
    dpib = np.min(dif_pib_obj)
    
    
    #Comentario del escenario
    plantilla_estado = plantilla_estado_des_maestra
    if   dtem == 0: plantilla_estado = plantilla_estado.replace('<res tem>', 'es adecuada')
    elif dtem == 1: plantilla_estado = plantilla_estado.replace('<res tem>', 'es elevada')
    elif dtem == 2: plantilla_estado = plantilla_estado.replace('<res tem>', 'es muy elevada')
    else:           plantilla_estado = plantilla_estado.replace('<res tem>', 'es inviable para la vida')
        
    if   dpib == 0: plantilla_estado = plantilla_estado.replace('<res pib>', 'es adecuado')
    elif dpib == 1: plantilla_estado = plantilla_estado.replace('<res pib>', 'es bajo')
    elif dpib == 2: plantilla_estado = plantilla_estado.replace('<res pib>', 'es muy bajo')
    else:           plantilla_estado = plantilla_estado.replace('<res pib>', 'se hunde completamente')
    
    MSG +='\n\n'
    MSG += plantilla_estado 
    
    #Preparamos la recomendación según el escenario de PIB y temperatura
    if cl_pib_act in CL_PIB_IRREAL: #PIB disparado e irreal
        if cl_tem_act in CL_OBJETIVO_TEM:
            plantilla_cambio_maestra = plantilla_cambio_maestra.replace('<tipo>', 'con niveles económicos más realistas')
        else:
            plantilla_cambio_maestra = plantilla_cambio_maestra.replace('<tipo>', 'con niveles económicos más realista y respetuoso con el medio ambiente')
    elif cl_pib_act not in CL_OBJETIVO_PIB: #PIB que se unde
        if cl_tem_act in CL_OBJETIVO_TEM:
            plantilla_cambio_maestra = plantilla_cambio_maestra.replace('<tipo>', 'económicamente más equilibrado')
        else:
            plantilla_cambio_maestra = plantilla_cambio_maestra.replace('<tipo>', 'económicamente más equilibrado y respetuoso con el medio ambiente')
    else: #PIB adecuado con mala temperatura
        plantilla_cambio_maestra = plantilla_cambio_maestra.replace('<tipo>', 'más respetuoso con el medio ambiente')
    
    MSG += " " + plantilla_cambio_maestra
    MSG +="\n" 
    
        
    #----------------------------------------
    #RECOMENDACIÓN
    #----------------------------------------
    
    
    #Nos quedamos con los candidatos que esten en el clúster objetivo
    escen_case = escen[escen.cluster.isin(clusteres_objetivo)]
    
    #Miramos si es posible alcanzar ese escenario sin variar las hipótesis
    cambio_h='no'
    escen_hip = escen_case[escen_case.Hipos == hipos]
    #print(escen_hip)
    if escen_hip.shape[0] == 0:
        escen_hip = escen_case
        MSG += ' Se requiere un cambio en las hipótesis para alcanzar el objetivo.'
        cambio_h='si'
        
    
    def n_preg_cambio(x,y=cuestiones):
        x = np.array(x)
        y = np.array(y)
        return len(np.where(x!=y)[0])
    
    def dif_entre_preguntas(x,y=cuestiones):
        dic = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5}
        x = np.array([dic.get(x[i]) for i in range(len(x))])
        y = np.array([dic.get(y[i]) for i in range(len(y))])
        
        return np.sum(np.abs(x-y))
    
    escen_hip['distancia'] = escen_hip[cols].apply(n_preg_cambio, axis=1)
    escen_hip = escen_hip[escen_hip.distancia == np.min(escen_hip.distancia)]
    escen_hip['diferencia'] = escen_hip[cols].apply(dif_entre_preguntas, axis=1)
    escen_hip = escen_hip[escen_hip.diferencia == np.min(escen_hip.diferencia)].reset_index(drop=True)
    escen_hip = escen_hip.sort_values(by='cluster', ascending=False).reset_index(drop=True)
    
    respuestas_finales = escen_hip.loc[0][cols].to_list()
    
    #    cols_orden = info_mutua[info_mutua.cluster==cluster].\
    #             sort_values(by='info_mutua', ascending=False).\
    #             reset_index(drop=True).pregunta.to_list()
    
    for i in range(len(respuestas_finales)):
        n_preg = i
        plantilla_cambio = plantilla_cambio_preg
        cuestion = cuestiones[n_preg] 
        cambio = respuestas_finales[n_preg]
        if cuestion != cambio:
            if respuestaMenor(cuestion,cambio, cols[i]):
                plantilla_cambio = plantilla_cambio.replace('<cambio>', '- Subir')
            else:
                plantilla_cambio = plantilla_cambio.replace('<cambio>', '- Bajar')
            
            preg = cols[i]
            if 'h' in preg:
                    plantilla_cambio = plantilla_cambio.replace('<HoM>', 'hipótesis')
            else:
                plantilla_cambio = plantilla_cambio.replace('<HoM>', 'medida')
            plantilla_cambio = plantilla_cambio.replace('<preg>', preg)  
            plantilla_cambio = plantilla_cambio.replace('<descripcion>', '\"' + narrativas.get(preg.upper()) + '\"')
            MSG += plantilla_cambio
            MSG += '\n'
            
            #print(preg + ' ' + cuestion +' => ' + cambio)
            if solo_una_respuesta:
                break
		    

    return MSG
