# -*- coding: utf-8 -*-
import time
import datetime
from xml.dom.minidom import parse as mdParse
from windows import FontUtils, get_custom_xmls_version, download_custom_xmls
from caches import check_databases, clean_databases
from apis.trakt_api import trakt_sync_activities
from modules import kodi_utils, settings

disable_enable_addon, update_local_addons, get_infolabel, run_plugin = kodi_utils.disable_enable_addon, kodi_utils.update_local_addons, kodi_utils.get_infolabel, kodi_utils.run_plugin
ls, path_exists, translate_path, custom_context_main_menu_prop = kodi_utils.local_string, kodi_utils.path_exists, kodi_utils.translate_path, kodi_utils.custom_context_main_menu_prop
custom_context_prop, custom_info_prop, pause_settings_prop, addon = kodi_utils.custom_context_prop, kodi_utils.custom_info_prop, kodi_utils.pause_settings_prop, kodi_utils.addon
pause_services_prop, xbmc_monitor, xbmc_player, userdata_path = kodi_utils.pause_services_prop, kodi_utils.xbmc_monitor, kodi_utils.xbmc_player, kodi_utils.userdata_path
get_window_id, clean_settings, Thread, make_window_properties = kodi_utils.get_window_id, kodi_utils.clean_settings, kodi_utils.Thread, kodi_utils.make_window_properties
get_setting, set_setting, make_settings_dict, external_browse = kodi_utils.get_setting, kodi_utils.set_setting, kodi_utils.make_settings_dict, kodi_utils.external_browse
logger, json, run_addon, confirm_dialog, close_dialog = kodi_utils.logger, kodi_utils.json, kodi_utils.run_addon, kodi_utils.confirm_dialog, kodi_utils.close_dialog
get_property, set_property, clear_property, get_visibility = kodi_utils.get_property, kodi_utils.set_property, kodi_utils.clear_property, kodi_utils.get_visibility
trakt_sync_interval, trakt_sync_refresh_widgets, auto_start_fen = settings.trakt_sync_interval, settings.trakt_sync_refresh_widgets, settings.auto_start_fen
make_directories, kodi_refresh, list_dirs, delete_file = kodi_utils.make_directories, kodi_utils.kodi_refresh, kodi_utils.list_dirs, kodi_utils.delete_file
current_skin_prop, use_skin_fonts_prop, custom_skin_path = kodi_utils.current_skin_prop, kodi_utils.use_skin_fonts_prop, kodi_utils.custom_skin_path
fen_str, window_top_str, listitem_property_str = ls(32036).upper(), 'Window.IsTopMost(%s)', 'ListItem.Property(%s)'
media_windows = (10000, 10025)
movieinformation_str, contextmenu_str = 'movieinformation', 'contextmenu'

class SetKodiVersion:
	def run(self):
		logger(fen_str, 'SetKodiVersion Service Starting')
		kodi_version = get_infolabel('System.BuildVersion')
		set_property('fen.kodi_version', kodi_version)
		return logger(fen_str, 'SetKodiVersion Service Finished - Kodi Version Detected: %s' % kodi_version)

class InitializeDatabases:
	def run(self):
		logger(fen_str, 'InitializeDatabases Service Starting')
		check_databases()
		return logger(fen_str, 'InitializeDatabases Service Finished')

class DatabaseMaintenance:
	def run(self):
		logger(fen_str, 'Database Maintenance Service Starting')
		time = datetime.datetime.now()
		current_time = self._get_timestamp(time)
		due_clean = int(get_setting('database.maintenance.due', '0'))
		if due_clean == 0:
			next_clean = str(int(self._get_timestamp(time + datetime.timedelta(days=3))))
			set_setting('database.maintenance.due', next_clean)
			return logger(fen_str, 'Database Maintenance Service First Run - Skipping')
		if current_time >= due_clean:
			clean_databases(current_time, database_check=False, silent=True)
			next_clean = str(int(self._get_timestamp(time + datetime.timedelta(days=3))))
			set_setting('database.maintenance.due', next_clean)
			return logger(fen_str, 'Database Maintenance Service Finished')
		else: return logger(fen_str, 'Database Maintenance Service Finished - Not Run')

	def _get_timestamp(self, date_time):
		return int(time.mktime(date_time.timetuple()))

