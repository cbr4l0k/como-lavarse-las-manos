import ujson
def update_json_field(filepath:str,fiedldname:str,value:str)->None:
	with open(filepath,"r")as f:
		data=ujson.load(f)
		data[fiedldname]=value
	with open(filepath,"w")as f:
		ujson.dump(data,f)
def update_json_actuator(filepath:str,actuatorId:str,settings:dict)->None:
	with open(filepath,"r")as f:
		data=ujson.load(f)
		for field in settings.keys():
			data["actuators"][actuatorId][field]=settings[field]
	with open(filepath,"w")as f:
		ujson.dump(data,f)
def log_error(filepath:str,error_msg:str)->None:
	with open(filepath,"r")as f:
		data=ujson.load(f)
		if"errors"not in data.keys():
			data["errors"]=[]
			data["errors"].append(error_msg)
		elif len(data["errors"])>3:
			data["errors"].pop(0)
			data["errors"].append(error_msg)
	with open(filepath,"w")as f:
		ujson.dump(data,f)