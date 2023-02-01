# -*- coding: utf-8 -*-
from modules import service_functions
from modules.kodi_utils import Thread, xbmc_monitor, logger, local_string as ls

fen_str = ls(32036).upper()
OnNotificationActions = service_functions.OnNotificationActions()
OnSettingsChangedActions = service_functions.OnSettingsChangedActions()

class FenMonitor(xbmc_monitor):
	def __init__ (self):
		xbmc_monitor.__init__(self)
		self.startUpServices()
	
	def startUpServices(self):
		try: service_functions.SetKodiVersion().run()
		except: pass
		try: service_functions.InitializeDatabases().run()
		except: pass
		Thread(target=service_functions.DatabaseMaintenance().run).start()
		try: service_functions.CheckSettings().run()
		except: pass
		try: service_functions.CleanSettings().run()
		except: pass
		try: service_functions.FirstRunActions().run()
		except: pass
		try: service_functions.ReuseLanguageInvokerCheck().run()
		except: pass
		Thread(target=service_functions.TraktMonitor().run).start()
		Thread(target=service_functions.CustomActions().run).start()
		Thread(target=service_functions.CustomFonts().run).start()
		try: service_functions.ClearSubs().run()
		except: pass
		try: service_functions.AutoRun().run()
		except: pass

	def onSettingsChanged(self):
		OnSettingsChangedActions.run()

	def onNotification(self, sender, method, data):
		OnNotificationActions.run(sender, method, data)

logger(fen_str, 'Main Monitor Service Starting')
logger(fen_str, 'Settings Monitor Service Starting')
FenMonitor().waitForAbort()
logger(fen_str, 'Settings Monitor Service Finished')
logger(fen_str, 'Main Monitor Service Finished')