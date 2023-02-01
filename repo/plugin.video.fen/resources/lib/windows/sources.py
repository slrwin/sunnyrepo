# -*- coding: utf-8 -*-
from windows import BaseDialog
from modules.settings import get_art_provider, provider_sort_ranks, get_fanart_data, suppress_episode_plot
from modules.kodi_utils import json, Thread, dialog, select_dialog, ok_dialog, hide_busy_dialog, addon_fanart, empty_poster, fetch_kodi_imagecache, get_icon, local_string as ls
from modules.kodi_utils import logger

info_icons_dict = {'furk': get_icon('provider_furk'),
					'easynews': get_icon('provider_easynews'),
					'alldebrid': get_icon('provider_alldebrid'),
					'real-debrid': get_icon('provider_realdebrid'),
					'premiumize': get_icon('provider_premiumize'),
					'ad_cloud': get_icon('provider_alldebrid'),
					'rd_cloud': get_icon('provider_realdebrid'),
					'pm_cloud': get_icon('provider_premiumize')}
info_quality_dict = {'4k': get_icon('flag_4k'),
					'1080p': get_icon('flag_1080p'),
					'720p': get_icon('flag_720p'),
					'sd': get_icon('flag_sd'),
					'cam': get_icon('flag_sd'),
					'tele': get_icon('flag_sd'),
					'scr': get_icon('flag_sd')}
extra_info_choices = (('PACK', 'PACK'), ('DOLBY VISION', 'D/VISION'), ('HIGH DYNAMIC RANGE (HDR)', 'HDR'), ('HYBRID', 'HYBRID'), ('AV1', 'AV1'),
					('HEVC (X265)', 'HEVC'), ('REMUX', 'REMUX'), ('BLURAY', 'BLURAY'), ('SDR', 'SDR'), ('3D', '3D'), ('DOLBY ATMOS', 'ATMOS'), ('DOLBY TRUEHD', 'TRUEHD'),
					('DOLBY DIGITAL EX', 'DD-EX'), ('DOLBY DIGITAL PLUS', 'DD+'), ('DOLBY DIGITAL', 'DD'), ('DTS-HD MASTER AUDIO', 'DTS-HD MA'), ('DTS-X', 'DTS-X'),
					('DTS-HD', 'DTS-HD'), ('DTS', 'DTS'), ('AAC', 'AAC'), ('OPUS', 'OPUS'), ('MP3', 'MP3'), ('8CH AUDIO', '8CH'), ('7CH AUDIO', '7CH'), ('6CH AUDIO', '6CH'),
					('2CH AUDIO', '2CH'), ('DVD SOURCE', 'DVD'), ('WEB SOURCE', 'WEB'), ('MULTIPLE LANGUAGES', 'MULTI-LANG'), ('SUBTITLES', 'SUBS'))
quality_choices = ('4K', '1080P', '720P', 'SD', 'TELE', 'CAM', 'SCR')
filter_str, clr_filter_str, extra_info_str, down_file_str, browse_pack_str, down_pack_str, furk_addto_str = ls(32152), ls(32153), ls(32605), ls(32747), ls(33004), ls(32007), ls(32769)
filter_quality, filter_provider, filter_title, filter_extraInfo, cloud_str, filters_ignored, start_scrape = ls(32154), ls(32157), ls(32679), ls(32169), ls(32016), ls(32686), ls(33023)
show_uncached_str, spoilers_str, pack_check, run_plugin_str = ls(32088), ls(33105), ('true', 'show', 'season'), 'RunPlugin(%s)'
string = str
upper, lower = string.upper, string.lower

