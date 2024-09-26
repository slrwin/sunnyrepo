# -*- coding: utf-8 -*-
from time import time
from windows.base_window import FontUtils
from caches.base_cache import make_databases, remove_old_databases
from caches.settings_cache import get_setting, sync_settings
from apis.trakt_api import trakt_sync_activities
from modules.updater import update_check
from modules import kodi_utils, settings

run_addon, pause_services_prop, xbmc_monitor, xbmc_player = kodi_utils.run_addon, kodi_utils.pause_services_prop, kodi_utils.xbmc_monitor, kodi_utils.xbmc_player
firstrun_update_prop, get_property, set_property, clear_property = kodi_utils.firstrun_update_prop, kodi_utils.get_property, kodi_utils.set_property, kodi_utils.clear_property
logger, kodi_version, ok_dialog, notification, home = kodi_utils.logger, kodi_utils.kodi_version, kodi_utils.ok_dialog, kodi_utils.notification, kodi_utils.home
run_plugin, current_skin_prop, json = kodi_utils.run_plugin, kodi_utils.current_skin_prop, kodi_utils.json
trakt_sync_interval, update_action, update_delay, auto_start_fenlight = settings.trakt_sync_interval, settings.update_action, settings.update_delay, settings.auto_start_fenlight
trakt_service_string = 'TraktMonitor Service Update %s - %s'
trakt_success_line_dict = {'success': 'Trakt Update Performed', 'no account': '(Unauthorized) Trakt Update Performed'}
update_string = 'Next Update in %s minutes...'

class MakeDatabases:
	def run(self):
		logger('Fen Light', 'MakeDatabases Service Starting')
		make_databases()
		return logger('Fen Light', 'MakeDatabases Service Finished')

class CheckSettings:
	def run(self):
		logger('Fen Light', 'CheckSettingsFile Service Starting')
		sync_settings()
		return logger('Fen Light', 'CheckSettingsFile Service Finished')

class RemoveOldDatabases:
	def run(self):
		logger('Fen Light', 'RemoveOldDatabases Service Starting')
		remove_old_databases()
		return logger('Fen Light', 'RemoveOldDatabases Service Finished')

class CheckKodiVersion:
	def run(self):
		logger('Fen Light', 'CheckKodiVersion Service Starting')
		if kodi_version() < 20: ok_dialog('Fen Light', 'Kodi 20 or above required[CR]Please update Kodi or uninstall Fen Light')
		return logger('Fen Light', 'CheckKodiVersion Service Finished')

class CustomFonts:
	def run(self):
		logger('Fen Light', 'CustomFonts Service Starting')
		monitor, player = xbmc_monitor(), xbmc_player()
		wait_for_abort, is_playing = monitor.waitForAbort, player.isPlayingVideo
		clear_property(current_skin_prop)
		font_utils = FontUtils()
		while not monitor.abortRequested():
			font_utils.execute_custom_fonts()
			if get_property(pause_services_prop) == 'true' or is_playing(): sleep = 20
			else: sleep = 10
			wait_for_abort(sleep)
		try: del monitor
		except: pass
		try: del player
		except: pass
		return logger('Fen Light', 'CustomFonts Service Finished')

class TraktMonitor:
	def run(self):
		logger('Fen Light', 'TraktMonitor Service Starting')
		monitor, player = xbmc_monitor(), xbmc_player()
		wait_for_abort, is_playing = monitor.waitForAbort, player.isPlayingVideo
		while not monitor.abortRequested():
			while is_playing() or get_property(pause_services_prop) == 'true': wait_for_abort(10)
			wait_time = 1800
			try:
				sync_interval, wait_time = trakt_sync_interval()
				next_update_string = update_string % sync_interval
				status = trakt_sync_activities()
				if status == 'failed': logger('Fen Light', trakt_service_string % ('Failed. Error from Trakt', next_update_string))
				else:
					if status in ('success', 'no account'): logger('Fen Light', trakt_service_string % ('Success. %s' % trakt_success_line_dict[status], next_update_string))
					else: logger('Fen Light', trakt_service_string % ('Success. No Changes Needed', next_update_string))# 'not needed'
					if status == 'success' and get_setting('fenlight.trakt.refresh_widgets', 'false') == 'true': run_plugin({'mode': 'kodi_refresh'})
			except Exception as e: logger('Fen Light', trakt_service_string % ('Failed', 'The following Error Occured: %s' % str(e)))
			wait_for_abort(wait_time)
		try: del monitor
		except: pass
		try: del player
		except: pass
		return logger('Fen Light', 'TraktMonitor Service Finished')

