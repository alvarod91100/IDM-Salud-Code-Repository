# FUNCIONES PARA GENERACIÓN DE DATOS
import random
import string
import numpy as np
import pandas as pd
import random as rn
from datetime import datetime, timedelta
from sqlalchemy import text

# GENERACIÓN DE CLIENTES
def generate_client_data(num_rows: int, engine, nombres_hombres, nombres_mujeres, apellidos, ciudades, estados, codigos_postales, preguntas_seguridad, respuestas_de_seguridad):
    """ Funcion para generar datos de clientes simulados y ejecutar su inserción en la base de datos.

    Args:
        num_rows (int): _description_
        engine: objeto sqlalchemy engine conectado a la base de datos
        nombres_hombres (list): lista de strings de nombres de hombres para su selección aleatoria
        nombres_mujeres (list): lista de strings de nombres de mujeres para su selección aleatoria
        apellidos (list): lista de strings de apellidos para su selección aleatoria
        ciudades (list): lista de strings de ciudades para su selección aleatoria
        estados (list): lista de strings de estados para su selección aleatoria
        codigos_postales (list): lista de strings de códigos postales para su selección aleatoria
        preguntas_seguridad (list): lista de strings de preguntas de seguridad para su selección aleatoria
        respuestas_de_seguridad (list): lista de strings de respuestas de seguridad para su selección aleatoria
    """
    
    data = []
    for i in range(num_rows):
        nombre = random.choice(nombres_mujeres+nombres_hombres)
        apellido_paterno = random.choice(apellidos)
        apellido_materno = random.choice(apellidos)
        genero = "Masculino" if nombre in nombres_hombres else "Femenino"
        correo = f"{nombre.lower()}.{apellido_paterno.lower()}{random.randint(0,100)}@gmail.com"
        telefono = random.randint(1000000000, 9999999999)
        ciudad = random.choice(ciudades)
        estado = estados[ciudades.index(ciudad)]
        codigo_postal = codigos_postales[ciudades.index(ciudad)]
        a_nacimiento = random.randint(1930, 1960)
        pregunta_seguridad = random.choice(preguntas_seguridad)
        respuesta_seguridad = respuestas_de_seguridad[preguntas_seguridad.index(pregunta_seguridad)] + ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=3))
        contrasena=  ''.join(rn.choices(string.ascii_uppercase +
                             string.digits, k=8))
        
        
        clause= "INSERT INTO proyecto_salud.clientes (nombre, apellido_paterno, apellido_materno, contrasena, genero, telefono, correo, ciudad, estado, codigo_postal, a_nacimiento, pregunta_seguridad, respuesta_pregunta_seguridad)\nVALUES "
        row = f"('{nombre}', '{apellido_paterno}', '{apellido_materno}','{contrasena}', '{genero}', {telefono}, '{correo}', '{ciudad}', '{estado}', {codigo_postal}, {a_nacimiento}, {pregunta_seguridad}, '{respuesta_seguridad}')"
        complete_query= clause + row + ";"    
        #print("Running Query:\n", complete_query)
        sql = text(complete_query);
        results = engine.execute(sql);
        print("Adding row ", i, end="\r")
        
