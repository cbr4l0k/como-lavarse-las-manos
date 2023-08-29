import dependencies.urequests as requests
from time import sleep
def get_current_time():
	providers=['https://timeapi.io/api/Time/current/zone?timeZone=America/Bogota','http://worldtimeapi.org/api/timezone/America/Bogota']
	fieldNames=["dateTime","datetime"]
	response=None
	for provider,fieldname in zip(providers,fieldNames):
		for iretry in range(3):
			try:
				response=requests.request("GET",url=provider)
			except:
				sleep(1)
				continue
			if response==None:
				continue
			elif(response.status_code==200):
				parsed=response.json()
				h,m,s=parse_datetime_time(parsed[fieldname])
				return (h,m,s)
	raise Exception("Sorry, seems like the time providers aren't working...")
def parse_datetime_time(datetime_str):
	start=11
	end=-7
	txt=datetime_str.strip()
	txt=txt[start:end]
	time_str=txt.split(":")
	hour=int(time_str[0])
	minute=int(time_str[1])
	second=float(time_str[2])
	return hour,minute,second
class Time:
	def __init__(self,hour=0,min=0,sec=0):
		self.hour=hour
		self.min=min
		self.sec=sec
	@staticmethod
	def from_string(time_str):
		hour,min,sec=time_str.split(":")
		return Time(int(hour),int(min),int(sec))
	@staticmethod
	def from_string_to_list(time_str):
		hour,min,sec=time_str.split(":")
		return [int(hour),int(min),int(sec)]
	def to_total_minutes(self):
		total_minutes=(self.hour*60)+(self.min)+(self.sec/60)
		return total_minutes
	def to_total_seconds(self):
		total_seconds=(self.hour*3600)+(self.min*60)+self.sec
		return total_seconds
	def to_total_hours(self):
		total_hours=self.hour+(self.min/60)+(self.sec/3600)
		return total_hours
	def __gt__(self,other):
		if self.hour>other.hour:
			return True
		elif self.hour==other.hour and self.min>other.min:
			return True
		elif self.hour==other.hour and self.min==other.min and self.sec>other.sec:
			return True
		else:
			return False
	def __ge__(self,other):
		if self.hour>other.hour:
			return True
		elif self.hour==other.hour and self.min>other.min:
			return True
		elif self.hour==other.hour and self.min==other.min and self.sec>=other.sec:
			return True
		else:
			return False
	def __lt__(self,other):
		if self.hour<other.hour:
			return True
		elif self.hour==other.hour and self.min<other.min:
			return True
		elif self.hour==other.hour and self.min==other.min and self.sec<other.sec:
			return True
		else:
			return False
	def __eq__(self,other):
		if self.hour==other.hour and self.min==other.min and self.sec==other.sec:
			return True
		else:
			return False
	def __sub__(self,other):
		seconds1=self.hour*3600+self.min*60+self.sec
		seconds2=other.hour*3600+other.min*60+other.sec
		diff=seconds1-seconds2
		return Time(int(diff//3600),int(diff%3600)//60,int(diff%60))
	def __add__(self,other):
		seconds1=self.hour*3600+self.min*60+self.sec
		seconds2=other.hour*3600+other.min*60+other.sec
		total_seconds=seconds1+seconds2
		new_hour=total_seconds//3600
		remaining_seconds=total_seconds%3600
		new_min=remaining_seconds//60
		new_sec=remaining_seconds%60
		return Time(int(new_hour),int(new_min),int(new_sec))
	def __str__(self):
		return "{:02d}:{:02d}:{:02d}".format(int(self.hour),int(self.min),int(self.sec))