class SourceResults(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_format = kwargs.get('window_format', 'list')
		self.window_style = kwargs.get('window_style', 'contrast')
		self.make_poster = self.window_format in ('list', 'medialist')
		self.window_id = kwargs.get('window_id')
		self.results = kwargs.get('results')
		self.uncached_torrents = kwargs.get('uncached_torrents', [])
		self.meta = kwargs.get('meta')
		self.meta_get = self.meta.get
		self.info_highlights_dict = kwargs.get('scraper_settings')
		self.prescrape = kwargs.get('prescrape')
		self.filters_ignored = '[B](%s)[/B]' % filters_ignored if kwargs.get('filters_ignored', False) else ''
		self.poster_main, self.poster_backup, self.fanart_main, self.fanart_backup, self.clearlogo_main, self.clearlogo_backup = get_art_provider()
		self.poster = self.original_poster()
		self.make_items()
		self.set_properties()

	def onInit(self):
		self.filter_applied = False
		if self.make_poster: Thread(target=self.set_poster).start()
		self.win = self.getControl(self.window_id)
		self.win.addItems(self.item_list)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		self.clearProperties()
		hide_busy_dialog()
		return self.selected

	def get_provider_and_path(self, provider):
		try: icon_path = info_icons_dict[provider]
		except: provider, icon_path = 'folders', get_icon('provider_folder')
		return provider, icon_path

	def get_quality_and_path(self, quality):
		icon_path = info_quality_dict[quality]
		return quality, icon_path

	def onAction(self, action):
		chosen_listitem = self.get_listitem(self.window_id)
		if action == self.info_action:
			self.open_window(('windows.sources', 'ResultsInfo'), 'sources_info.xml', item=chosen_listitem)
		elif action in self.selection_actions:
			if self.prescrape:
				if chosen_listitem.getProperty('perform_full_search') == 'true':
					self.selected = ('perform_full_search', '')
					return self.close()
			self.selected = ('play', json.loads(chosen_listitem.getProperty('source')))
			return self.close()
		elif action in self.context_actions:
			source = json.loads(chosen_listitem.getProperty('source'))
			choice = self.open_window(('windows.sources', 'ResultsContextMenu'), 'contextmenu.xml', item=source, meta=self.meta, filter_applied=self.filter_applied)
			if choice:
				if 'results_info' in choice: self.open_window(('windows.sources', 'ResultsInfo'), 'sources_info.xml', item=chosen_listitem)
				elif 'clear_results_filter' in choice: return self.clear_filter()
				elif 'results_filter' in choice: return self.filter_results()
				else: self.execute_code(choice)
		elif action in self.closing_actions:
			if self.filter_applied: return self.clear_filter()
			self.selected = (None, '')
			return self.close()

	def make_items(self, filtered_list=None):
		def builder(results):
			for count, item in enumerate(results, 1):
				try:
					get = item.get
					listitem = self.make_listitem()
					set_property = listitem.setProperty
					scrape_provider, source, quality, name = get('scrape_provider'), get('source'), get('quality', 'SD'), get('display_name')
					basic_quality, quality_icon = self.get_quality_and_path(lower(quality))
					pack = get('package', 'false') in pack_check
					extra_info = get('extraInfo', '')
					extra_info = extra_info.rstrip('| ')
					if pack: extra_info = '[B]%s PACK[/B] | %s' % (get('package'), extra_info)
					elif not extra_info: extra_info = 'N/A'
					if scrape_provider == 'external':
						source_site = upper(get('provider'))
						provider = upper(get('debrid', source_site).replace('.me', ''))
						provider_lower = lower(provider)
						provider_icon = self.get_provider_and_path(provider_lower)[1]
						if 'cache_provider' in item:
							if 'Uncached' in item['cache_provider']:
								if 'seeders' in item: set_property('source_type', 'UNCACHED (%d SEEDERS)' % get('seeders', 0))
								else: set_property('source_type', 'UNCACHED')
								set_property('highlight', 'dimgray')
							else:
								if highlight_type == 0: key = 'torrent_highlight'
								elif highlight_type == 1: key = provider_lower
								else: key = basic_quality
								set_property('highlight', self.info_highlights_dict[key])
								if pack: set_property('source_type', 'CACHED [B]PACK[/B]')
								else: set_property('source_type', 'CACHED')
						else:
							if highlight_type == 0: key = 'hoster_highlight'
							elif highlight_type == 1: key = provider_lower
							else: key = basic_quality
							set_property('highlight', self.info_highlights_dict[key])
							set_property('source_type', source)
						set_property('provider', provider)
					else:
						if pack: extra_info = extra_info.replace('true PACK', 'PACK')
						source_site = upper(source)
						provider, provider_icon = self.get_provider_and_path(lower(source))
						if highlight_type in (0, 1): key = provider
						else: key = basic_quality
						set_property('highlight', self.info_highlights_dict[key])
						set_property('source_type', 'DIRECT')
						set_property('provider', upper(provider))
					set_property('name', upper(name))
					set_property('source_site', source_site)
					set_property('provider_icon', provider_icon)
					set_property('quality_icon', quality_icon)
					set_property('size_label', get('size_label', 'N/A'))
					set_property('extra_info', extra_info)
					set_property('quality', upper(quality))
					set_property('count', '%02d.' % count)
					set_property('hash', get('hash', 'N/A'))
					set_property('source', json.dumps(item))
					yield listitem
				except: pass
		try:
			highlight_type = self.info_highlights_dict['highlight_type']
			if filtered_list: return list(builder(filtered_list))
			self.item_list = list(builder(self.results))
			if self.prescrape:
				prescrape_listitem = self.make_listitem()
				prescrape_listitem.setProperty('perform_full_search', 'true')
			self.total_results = string(len(self.item_list))
			if self.prescrape: self.item_list.append(prescrape_listitem)
		except: pass

	def set_properties(self):
		self.setProperty('window_format', self.window_format)
		self.setProperty('window_style', self.window_style)
		self.setProperty('fanart', self.original_fanart())
		self.setProperty('clearlogo', self.meta_get('custom_clearlogo') or self.meta_get(self.clearlogo_main) or self.meta_get(self.clearlogo_backup) or '')
		self.setProperty('title', self.meta_get('title'))
		if self.meta_get('media_type') == 'episode' and suppress_episode_plot(): plot = self.meta_get('tvshow_plot') or spoilers_str
		else: plot = self.meta_get('plot', '') or self.meta_get('tvshow_plot', '')
		self.setProperty('plot', plot)
		self.setProperty('total_results', self.total_results)
		self.setProperty('filters_ignored', self.filters_ignored)

	def original_poster(self):
		poster = self.meta_get('custom_poster') or self.meta_get(self.poster_main) or self.meta_get(self.poster_backup) or empty_poster
		self.current_poster = poster
		if 'image.tmdb' in self.current_poster:
			try: poster = self.current_poster.replace('w185', 'original').replace('w342', 'original').replace('w780', 'original')
			except: pass
		elif 'fanart.tv' in self.current_poster:
			if not self.check_poster_cached(self.current_poster): self.current_poster = self.meta_get(self.poster_backup) or empty_poster
		return poster

	def set_poster(self):
		if self.current_poster:
			image_control = 200 if self.window_format == 'list' else 205
			self.getControl(image_control).setImage(self.current_poster)
			self.getControl(210).setImage(self.poster)
			total_time = 0
			while not self.check_poster_cached(self.poster):
				if total_time >= 200: break
				total_time += 1
				self.sleep(50)
			self.getControl(image_control).setImage(self.poster)

	def check_poster_cached(self, poster):
		try:
			if poster == empty_poster: return True
			if fetch_kodi_imagecache(poster): return True
			return False
		except: return True

	def original_fanart(self):
		fanart = self.meta_get('custom_fanart') or self.meta_get(self.fanart_main) or self.meta_get(self.fanart_backup) or addon_fanart
		return fanart

	def filter_results(self):
		choices = [(filter_quality, 'quality'), (filter_provider, 'provider'), (filter_title, 'keyword_title'), (filter_extraInfo, 'extra_info')]
		if self.uncached_torrents: choices.append((show_uncached_str, 'show_uncached'))
		list_items = [{'line1': item[0]} for item in choices]
		kwargs = {'items': json.dumps(list_items), 'heading': filter_str}
		main_choice = select_dialog([i[1] for i in choices], **kwargs)
		if main_choice == None: return
		if main_choice in ('quality', 'provider'):
			if main_choice == 'quality': choice_sorter = quality_choices
			else:
				sort_ranks = provider_sort_ranks()
				sort_ranks['premiumize'] = sort_ranks.pop('premiumize.me')
				choice_sorter = sorted(sort_ranks.keys(), key=sort_ranks.get)
				choice_sorter = [upper(i) for i in choice_sorter]
			duplicates = set()
			provider_choices = [i.getProperty(main_choice) for i in self.item_list \
						if not (i.getProperty(main_choice) in duplicates or duplicates.add(i.getProperty(main_choice))) \
						and not i.getProperty(main_choice) == '']
			provider_choices.sort(key=choice_sorter.index)
			list_items = [{'line1': item} for item in provider_choices]
			kwargs = {'items': json.dumps(list_items), 'heading': filter_str, 'multi_choice': 'true'}
			choice = select_dialog(provider_choices, **kwargs)
			if choice == None: return
			filtered_list = [i for i in self.item_list if any(x in i.getProperty(main_choice) for x in choice)]
		elif main_choice == 'keyword_title':
			keywords = dialog.input(ls(33063))
			if not keywords: return
			keywords.replace(' ', '')
			keywords = keywords.split(',')
			choice = [upper(i) for i in keywords]
			filtered_list = [i for i in self.item_list if all(x in i.getProperty('name') for x in choice)]
		elif main_choice == 'extra_info':
			list_items = [{'line1': item[0]} for item in extra_info_choices]
			kwargs = {'items': json.dumps(list_items), 'heading': filter_str, 'multi_choice': 'true'}
			choice = select_dialog(extra_info_choices, **kwargs)
			if choice == None: return
			choice = [i[1] for i in choice]
			filtered_list = [i for i in self.item_list if all(x in i.getProperty('extra_info') for x in choice)]
		else: filtered_list = self.make_items(self.uncached_torrents)# show_uncached
		if not filtered_list: return ok_dialog(text=32760)
		self.filter_applied = True
		self.win.reset()
		self.win.addItems(filtered_list)
		self.setFocusId(self.window_id)
		self.setProperty('total_results', string(len(filtered_list)))

	def clear_filter(self):
		self.win.reset()
		self.setProperty('total_results', self.total_results)
		self.onInit()

class ResultsInfo(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.item = kwargs['item']
		self.item_get_property = self.item.getProperty
		self.set_properties()

	def run(self):
		self.doModal()

	def onAction(self, action):
		self.close()

	def get_provider_and_path(self):
		try:
			provider = lower(self.item_get_property('provider'))
			icon_path = info_icons_dict[provider]
		except: provider, icon_path = 'folders', get_icon('provider_folder')
		return provider, icon_path

	def get_quality_and_path(self):
		quality = lower(self.item_get_property('quality'))
		icon_path = info_quality_dict[quality]
		return quality, icon_path

	def set_properties(self):
		provider, provider_path = self.get_provider_and_path()
		quality, quality_path = self.get_quality_and_path()
		self.setProperty('name', self.item_get_property('name'))
		self.setProperty('source_type', self.item_get_property('source_type'))
		self.setProperty('source_site', self.item_get_property('source_site'))
		self.setProperty('size_label', self.item_get_property('size_label'))
		self.setProperty('extra_info', self.item_get_property('extra_info'))
		self.setProperty('highlight', self.item_get_property('highlight'))
		self.setProperty('hash', self.item_get_property('hash'))
		self.setProperty('provider', provider)
		self.setProperty('quality', quality)
		self.setProperty('provider_icon', provider_path)
		self.setProperty('quality_icon', quality_path)

class ResultsContextMenu(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = 2020
		self.item = kwargs['item']
		self.meta = kwargs['meta']
		self.filter_applied = kwargs['filter_applied']
		self.item_get = self.item.get
		self.item_list = []
		self.selected = None
		self.make_menu()

	def onInit(self):
		win = self.getControl(self.window_id)
		win.addItems(self.item_list)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		return self.selected

	def onAction(self, action):
		if action in self.selection_actions:
			chosen_listitem = self.get_listitem(self.window_id)
			self.selected = chosen_listitem.getProperty('action')
			return self.close()
		elif action in self.context_actions: return self.close()
		elif action in self.closing_actions: return self.close()

	def make_menu(self):  
		meta_json = json.dumps(self.meta)
		item_id = self.item_get('id', None)
		name = self.item_get('name')
		down_file_params, down_pack_params, browse_pack_params, add_magnet_to_cloud_params, add_files_to_furk_params = None, None, None, None, None
		provider_source = self.item_get('source')
		scrape_provider = self.item_get('scrape_provider')
		cache_provider = self.item_get('cache_provider', 'None')
		magnet_url = self.item_get('url', 'None')
		info_hash = self.item_get('hash', 'None')
		uncached_torrent = 'Uncached' in cache_provider
		source = json.dumps(self.item)
		if not uncached_torrent and scrape_provider != 'folders':
			down_file_params = {'mode': 'downloader', 'action': 'meta.single', 'name': self.meta.get('rootname', ''), 'source': source,
								'url': None, 'provider': scrape_provider, 'meta': meta_json}
		if 'package' in self.item:
			if scrape_provider == 'furk':
				add_files_to_furk_params = {'mode': 'furk.add_to_files', 'item_id': item_id}
				if self.item_get('package', 'false') == 'true':                 
					browse_pack_params = {'mode': 'furk.browse_packs', 'file_name': name, 'file_id': item_id}
					down_pack_params = {'mode': 'downloader', 'action': 'meta.pack', 'name': self.meta.get('rootname', ''), 'source': source,
										'url': None, 'provider': scrape_provider, 'meta': meta_json, 'file_name': name, 'file_id': item_id}
			elif not uncached_torrent:
				browse_pack_params = {'mode': 'debrid.browse_packs', 'provider': cache_provider, 'name': name,
									'magnet_url': magnet_url, 'info_hash': info_hash}
				down_pack_params = {'mode': 'downloader', 'action': 'meta.pack', 'name': self.meta.get('rootname', ''), 'source': source, 'url': None,
									'provider': cache_provider, 'meta': meta_json, 'magnet_url': magnet_url, 'info_hash': info_hash}
		if provider_source == 'torrent' and not uncached_torrent:
			add_magnet_to_cloud_params = {'mode': 'manual_add_magnet_to_cloud', 'provider': cache_provider, 'magnet_url': magnet_url}
		if self.filter_applied: self.item_list.append(self.make_contextmenu_item('[B]%s[/B]' % clr_filter_str, run_plugin_str, {'mode': 'clear_results_filter'}))
		else: self.item_list.append(self.make_contextmenu_item('[B]%s[/B]' % filter_str, run_plugin_str, {'mode': 'results_filter'}))
		self.item_list.append(self.make_contextmenu_item('[B]%s[/B]' % extra_info_str, run_plugin_str, {'mode': 'results_info'}))
		if add_magnet_to_cloud_params: self.item_list.append(self.make_contextmenu_item(cloud_str, run_plugin_str, add_magnet_to_cloud_params))
		if add_files_to_furk_params: self.item_list.append(self.make_contextmenu_item(furk_addto_str, run_plugin_str, add_files_to_furk_params))
		if browse_pack_params: self.item_list.append(self.make_contextmenu_item(browse_pack_str, run_plugin_str, browse_pack_params))
		if down_pack_params: self.item_list.append(self.make_contextmenu_item(down_pack_str, run_plugin_str, down_pack_params))
		if down_file_params: self.item_list.append(self.make_contextmenu_item(down_file_str, run_plugin_str, down_file_params))

class SourceResultsChooser(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = 5001
		self.xml_choices = kwargs.get('xml_choices')
		self.xml_items = []
		self.make_items()

	def onInit(self):
		self.win = self.getControl(self.window_id)
		self.win.addItems(self.xml_items)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		return self.choice

	def onAction(self, action):
		if action in self.closing_actions:
			self.choice = None
			self.close()
		if action in self.selection_actions:
			chosen_listitem = self.get_listitem(self.window_id)
			self.choice = chosen_listitem.getProperty('name')
			self.close()

	def make_items(self):
		append = self.xml_items.append
		for item in self.xml_choices:
			listitem = self.make_listitem()
			listitem.setProperty('name', item[0])
			listitem.setProperty('image', item[1])
			append(listitem)
