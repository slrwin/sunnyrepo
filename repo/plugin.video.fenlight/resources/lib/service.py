# -*- coding: utf-8 -*-
from modules import service_functions
from modules.kodi_utils import Thread, xbmc_monitor, logger

on_notification_actions = service_functions.OnNotificationActions()

class FenLightMonitor(xbmc_monitor):
	def __init__ (self):
		xbmc_monitor.__init__(self)
		self.startServices()

	def startServices(self):
		service_functions.MakeDatabases().run()
		service_functions.CheckSettings().run()
		service_functions.RemoveOldDatabases().run()
		service_functions.CheckKodiVersion().run()
		Thread(target=service_functions.CustomActions().run).start()
		Thread(target=service_functions.CustomFonts().run).start()
		Thread(target=service_functions.TraktMonitor().run).start()
		Thread(target=service_functions.UpdateCheck().run).start()
		service_functions.AutoStart().run()

	def onNotification(self, sender, method, data):
		on_notification_actions.run(sender, method, data)

logger('Fen Light', 'Main Monitor Service Starting')
FenLightMonitor().waitForAbort()
logger('Fen Light', 'Main Monitor Service Finished')