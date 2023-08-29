import framebuf
from machine import Pin,I2C
from time import sleep
from ujson import load
from dependencies import font10
from dependencies.writer import Writer
from dependencies.ssd1306 import SSD1306_I2C
from utils.internet_connection import connect2
from utils.json_related import update_json_field
from utils.time_management_module import Time
class ScreenModule():
	def __init__(self,config_file:str,screenwidth:int=128,screenheight:int=64,scl_pin:int=22,sda_pin:int=21):
		with open(config_file)as f:
			config=load(f)
			self.ip=config["ip"]
			self.update_screen_every_some_time=Time(*config["screen"]["update_every_some_time"])
			self.refresh_time=Time(*config["screen"]["refresh_screen_every_some_time"])
			self.last_screen_update=Time(-100,0,0)
		self.refresh_timer=Time(0,-10,0)
		self.config_file=config_file
		self.screenwidth=screenwidth
		self.screenheight=screenheight
		i2c=I2C(scl=Pin(scl_pin),sda=Pin(sda_pin))
		self.screen=SSD1306_I2C(128,64,i2c,60)
		self.screen.poweron()
		self.w=Writer(self.screen,font10,verbose=False)
		self.display_boot_screen()
	def refresh_screen(self,now:Time):
		if(now-self.refresh_timer)>self.refresh_time:
			self.display_maticas_logo()
			self.refresh_timer=now
	def display_maticas_logo(self):
		with open('utils/a2.pbm','rb')as f:
			f.readline()
			dimensions=f.readline().split()
			width,height=int(dimensions[0]),int(dimensions[1])
			data=bytearray(f.read())
		self.screen.invert(1)
		self.screen.blit(framebuf.FrameBuffer(data,width,height,framebuf.MONO_HLSB),(self.screenwidth-width)//2,(self.screenheight-height)//2)
		self.screen.show()
		sleep(1.5)
		self.screen.invert(0)
		sleep(1.5)
	def display_boot_screen(self):
		self.display_maticas_logo()
		self.display_text(["Bienvenid@ a","Maticas Tech",":D"])
	def display_need_to_update_screen(self):
		self.display_text(["Guardando","Cambios...","Reiniciando..."])
	def display_overflow_screen(self):
		self.display_text(["RAM llena","Reiniciando..."])
	def display_no_connection_screen(self):
		self.display_text(["Fallo en","Servidor interno","Reiniciando..."])
	def display_exception_screen(self,exception:str):
		self.display_text([exception[i:i+15] for i in range(0,len(exception),15)])
	def display_text(self,text_lines):
		self.screen.fill(1)
		for i,line in enumerate(text_lines):
			self.screen.text(line,self.screenwidth//9,(i+1)*self.screenheight//8,0)
		self.screen.show()
	def update_ip(self)->None:
		self.ip=connect2(config_file=self.config_file,doreconnect=False)
		if self.ip==None:
			self.ip="No internet connection"
		update_json_field(self.config_file,"ip",self.ip)
	def display_ip(self,now:Time)->None:
		if(now-self.last_screen_update)>self.update_screen_every_some_time:
			self.last_screen_update=now
			self.update_ip()
			print("IP update.")
			ypadding=5
			xpadding=5
			between_lines_padding=20
			self.screen.fill(0)
			self.screen.show()
			self.w.set_textpos(self.screen,ypadding,xpadding)
			self.w.printstring("Pagina web en:\n")
			self.w.set_textpos(self.screen,ypadding+between_lines_padding,xpadding)
			self.w.printstring("{}\n".format(self.ip))
			self.screen.show()
			print("screen updated.")