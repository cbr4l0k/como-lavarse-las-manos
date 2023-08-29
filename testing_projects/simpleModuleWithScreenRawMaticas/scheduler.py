import gc
from time import sleep,ticks_ms,ticks_diff
from machine import reset
from utils.json_related import log_error
from utils.time_management_module import Time,get_current_time
from modules.actuators_module import ActuatorsModule
from modules.sensors_module import SensorsModule
from modules.screen_module import ScreenModule
from modules.web_module import WebModule
class Scheduler():
	def __init__(self,act_module:ActuatorsModule,sen_module:SensorsModule,screen_module:ScreenModule,web_module:WebModule):
		self.act_module=act_module
		self.sen_module=sen_module
		self.screen_module=screen_module
		self.web_module=web_module
		self.actuators=act_module.actuators
		self.sensors=sen_module.sensors
		self.boot=True
		self.current_time=Time(*get_current_time())
		self.sync_time_every_some_time=Time(1,30,0)
		self.time_away_count=Time(0,0,0)
		self.handle_modules_every_some_time=Time(0,0,30)
	def clean_memory(self)->None:
		if self.get_memory_use_percentage()>=60:
			gc.collect()
	def get_memory_use_percentage(self,verbose:bool=False)->float:
		current_use_of_memory=gc.mem_alloc()
		available_memory=gc.mem_free()
		percentage=(current_use_of_memory/(current_use_of_memory+available_memory))*100
		if verbose:
			print("Memory usage: {}%".format(percentage))
		return percentage
	def update_time(self,now,last)->None:
		if(self.boot) or (self.time_away_count>=self.sync_time_every_some_time):
			self.current_time=Time(*get_current_time())
			self.time_away_count=Time(0,0,0)
			self.boot=False
			print("server side time update.")
		else:
			self.current_time+=Time(0,0,ticks_diff(now,last)/1000)
			self.time_away_count+=Time(0,0,ticks_diff(now,last)/1000)
			print("local side time update.")
	def loop(self,log=True):
		try:
			self._loop(log=log)
		except MemoryError as e:
			print("MemoryError: {}".format(e))
			self.clean_memory()
			self.screen_module.display_overflow_screen()
			log_error("utils/config.json","MemoryError: {}. at {}".format(e,self.current_time))
			reset()
		except OSError as e:
			print("OSError: {}".format(e))
			self.clean_memory()
			self.screen_module.display_no_connection_screen()
			log_error("utils/config.json","OSError: {}. at {}".format(e,self.current_time))
			reset()
		except Exception as e:
			print("Exception: {}".format(e))
			self.clean_memory()
			self.screen_module.display_exception_screen("{}".format(e))
			log_error("utils/config.json","Exception: {}. at {}".format(e,self.current_time))
			reset()
	def _loop(self,log=True):
		last=ticks_ms()
		handle_modules_every_some_msecs=self.handle_modules_every_some_time.to_total_seconds()*1000
		while True:
			now=ticks_ms()
			if(ticks_diff(now,last)>=(handle_modules_every_some_msecs)) or (self.boot):
				print("handling time...")
				self.update_time(now,last)
				print("curent time {}\n".format(self.current_time))
				self.clean_memory()
				sleep(0.1)
				print("handling on/off actuators...")
				print("handling timed actuators...")
				self.act_module.timed_control(self.current_time)
				self.clean_memory()
				print("\n")
				print("handling sensors...")
				self.sen_module.timed_measurement(self.current_time)
				self.clean_memory()
				print("\n")
				print("handling screen...")
				self.screen_module.refresh_screen(self.current_time)
				self.screen_module.display_ip(self.current_time)
				self.clean_memory()
				print("\n")
				last=now
				print("Done!\n")
			self.clean_memory()
			if self.get_memory_use_percentage()<80:
				self.web_module.serve(self.current_time)
				self.clean_memory()
			sleep(0.1)
			if self.web_module.need_to_update:
				self.screen_module.display_need_to_update_screen()
				reset()
			if self.get_memory_use_percentage()>=90:
				self.clean_memory()
				self.screen_module.display_overflow_screen()
				raise MemoryError("memory overflow")
			self.get_memory_use_percentage(verbose=True)