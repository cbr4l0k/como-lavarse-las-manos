import network
import utime
from json import load
def connect2(config_file:str,doreconnect=False)->str:
	with open(config_file)as f:
		config=load(f)
	sta_if=network.WLAN(network.STA_IF)
	ap_if=network.WLAN(network.AP_IF)
	ap_if.active(False)
	utime.sleep(1)
	if not sta_if.isconnected():
		print('Connecting to hotspot...')
		sta_if.active(True)
		sta_if.connect(config["wifi_ssid"],config["wifi_password"])
		for count in range(600):
			if sta_if.isconnected():
				print('Network config:',sta_if.ifconfig())
				return sta_if.ifconfig()[0]
			print('.',end='')
			utime.sleep(1)
		sta_if.disconnect()
		sta_if.active(False)
		print('Connection failed')
	else:
		print('Already connected')
		print('Network config:',sta_if.ifconfig())
		if doreconnect:
			print('Reconnecting ...')
			reconnect(config_file,sta_if)
			return sta_if.ifconfig()[0]
		else:
			return sta_if.ifconfig()[0]
def reconnect(config_file:str,sta_if:network.WLAN)->None:
	sta_if.disconnect()
	sta_if.active(False)
	print('Disconnecting from network...')
	connect2(config_file,doreconnect=False)