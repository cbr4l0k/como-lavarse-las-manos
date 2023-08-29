from modules.database import Database
config_file="./utils/config.json"
db_mod=Database(config_file=config_file)
db_mod.add_register("0",max_len=120)
db_mod.add_register("1",max_len=120)