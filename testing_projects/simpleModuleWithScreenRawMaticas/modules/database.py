class MeasurementList:
	def __init__(self,minutes_between_measurement:int,max_len:int=120):
		self.measurements=[0]*max_len
		self.max_len=max_len
		self.minutes_between_measurement=minutes_between_measurement
		self.oldest_measurement_idx=0
		self.latest_measurement_idx=0
		self.n_additions=0
	def append(self,measurement:float):
		if measurement is None or measurement<=0:print("Measurement is None or <= 0"); return
		self.n_additions+=1
		self.latest_measurement_idx=(self.n_additions%self.max_len)
		if(self.n_additions<self.max_len):
			self.oldest_measurement_idx=0
		else:
			self.oldest_measurement_idx=(self.latest_measurement_idx+1)%self.max_len
		self.measurements[self.latest_measurement_idx]=int(round(measurement))
		if(self.n_additions>2*self.max_len):
			self.n_additions=self.n_additions%self.max_len
		print("n: {}, oldest: {}, latest: {}".format(self.n_additions,self.oldest_measurement_idx,self.latest_measurement_idx))
	def get_latest_measurement(self)->float:
		return self.measurements[self.latest_measurement_idx]
	def nth_hour_generator(self,nth_hour:int):
		if(nth_hour>int(nth_hour*60/self.minutes_between_measurement)):
			raise ValueError("n_hours is larger than the total time of the measurement list")
		n_measurements=int(60/self.minutes_between_measurement)
		start_idx=(self.oldest_measurement_idx+int((nth_hour-1)*60/self.minutes_between_measurement))%len(self.measurements)
		end_idx=(start_idx+n_measurements-1)%len(self.measurements)
		print("nth: {}, start_idx: {}, end_idx: {}".format(nth_hour,start_idx,end_idx))
		if(start_idx<end_idx):
			for i in range(start_idx,end_idx):
				yield self.measurements[i]
		else:
			idx=[i for i in range(start_idx,len(self.measurements))]+[i for i in range(0,end_idx)]
			for i in idx:
				yield self.measurements[i]
class Database:
	def __init__(self,config_file:str)->None:
		self.registers=dict()
		import ujson
		with open(config_file,"r")as f:
			self.config=ujson.load(f)["sensors"]
	def get_register(self,register_id:str)->MeasurementList:
		return self.registers.get(register_id,None)
	def add_register(self,register_id:str,max_len:int=120)->None:
		if(register_id not in self.registers) and (register_id in self.config):
			from utils.time_management_module import Time
			minutes_between_measurement=Time(*self.config[register_id]["measure_every_some_time"]).to_total_minutes()
			self.registers[register_id]=MeasurementList(minutes_between_measurement,max_len)
		else:
			raise ValueError("Register {} already exists or is not in config file".format(register_id))
	def add_measurement(self,register_id:str,measurement:float)->None:
		register=self.registers.get(register_id)
		if register:
			register.append(measurement)