# GENERACIÓN DE VITALES
def generar_vitales(normal_med_dict:dict, diabetes_med_dict:dict, hypertension_med_dict:dict,cantidad_lecturas: int , data_clientes: pd.DataFrame, data_padecimientos:pd.DataFrame, dict_padecimientos:dict,sqlalchemy_engine, vitales_current_ids_list= None, fecha_inicial_lecturas= '01/04/2023', days_delta_max= 90, client_list= None, ids_sucursales = [1,2,3], noise_factor_height= 0.0001, noise_factor_weight= 0.02):
    """ Funcion para simular lecturas de medidas fisiologicas y ejecutar su inserción en la base de datos.
    
    Args:
        normal_med_dict (dict): diccionario conteniendo las medias y desviaciones estandar de cada medicion que se simular a para las personas sin diabetes ni hipertension.
        diabetes_med_dict (dict): diccionario conteniendo las medias y desviaciones estandar de cada medicion que se simular a para las personas con diabetes tipo 2.
        hypertension_med_dict (dict): diccionario conteniendo las medias y desviaciones estandar de cada medicion que se simular a para las personas con hipertension.
        cantidad_lecturas (int): cantidad de lecturas que se generaran por cliente.
        data_clientes (pd.DataFrame): DataFrame que contiene todo id cliente en la base de datos actualmente y su g enero respectivo. Se debe obtener mediante una consulta de la tabla clientes utilizando SQL.
        data_padecimientos (pd.DataFrame): DataFrame que contiene todo id_cliente en la base de datos actualmente y sus id_padecimiento actuales respectivos. Se debe obtener mediante una consulta de la tabla padecimientos_cliente utilizando SQL.
        dict_padecimientos (dict): diccionario que contiene la signación de nombres de los padecimientos para cada id_padecimiento en data_padecimientos.
        sqlalchemy_engine: objeto sqlalchemy engine conectado a la base de datos
        vitales_current_ids_list (list, optional): lista de los id_lectura actualmente en la tabla. Predeterminado: None.
        fecha_inicial_lecturas (str, optional):fecha minima que puede aparecer en las las lecturas simuladas. Predeterminado: '01/04/2023'.
        days_delta_max (int, optional): diferencia de dias maxima que pueden tener las fechas simuladas respecto a fecha_inicial_lecturas. Predeterminado: 90.
        client_list (list, optional): lista de los id_cliente de los cuales se quiere generar las simulaciones. Predeterminado: None.
        ids_sucursales (list, optional): lista de los id_local que se quiere que puedan aparecer en las simulaciones de las lecturas. Predeterminado: [1,2,3].
        noise_factor_height (float, optional): variables para determinar la magnitud de los cambios que cada paciente puede presentar entre visitas para la variable de altura. Predeterminado: 0.0001.
        noise_factor_weight (float, optional): variables para determinar la magnitud de los cambios que cada paciente puede presentar entre visitas para la variable de peso. Defaults to 0.02.
        """
    
    lista_peso_df= []
    lista_altura_df= []
    lista_bmi_df=[]
    for i in range(data_clientes.shape[0]):
        cliente_padecimientos_actuales= data_padecimientos[data_padecimientos["id_cliente"]==data_clientes.iloc[i,0]]["id_padecimiento"].tolist()
        
        if data_clientes.iloc[i,1] == "Masculino":
            altura= np.round(np.random.normal(normal_med_dict["height"]["hombre"][0], normal_med_dict["height"]["hombre"][1], 1)[0],2)
            weight= np.round(np.random.normal(normal_med_dict["weight"]["hombre"][0], normal_med_dict["weight"]["hombre"][1], 1)[0],2)
        else: 
            altura= np.round(np.random.normal(normal_med_dict["height"]["mujer"][0], normal_med_dict["height"]["mujer"][1], 1)[0],2)
            weight= np.round(np.random.normal(normal_med_dict["weight"]["mujer"][0], normal_med_dict["weight"]["mujer"][1], 1)[0],2)

        if dict_padecimientos["Diabetes tipo 2"] in cliente_padecimientos_actuales:
            bmi= np.round(np.random.normal(diabetes_med_dict["bmi"][0], diabetes_med_dict["bmi"][1], 1)[0],1)
            lista_peso_df.append(np.round(bmi*(altura**2),1))
        elif dict_padecimientos["Hipertension"] in cliente_padecimientos_actuales:
            bmi= np.round(np.random.normal(hypertension_med_dict["bmi"][0], hypertension_med_dict["bmi"][0]/3, 1)[0],1)
            lista_peso_df.append(np.round(bmi*(altura**2),1))
        else: 
            bmi= np.round(weight/(altura**2), 1)
            lista_peso_df.append(np.round(weight,1))

        lista_bmi_df.append(bmi)
        lista_altura_df.append(altura)

    data_clientes["peso"]= lista_peso_df
    data_clientes["altura"]= lista_altura_df
    data_clientes["bmi"]= lista_bmi_df


    
    ids= data_clientes["id_cliente"].unique().tolist()
    id_max_lecturas_actuales= np.max(vitales_current_ids_list)
    
    if pd.isnull(id_max_lecturas_actuales):
        id_max_lecturas_actuales=0
    
    for cliente in range(1,cantidad_lecturas+1):
        print("Generando Lectura ", cliente, end="\r")
        #cliente_id
        if client_list is None:
            client_id= random.choice(ids)
        else: 
            client_id= random.choice(client_list)  

        cliente_padecimientos_actuales= data_padecimientos[data_padecimientos["id_cliente"]==client_id]["id_padecimiento"].tolist()

        if dict_padecimientos["Diabetes tipo 2"] in cliente_padecimientos_actuales:
            spo2= np.round(np.random.normal(diabetes_med_dict["spo2"][0], diabetes_med_dict["spo2"][1], 1)[0],0)
            if spo2>100:
                spo2=100
            bpm= np.round(np.random.normal(diabetes_med_dict["bpm"][0], diabetes_med_dict["bpm"][1], 1)[0],0)
            pres_sist= np.round(np.random.normal(diabetes_med_dict["pres_sist"][0], diabetes_med_dict["pres_sist"][1], 1)[0],0)
            pres_diast= np.round(np.random.normal(diabetes_med_dict["pres_diast"][0], diabetes_med_dict["pres_diast"][1], 1)[0],0)
            br= np.round(np.random.normal(diabetes_med_dict["br"][0], diabetes_med_dict["br"][1], 1)[0])
            lista_peso_df.append(np.round(bmi*(altura**2),1))



        elif dict_padecimientos["Hipertension"] in cliente_padecimientos_actuales:
            spo2= np.round(np.random.normal(hypertension_med_dict["spo2"][0], hypertension_med_dict["spo2"][1], 1)[0],0)
            if spo2>100:
                spo2=100
            bpm= np.round(np.random.normal(hypertension_med_dict["bpm"][0], hypertension_med_dict["bpm"][1], 1)[0],0)
            pres_sist= np.round(np.random.normal(hypertension_med_dict["pres_sist"][0], hypertension_med_dict["pres_sist"][1], 1)[0],0)
            pres_diast= np.round(np.random.normal(hypertension_med_dict["pres_diast"][0], hypertension_med_dict["pres_diast"][1], 1)[0],0)
            br= np.round(np.random.normal(hypertension_med_dict["br"][0], hypertension_med_dict["br"][1], 1)[0])
            lista_peso_df.append(np.round(bmi*(altura**2),1))
        
        else: 
            spo2= np.round(np.random.normal(normal_med_dict["spo2"][0], normal_med_dict["spo2"][1], 1)[0],0)
            if spo2>100:
                spo2=100
            bpm= np.round(np.random.normal(normal_med_dict["bpm"][0], normal_med_dict["bpm"][1], 1)[0],0)
            pres_sist= np.round(np.random.normal(normal_med_dict["pres_sist"][0], normal_med_dict["pres_sist"][1], 1)[0],0)
            pres_diast= np.round(np.random.normal(normal_med_dict["pres_diast"][0], normal_med_dict["pres_diast"][1], 1)[0],0)
            br= np.round(np.random.normal(normal_med_dict["br"][0], normal_med_dict["br"][1], 1)[0])
            lista_peso_df.append(np.round(weight,1))
            
        #id_lectura
        id_lectura= id_max_lecturas_actuales+cliente
        #saturacion_ox
        saturacion_ox= int(spo2)
        #Altura 
        altura= np.round(data_clientes[data_clientes["id_cliente"]==client_id]["altura"].tolist()[0] + rn.randrange(-100, 100,step=1)*noise_factor_height, 2)
        #Peso 
        peso= np.round(data_clientes[data_clientes["id_cliente"]==client_id]["peso"].tolist()[0] + rn.randrange(-100, 100,step=1)*noise_factor_weight, 2)
        #Recalculo de BMI
        bmi= np.round(peso/altura**2, 1)
        #Temperatura
        temp= np.random.normal(36.6, 0.6, 1)[0].round(1)
        # Presion Sistolica
        pres_sist=  int(pres_sist)
        # Presion Diastolica
        pres_diast= int(pres_diast)
        # Fecha de registro
        start_date = datetime.strptime(fecha_inicial_lecturas, '%d/%m/%Y')
        end_date = start_date + timedelta(days=rn.choice(list(range(0, days_delta_max+1))))
        random_date = start_date + (end_date - start_date)*random.random()
        random_date="'"+ datetime.strftime(random_date, '%Y/%m/%d %H:%M:%S') + "'"
        # ID del local
        id_local= random.choice(ids_sucursales)
        bpm= int(bpm)
        # Frecuencia respiratoria
        breath_rate= int(br)
        
        list_values= [id_lectura,client_id, id_local, bpm, breath_rate, peso, bmi, saturacion_ox, temp, pres_sist, pres_diast, altura, random_date]
        string_values= ",".join([str(item) for item in list_values])
        string_values= "("+string_values+");"
        insert_str= "INSERT INTO vitales (id_lectura, id_cliente,id_sucursal,ritmo_cardiaco,frecuencia_respiratoria,peso,indice_masa_corporal,saturacion_oxigeno,temperatura,presion_sanguinea_sistolica,presion_sanguinea_diastolica,altura,date_time) VALUES "
        query= insert_str+string_values
        #print(query)
        sql = text(query);
        engine= sqlalchemy_engine
        results = engine.execute(sql);
        


