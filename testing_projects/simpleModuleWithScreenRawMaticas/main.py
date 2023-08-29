import gc
gc.collect()
import scheduler
import modules.initialize_modules as mods
mods.act_mod.startup_off()
sch=scheduler.Scheduler(act_module=mods.act_mod,sen_module=mods.sen_mod,screen_module=mods.screen_mod,web_module=mods.web_mod,)
gc.collect()
sch.loop()