class CheckSettings:
	def run(self):
		logger(fen_str, 'CheckSettingsFile Service Starting')
		monitor = xbmc_monitor()
		wait_for_abort = monitor.waitForAbort
		clear_property('fen_settings')
		if not path_exists(userdata_path): make_directories(userdata_path)
		addon().setSetting('dummy_setting', 'foo')
		wait_for_abort(0.5)
		make_settings_dict()
		make_window_properties()
		try: del monitor
		except: pass
		return logger(fen_str, 'CheckSettingsFile Service Finished')

class CleanSettings:
	def run(self):
		logger(fen_str, 'CleanSettings Service Starting')
		clean_settings(silent=True)
		return logger(fen_str, 'CleanSettings Service Finished')

class FirstRunActions:
	def run(self):
		logger(fen_str, 'CheckUpdateActions Service Starting')
		addon_version, settings_version =  self.remove_alpha(addon().getAddonInfo('version')), self.remove_alpha(addon().getSetting('version_number'))
		addon().setSetting('version_number', addon_version)
		if addon_version != settings_version:
			logger(fen_str, 'CheckUpdateActions Running Update Actions....')
			self.update_action(addon_version)
		return logger(fen_str, 'CheckUpdateActions Service Finished')

	def update_action(self, addon_version):
		''' Put code that needs to run once on update here'''
		return

	def remove_alpha(self, string):
		try: result = ''.join(c for c in string if (c.isdigit() or c =='.'))
		except: result = ''
		return result

class ReuseLanguageInvokerCheck:
	def run(self):
		logger(fen_str, 'ReuseLanguageInvokerCheck Service Starting')
		addon_xml = translate_path('special://home/addons/plugin.video.fen/addon.xml')
		current_addon_setting = get_setting('reuse_language_invoker', 'true')
		root = mdParse(addon_xml)
		invoker_instance = root.getElementsByTagName('reuselanguageinvoker')[0].firstChild
		if invoker_instance.data != current_addon_setting:
			invoker_instance.data = current_addon_setting
			new_xml = str(root.toxml()).replace('<?xml version="1.0" ?>', '')
			with open(addon_xml, 'w') as f: f.write(new_xml)
			if confirm_dialog(text='%s\n%s' % (ls(33021), ls(33020))):
				update_local_addons()
				disable_enable_addon()
		return logger(fen_str, 'ReuseLanguageInvokerCheck Service Finished')

class TraktMonitor:
	def run(self):
		logger(fen_str, 'TraktMonitor Service Starting')
		monitor, player = xbmc_monitor(), xbmc_player()
		wait_for_abort, is_playing = monitor.waitForAbort, player.isPlayingVideo
		trakt_service_string = 'TraktMonitor Service Update %s - %s'
		update_string = 'Next Update in %s minutes...'
		wait_time = 30 * 60
		while not monitor.abortRequested():
			try:
				while is_playing() or get_property(pause_services_prop) == 'true': wait_for_abort(10)
				sync_interval, wait_time = trakt_sync_interval()
				next_update_string = update_string % sync_interval
				status = trakt_sync_activities()
				if status == 'success':
					logger(fen_str, trakt_service_string % ('Success', 'Trakt Update Performed'))
					if trakt_sync_refresh_widgets():
						kodi_refresh()
						logger(fen_str, trakt_service_string % ('Widgets Refresh', 'Setting Activated. Widget Refresh Performed'))
					else: logger(fen_str, trakt_service_string % ('Widgets Refresh', 'Setting Disabled. Skipping Widget Refresh'))
				elif status == 'no account': logger(fen_str, trakt_service_string % ('Aborted. No Trakt Account Active', next_update_string))
				elif status == 'failed': logger(fen_str, trakt_service_string % ('Failed. Error from Trakt', next_update_string))
				else: logger(fen_str, trakt_service_string % ('Success. No Changes Needed', next_update_string))# 'not needed'
			except Exception as e: logger(fen_str, trakt_service_string % ('Failed', 'The following Error Occured: %s' % str(e)))
			wait_for_abort(wait_time)
		try: del monitor
		except: pass
		try: del player
		except: pass
		return logger(fen_str, 'TraktMonitor Service Finished')

