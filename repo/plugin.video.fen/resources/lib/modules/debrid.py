# -*- coding: utf-8 -*-
import time
from caches.debrid_cache import debrid_cache
from apis.real_debrid_api import RealDebridAPI
from apis.premiumize_api import PremiumizeAPI
from apis.alldebrid_api import AllDebridAPI
from modules import kodi_utils
from modules.utils import make_thread_list
from modules.settings import display_sleep_time, enabled_debrids_check
# logger = kodi_utils.logger

sleep, show_busy_dialog, hide_busy_dialog, notification = kodi_utils.sleep, kodi_utils.show_busy_dialog, kodi_utils.hide_busy_dialog, kodi_utils.notification
monitor, Thread, get_setting, ls = kodi_utils.monitor, kodi_utils.Thread, kodi_utils.get_setting, kodi_utils.local_string
plswait_str, checking_debrid_str, remaining_debrid_str = ls(32577), ls(32578), ls(32579)
debrid_list = [('Real-Debrid', 'rd'), ('Premiumize.me', 'pm'), ('AllDebrid', 'ad')]
debrid_list_modules = [('Real-Debrid', RealDebridAPI), ('Premiumize.me', PremiumizeAPI), ('AllDebrid', AllDebridAPI)]
line = '%s[CR]%s[CR]%s'
timeout = 20.0

def debrid_enabled():
	return [i[0] for i in debrid_list if enabled_debrids_check(i[1])]

def debrid_type_enabled(debrid_type, enabled_debrids):
	return [i[0] for i in debrid_list if i[0] in enabled_debrids and get_setting('%s.%s.enabled' % (i[1], debrid_type)) == 'true']

def debrid_valid_hosts(enabled_debrids):
	def _get_hosts(function):
		debrid_hosts_append(function().get_hosts())
	debrid_hosts = []
	debrid_hosts_append = debrid_hosts.append
	if enabled_debrids:
		threads = list(make_thread_list(_get_hosts, [i[1] for i in debrid_list_modules if i[0] in enabled_debrids]))
		[i.join() for i in threads]
	return debrid_hosts

def manual_add_magnet_to_cloud(params):
	show_busy_dialog()
	function = [i[1] for i in debrid_list_modules if i[0] == params['provider']][0]
	result = function().create_transfer(params['magnet_url'])
	function().clear_cache()
	hide_busy_dialog()
	if result == 'failed': notification(32490)
	else: notification(32576)

class DebridCheck:
	def run(self, hash_list, background, debrid_enabled, progress_dialog=None):
		self.progress_dialog = progress_dialog
		if self.progress_dialog: self.progress_dialog.reset_is_cancelled()
		self.hash_list = hash_list
		self.debrid_enabled = debrid_enabled
		self.sleep_time = display_sleep_time()
		self.main_threads = []
		self.ad_cached_hashes, self.pm_cached_hashes, self.rd_cached_hashes = [], [], []
		self.processing_hashes = False
		self.cached_hashes = self._query_local_cache()
		main_threads_append = self.main_threads.append
		debrid_runners = {'Real-Debrid': self.RD_check, 'Premiumize.me': self.PM_check, 'AllDebrid': self.AD_check}
		for item in debrid_enabled: main_threads_append(Thread(target=debrid_runners[item], name=item))
		if self.main_threads:
			[i.start() for i in self.main_threads]
			if background: [i.join() for i in self.main_threads]
			else:
				self.monitor_processing()
				if self.processing_hashes: self.debrid_check_dialog()
		return {'rd_cached_hashes': self.rd_cached_hashes, 'pm_cached_hashes': self.pm_cached_hashes, 'ad_cached_hashes': self.ad_cached_hashes}

	def cached_check(self, debrid):
		cached_list = [i[0] for i in self.cached_hashes if i[1] == debrid and i[2] == 'True']
		unchecked_list = [i for i in self.hash_list if not any([h for h in self.cached_hashes if h[0] == i and h[1] == debrid])]
		if unchecked_list: self.processing_hashes = True
		return cached_list, unchecked_list

	def RD_check(self):
		self.rd_cached_hashes, unchecked_hashes = self.cached_check('rd')
		if not unchecked_hashes: return
		rd_cache = RealDebridAPI().check_cache(unchecked_hashes)
		if not rd_cache: return
		cached_append = self.rd_cached_hashes.append
		process_list = []
		process_append = process_list.append
		try:
			for h in unchecked_hashes:
				cached = 'False'
				try:
					if h in rd_cache:
						info = rd_cache[h]
						if isinstance(info, dict) and len(info.get('rd')) > 0:
							cached_append(h)
							cached = 'True'
				except: pass
				process_append((h, cached))
		except:
			for i in unchecked_hashes: process_append((i, 'False'))
		self._add_to_local_cache(process_list, 'rd')

	def PM_check(self):
		self.pm_cached_hashes, unchecked_hashes = self.cached_check('pm')
		if not unchecked_hashes: return
		pm_cache = PremiumizeAPI().check_cache(unchecked_hashes)
		if not pm_cache: return
		cached_append = self.pm_cached_hashes.append
		process_list = []
		process_append = process_list.append
		try:
			pm_cache = pm_cache['response']
			for c, h in enumerate(unchecked_hashes):
				cached = 'False'
				try:
					if pm_cache[c] is True:
						cached_append(h)
						cached = 'True'
				except: pass
				process_append((h, cached))
		except:
			for i in unchecked_hashes: process_append((i, 'False'))
		self._add_to_local_cache(process_list, 'pm')

	def AD_check(self):
		self.ad_cached_hashes, unchecked_hashes = self.cached_check('ad')
		if not unchecked_hashes: return
		ad_cache = AllDebridAPI().check_cache(unchecked_hashes)
		if not ad_cache: return
		cached_append = self.ad_cached_hashes.append
		process_list = []
		process_append = process_list.append
		try:
			ad_cache = ad_cache['magnets']
			for i in ad_cache:
				cached = 'False'
				try:
					if i['instant'] == True:
						cached_append(i['hash'])
						cached = 'True'
				except: pass
				process_append((i['hash'], cached))
		except:
			for i in unchecked_hashes: process_append((i, 'False'))
		self._add_to_local_cache(process_list, 'ad')

	def monitor_processing(self):
		while not self.processing_hashes:
			sleep(5)
			if not [i for i in self.main_threads if i.is_alive()]: break

	def debrid_check_dialog(self):
		start_time = time.time()
		end_time = start_time + timeout
		while not self.progress_dialog.iscanceled():
			try:
				if monitor.abortRequested() is True: break
				remaining_debrids = [x.getName() for x in self.main_threads if x.is_alive() is True]
				current_time = time.time()
				current_progress = current_time - start_time
				try:
					insert_line = remaining_debrid_str % ', '.join(remaining_debrids).upper()
					percent = int((current_progress/float(timeout))*100)
					self.progress_dialog.update(line % (plswait_str, checking_debrid_str, insert_line), percent)
				except: pass
				sleep(self.sleep_time)
				if len(remaining_debrids) == 0: break
				if percent >= 100: break
			except Exception: pass

	def _query_local_cache(self):
		return debrid_cache.get_many(self.hash_list) or []

	def _add_to_local_cache(self, hash_list, debrid):
		debrid_cache.set_many(hash_list, debrid)

debrid_check = DebridCheck()
