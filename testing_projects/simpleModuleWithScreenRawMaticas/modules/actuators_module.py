from utils.time_management_module import Time
class ActuatorWrapper:
	TIMED_TYPE='timed'
	ON_OFF_TYPE='on/off'
	def __init__(self,actuator_id:str,actuator_name:str,actuator_type:str,actuator_pin:Pin,start_time:Time,end_time:Time,minutes_on:int,minutes_off:int,):
		self.id=actuator_id
		self.name=actuator_name
		self.type=actuator_type
		self.pin=actuator_pin
		self.start_time=start_time
		self.end_time=end_time
		self.minutes_on=minutes_on
		self.minutes_off=minutes_off
		self.status=False
		self.last_used=Time(-100,0,0)
	def off(self)->None:
		self.pin.value(0)
		self.status=False
	def on(self)->None:
		self.pin.value(1)
		self.status=True
	def timed_on_off(self,now:Time)->None:
		if self.type==ActuatorWrapper.TIMED_TYPE:
			self.handle_timed(now)
			print("actuator {} of type {} is {}".format(self.name,self.type,self.status))
		elif self.type==ActuatorWrapper.ON_OFF_TYPE:
			self.handle_on_off(now)
			print("actuator {} of type {} is {}".format(self.name,self.type,self.status))
		else:
			raise ValueError("actuator type not recognized")
	def handle_on_off(self,now:Time)->None:
		if(self.start_time>now) or (now>self.end_time):
			self.off()
		else:
			self.on()
	def handle_timed(self,now:Time)->None:
		if(self.start_time>now) or (now>self.end_time):
			self.off()
			return
		if self.status and ((now-self.last_used).to_total_minutes()>self.minutes_on):
			self.off()
			self.last_used=now
		elif( not self.status) and ((now-self.last_used).to_total_minutes()>self.minutes_off):
			self.on()
			self.last_used=now
	def __str__(self):
		return "ActuatorWrapper {}: {}, is {}".format(self.id,self.name,self.status)
	def __repr__(self):
		return self.__str__()
class ActuatorsModule():
	def __init__(self,config_file:str):
		from ujson import load
		with open(config_file)as f:
			self.config=load(f)
		self.actuators_config=self.config["actuators"]
		self.actuators=dict()
		self.default_init()
	def startup_off(self)->None:
		print("Starting up actuators...")
		for actuator in self.actuators.values():
			actuator.off()
			print("Actuator {actuator.name} is OFF".format(actuator=actuator))
		print("Done! they are all OFF.\n")
	def default_init(self)->None:
		from machine import Pin
		for actuatorId in self.actuators_config.keys():
			actuator=ActuatorWrapper(actuatorId,self.actuators_config[actuatorId]["name"],self.actuators_config[actuatorId]["type"],Pin(self.actuators_config[actuatorId]["pin"],Pin.OUT),Time(*self.actuators_config[actuatorId]["starttime"]),Time(*self.actuators_config[actuatorId]["endtime"]),self.actuators_config[actuatorId]["minuteson"],self.actuators_config[actuatorId]["minutesoff"])
			self.actuators[actuatorId]=actuator
	def timed_control(self,now:Time):
		for actuatorId in self.actuators_config.keys():
			self.actuators[actuatorId].timed_on_off(now)