class CustomActions:
	def run(self):
		logger(fen_str, 'CustomActions Service Starting')
		monitor, player = xbmc_monitor(), xbmc_player()
		self.wait_for_abort, abort_requested, is_playing = monitor.waitForAbort, monitor.abortRequested, player.isPlayingVideo
		while not abort_requested():
			customs_active, any_custom_params = False, False
			context_visible, info_visible = False, False
			run_custom = False
			while not any([context_visible, info_visible]) and not abort_requested():
				custom_context = get_property(custom_context_prop) == 'true'
				custom_main_context = get_property(custom_context_main_menu_prop) == 'true'
				custom_info = get_property(custom_info_prop) == 'true'
				customs_active = any([custom_context, custom_main_context, custom_info])
				if not customs_active:
					self.wait_for_abort(2)
					continue
				if not get_window_id() in media_windows:
					self.wait_for_abort(2)
					continue
				if get_property(pause_services_prop) == 'true' or is_playing():
					self.wait_for_abort(2)
					continue
				if not external_browse() or get_infolabel(listitem_property_str % 'fen.widget') == 'true':
					run_custom = True
					custom_context_params = get_infolabel(listitem_property_str % 'fen.options_params')
					custom_main_context_params = get_infolabel(listitem_property_str % 'fen.context_main_menu_params')
					custom_info_params = get_infolabel(listitem_property_str % 'fen.extras_params')
					self.wait_for_abort(0.25)
				else:
					run_custom = False
					self.wait_for_abort(1)
				context_visible, info_visible = get_visibility(window_top_str % contextmenu_str), get_visibility(window_top_str % movieinformation_str)
			try:
				if run_custom and any([custom_context_params, custom_main_context_params, custom_info_params]):
					if info_visible:
						if custom_info and custom_info_params: self.run_custom_action(custom_info_params, movieinformation_str)
					else:
						if all([custom_context, custom_context_params != '']) or all([custom_main_context, custom_main_context_params != '']):
							self.run_custom_action(custom_context_params or custom_main_context_params, contextmenu_str)
				else: self.wait_for_abort(1)
			except: self.wait_for_abort(2)
		try: del monitor
		except: pass
		try: del player
		except: pass
		return logger(fen_str, 'CustomActions Service Finished')

	def run_custom_action(self, action, window):
		close_dialog(window)
		run_plugin(action)
		while get_visibility(window_top_str % window): self.wait_for_abort(0.25)

class CustomFonts:
	def run(self):
		logger(fen_str, 'CustomFonts Service Starting')
		monitor, player = xbmc_monitor(), xbmc_player()
		wait_for_abort, is_playing = monitor.waitForAbort, player.isPlayingVideo
		for item in (current_skin_prop, use_skin_fonts_prop): clear_property(item)
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
		return logger(fen_str, 'CustomFonts Service Finished')

class CheckCustomXMLs:
	def run(self):
		logger(fen_str, 'CheckCustomXMLs Service Starting')
		if '32859' in get_setting('custom_skins.enable', '$ADDON[plugin.video.fen 32860]'):
			current_version = get_setting('custom_skins.version', '0.0.0')
			latest_version = get_custom_xmls_version()
			if current_version != latest_version or not path_exists(translate_path(custom_skin_path[:-2])):
				success = download_custom_xmls()
				if success: set_setting('custom_skins.version', latest_version)
				logger(fen_str, 'CheckCustomXMLs Service - Attempted XMLs Update. Success? %s' % success)
		logger(fen_str, 'CheckCustomXMLs Service Finished')

class ClearSubs:
	def run(self):
		logger(fen_str, 'Clear Subtitles Service Starting')
		sub_formats = ('.srt', '.ssa', '.smi', '.sub', '.idx', '.nfo')
		subtitle_path = 'special://temp/%s'
		files = list_dirs(translate_path('special://temp/'))[1]
		for i in files:
			if i.startswith('FENSubs_') or i.endswith(sub_formats): delete_file(translate_path(subtitle_path % i))
		return logger(fen_str, 'Clear Subtitles Service Finished')

class AutoRun:
	def run(self):
		logger(fen_str, 'AutoRun Service Starting')
		if auto_start_fen(): run_addon()
		return logger(fen_str, 'AutoRun Service Finished')

class OnSettingsChangedActions:
	def run(self):
		if get_property(pause_settings_prop) != 'true':
			make_settings_dict()
			make_window_properties(override=True)

class OnNotificationActions:
	def run(self, sender, method, data):
		if sender == 'xbmc':
			if method in ('GUI.OnScreensaverActivated', 'System.OnSleep'): set_property(pause_services_prop, 'true')
			elif method in ('GUI.OnScreensaverDeactivated', 'System.OnWake'): clear_property(pause_services_prop)

