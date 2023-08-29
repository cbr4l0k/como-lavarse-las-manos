import gc
from time import sleep
from utils.internet_connection import*
from utils.json_related import update_json_field
config_file="utils/config.json"
sleep(1)
ip=connect2(config_file=config_file,doreconnect=False)
update_json_field(config_file,"ip",ip)
sleep(1)
gc.collect()