class UpdateCheck:
	def run(self):
		if get_property(firstrun_update_prop) == 'true': return
		logger('Fen Light', 'UpdateCheck Service Starting')
		end_pause = time() + update_delay()
		monitor, player = xbmc_monitor(), xbmc_player()
		wait_for_abort, is_playing = monitor.waitForAbort, player.isPlayingVideo
		while not monitor.abortRequested():
			while time() < end_pause: wait_for_abort(1)
			while get_property(pause_services_prop) == 'true' or is_playing(): wait_for_abort(1)
			update_check(update_action())
			break
		set_property(firstrun_update_prop, 'true')
		try: del monitor
		except: pass
		try: del player
		except: pass
		return logger('Fen Light', 'UpdateCheck Service Finished')

class WidgetRefresher:
	def run(self):
		logger('Fen Light', 'WidgetRefresher Service Starting')
		monitor, player = xbmc_monitor(), xbmc_player()
		wait_for_abort, self.is_playing = monitor.waitForAbort, player.isPlayingVideo
		set_property('fenlight.refresh_widgets', 'true')
		self.set_next_refresh()
		wait_for_abort(20)
		while not monitor.abortRequested():
			try:
				wait_for_abort(10)
				clear_property('fenlight.refresh_widgets')
				offset = int(get_setting('fenlight.widget_refresh_timer', '60'))
				if offset != self.offset:
					self.set_next_refresh()
					continue
				if self.condition_check(): continue
				if self.next_refresh < time():
					run_plugin({'mode': 'refresh_widgets', 'show_notification': get_setting('fenlight.widget_refresh_notification', 'false')}, block=True)
					logger('Fen Light', 'WidgetRefresher Service - Widgets Refreshed')
					self.set_next_refresh()
			except: pass
		try: del monitor
		except: pass
		try: del player
		except: pass
		return logger('Fen Light', 'WidgetRefresher Service Finished')

	def condition_check(self):
		if not home(): return True
		if self.next_refresh == None or self.is_playing() or get_property(pause_services_prop) == 'true': return True
		if get_property('fenlight.window_loaded') == 'true': return True 
		try:
			window_stack = json.loads(get_property('fenlight.window_stack'))
			if window_stack or window_stack == []: return True
		except: pass
		return False

	def set_next_refresh(self):
		self.offset = int(get_setting('fenlight.widget_refresh_timer', '60'))
		if self.offset: self.next_refresh = time() + (self.offset*60)
		else: self.next_refresh = None

class AutoStart:
	def run(self):
		logger('Fen Light', 'AutoStart Service Starting')
		if auto_start_fenlight(): run_addon()
		return logger('Fen Light', 'AutoStart Service Finished')

class OnNotificationActions:
	def run(self, sender, method, data):
		if sender == 'xbmc':
			if method in ('GUI.OnScreensaverActivated', 'System.OnSleep'):
				set_property(pause_services_prop, 'true')
				logger('OnNotificationActions', 'PAUSING Fen Light Services Due to Device Sleep')
			elif method in ('GUI.OnScreensaverDeactivated', 'System.OnWake'):
				clear_property(pause_services_prop)
				logger('OnNotificationActions', 'UNPAUSING Fen Light Services Due to Device Awake')
