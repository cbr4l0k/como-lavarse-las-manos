from dht import DHT11
from time import sleep
from machine import Pin,I2C,ADC
from modules.actuators_module import ActuatorsModule
from modules.sensors_module import SensorsModule
config_file="./utils/config.json"
act_mod=ActuatorsModule(config_file=config_file)
sen_mod=SensorsModule(config_file=config_file)
dht_sensor=DHT11(Pin(19))
def measure_temp(ntries=5)->int:
	measurements=0
	n_effective_measurements=0
	for sample in range(ntries):
		try:
			dht_sensor.measure()
			measurements+=dht_sensor.temperature()
			n_effective_measurements+=1
			sleep(1.1)
		except:
			print("This sensor seems to have a problem. FIX IT")
			return -1
	return measurements/n_effective_measurements
def measure_hum(ntries=5)->int:
	measurements=0
	n_effective_measurements=0
	for sample in range(ntries):
		try:
			dht_sensor.measure()
			measurements+=dht_sensor.humidity()
			n_effective_measurements+=1
			sleep(1.1)
		except:
			print("This sensor seems to have a problem. FIX IT")
			return -1
	return measurements/n_effective_measurements
sen_mod.set_measurement_function(sensor_id="0",fn=measure_temp)
sen_mod.set_measurement_function(sensor_id="1",fn=measure_hum)
from gc import collect
collect()
from modules.screen_module import ScreenModule
screen_mod=ScreenModule(config_file=config_file)
collect()
from modules.web_module import WebModule
web_mod=WebModule(config_file=config_file)
collect()