# GENERACION DE PADECIMIENTOS DE CLIENTES
def generar_padecimientos(lista_clientes: list, diseases_dict: dict, average_diseases: float, std_dev_diseases: float, diabetes_prob: float, hypertension_prob: float, engine):
    """ Funcion que genera padecimientos para cada cliente de la lista de clientes y los inserta en la tabla padecimientos.
    
    Args:
        lista_clientes (list): listado de los identificadores de clientes a los cuales se les desea simular la presencia de padecimientos. Se pretende que esta lista tenga los identificadores de los clientes que no tengan presencia alguna en la tabla padecimientos_cliente, para evitar filas duplicados en ella.
        diseases_dict (dict): diccionario originado de la extracción de todas las filas presentes en la tabla padecimientos_clientes antes de la ejecución de la función. Esto es para considerar qué padecimientos ya tiene cada cliente.
        average_diseases (float): valor que representa a la media de cantidad de padecimientos que se generarán a cada cliente.
        std_dev_diseases (float): valor que representa a la desviación estándar de cantidad de padecimientos que se generarán a cada cliente.
        diabetes_prob (float): probabilidad de que un paciente tenga diabetes tipo 2.
        hypertension_prob (float): probabilidad de que un paciente tenga hipertensión.
        engine: motor de conexión hacia la base de datos para ejecutar consultas de SQL.
    """
    
    clientes= lista_clientes
    start_id = np.min(clientes)
    diseases = list(diseases_dict.values())
    disease_avg = average_diseases  # Average number of diseases per client
    disease_std_dev = std_dev_diseases  # Standard deviation of the number of diseases per client

    # Generacion
    client_data = []
    for client_id in clientes:
        client_diseases_d_or_h=[]
        has_diabetes= rn.choices([True, False], weights = [diabetes_prob, 1-diabetes_prob], k=1)[0]
        has_hypertension= rn.choices([True, False], weights=[ hypertension_prob, 1-hypertension_prob], k=1)[0]

        if has_diabetes: 
            client_diseases_d_or_h.append(diseases_dict['Diabetes tipo 2'])
        if not has_diabetes:
            if has_hypertension:
                client_diseases_d_or_h.append(diseases_dict["Hipertension"])
                    
        num_diseases = round(random.normalvariate(disease_avg, disease_std_dev))
        num_diseases = max(0, min(len(diseases), num_diseases))
        
        if has_diabetes or has_hypertension:
            num_diseases= num_diseases-1
        
        client_diseases = random.sample(diseases, num_diseases)
        client_data.append((client_id, client_diseases_d_or_h + client_diseases))
        #agregar prevalencia de diabetes e hipertension
        # hacer que, por ahora, sean excluyentes

    # Query SQL 
    query = "INSERT INTO proyecto_salud.padecimientos_cliente (id_cliente, id_padecimiento) VALUES\n"
    values = []
    for client_id, client_diseases in client_data:
        for disease in client_diseases:
            values.append(f"({client_id}, {disease})")
    query += ",\n".join(values)
    #print(query)
    sql = text(query)
    results = engine.execute(sql);
