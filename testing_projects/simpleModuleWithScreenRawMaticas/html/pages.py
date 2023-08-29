import gc
from utils.metrics import Metrics
from modules.initialize_database import db_mod
update_config="""<!DOCTYPE html><html lang="en"><head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <link href="https://templatemo.com/tm-style-20210719c.css" rel="stylesheet"> <title>Maticas linea decoración - Modulo 0</title> </head> <body> <div class="form-container"><h1>Maticas linea decoración</h1><h3>Modulo 0</h3><hr><form action="/update" method="post"><table><tr><td><label for="nombre-actuador">Nombre de actuador</label><input type="text" id="nombre-actuador" name="name"></td></tr><tr><td><label for="hora-inicio">Hora de inicio</label><input type="time" step="1" id="hora-inicio" name="starttime"></td></tr><tr><td><label for="hora-fin">Hora de fin</label><input type="time" step="1" id="hora-fin" name="endtime"></td></tr><tr><td><label for="tipo-actuador">Tipo de actuador</label><select id="tipo-actuador" name="type" onchange="toggleTiempoFields()"><option value="timed" selected>Temporizado</option><option value="on/off">On/Off</option></select></td></tr><tr id="minuteson-help-row"><td><br><i>El número de minutos de encendido y apagado debe ser mayor a cero. Se permiten números decimales. Si no se selecciona "Temporizado", la configuración de encendido y apagado se ignorará.</i></td></tr><tr id="minuteson-row"><td><label for="minuteson">¿Cuántos minutos encendido?</label><input type="number" id="minuteson" name="minuteson" min="1.0" step="any"></td></tr><tr id="-row"><td><label for="minutesoff">¿Cuántos minutos apagado?</label><input type="number" id="minutesoff" name="minutesoff" min="1.0" step="any"></td></tr></table><br><input type="submit" value="Guardar"></form></div></body></html>"""
def get_config(config_file:str)->dict:
	import ujson
	from utils.time_management_module import Time
	with open(config_file,"r")as f:
		config=ujson.load(f)
		config=config["actuators"]["0"]
		config["starttime"]=Time(*config["starttime"])
		config["endtime"]=Time(*config["endtime"])
	gc.collect()
	return config
def show_config(config_file:str)->str:
	config=get_config(config_file)
	if config["type"]=="timed":
		display="""<div class="container"><p>El actuador <strong>'{name}'</strong> opera desde las <strong>{starttime}</strong> horas del día hasta las <strong>{endtime}</strong> horas del día. Es temporizado, se enciende durante <strong>{minuteson} Minutos</strong> y descansa durante <strong>{minutesoff} Minutos</strong>.</p></div>""".format(**config)
	else:
		display="""<div class="container"><p>El actuador <strong>'{name}'</strong> opera desde las <strong>{starttime}</strong> horas del día hasta las <strong>{endtime}</strong> horas del día. No es temporizado.</p></div>""".format(**config)
	gc.collect()
	return """<!DOCTYPE html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><link href="https://templatemo.com/tm-style-20210719c.css" rel="stylesheet"><style>body {font-family: Arial, sans-serif; margin: 0; padding: 20px;} .container {max-width: 600px; margin: 0 auto;border: 1px solid #ccc;padding: 20px;border-radius: 5px;box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);}.button-container {margin-top: 20px;}.update-button {background-color: #007bff;color: #fff;border: none;padding: 10px 20px;border-radius: 5px;cursor: pointer;}</style><title>Información del módulo</title></head><body>"""+"""{}""".format(display)+"""<br><br><div style="text-align:center"><button class="update-button" onclick="redirectToUpdateConfig()">Modificar configuración</button><br><br><button class="update-button" onclick="redirectToMeasurements()">Ver mediciones</button></div><script>function redirectToUpdateConfig() {window.location.href = '/updateConfig';}function redirectToMeasurements() {window.location.href = '/measurements';}</script></body></html>"""
def show_measurements():
	temp_register=db_mod.get_register("0")
	hum_register=db_mod.get_register("1")
	last_temp=temp_register.get_latest_measurement()
	last_hum=hum_register.get_latest_measurement()
	averageTemperatureData="""<script> const averageTemperatureData = ["""
	for i in range(1,4):
		avg=Metrics.get_average(temp_register.nth_hour_generator(i))
		averageTemperatureData+='{'
		averageTemperatureData+='value: {}, label: " Temperatura promedio en la hora {} de funcionamiento: ", valueId: "average-last-{}-hour"'.format(avg,i,i)
		averageTemperatureData+='},'
	averageTemperatureData+="""];"""
	averageHumidiyData="""const averageHumidityData = ["""
	for i in range(1,4):
		avg=Metrics.get_average(hum_register.nth_hour_generator(i))
		averageHumidiyData+='{'
		averageHumidiyData+='value: {}, label: " Humedad promedio en la hora {} de funcionamiento: ", valueId: "average-last-{}-hour"'.format(avg,i,i)
		averageHumidiyData+='},'
	averageHumidiyData+="""];"""
	gc.collect()
	response="""<!DOCTYPE HTML><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous"><style>html {font-family: Arial;display: inline-block;margin: 0px auto;text-align: center;}h2 {font-size: 3.0rem;}p{font-size: 3.0rem;} .units{font-size: 1.5rem;} .ds-labels {font-size: 1.5rem;vertical-align: middle;padding-bottom: 15px;} </style> </head>"""+"""<body><h1>Mediciones de variables ambientales</h2><p><i class="fas fa-thermometer-half" style="color:#9c2020;"></i><span class="ds-labels"> Ultima medicion de temperatura: </span><span id="temperature">{}</span><sup class="units">&deg;C</sup></p><p><i class="fas fa-water" style="color:#1eb8ab;"></i><span class="ds-labels"> Ultima muestra de humedad: </span><span id="humidity">{}</span><sup class="units">%</sup></p><br>""".format(last_temp,last_hum)+"""<span class="ds-labels"> Es importante considerar que este modulo solo puede retener informacion de las ultimas 3 horas de datos. Por lo tanto, la informacion mas reciente de los datos estara disponible en la tercera hora. </span>"""+averageTemperatureData+averageHumidiyData+"""averageTemperatureData.forEach(data => {document.write(`<p><i class="fas fa-thermometer-half" style="color:#9c2020a4;"></i><i class="fas fa-clock" style="color:#9c2020a4;"></i><span class="ds-labels">${data.label}</span><span id="${data.valueId}">${data.value}</span><sup class="units">&deg;C</sup></p>`);});averageHumidityData.forEach(data => {document.write(`<p><i class="fas fa-water" style="color:#1eb8ab;"></i><i class="fas fa-clock" style="color:#1eb8ab;"></i><span class="ds-labels">${data.label}</span><span id="${data.valueId}">${data.value}</span><sup class="units">%</sup></p>`);});</script></body></html>"""
	gc.collect()
	return response