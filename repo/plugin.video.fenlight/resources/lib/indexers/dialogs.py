# -*- coding: utf-8 -*-
import re
from windows.base_window import open_window, create_window
from caches.base_cache import refresh_cached_data
from caches.settings_cache import get_setting, set_setting, set_default
from modules.downloader import manager
from modules import kodi_utils, source_utils, settings, metadata
from modules.source_utils import clear_scrapers_cache, get_aliases_titles, make_alias_dict, audio_filter_choices
from modules.utils import get_datetime, title_key, adjust_premiered_date, append_module_to_syspath, manual_module_import
# logger = kodi_utils.logger

ok_dialog, container_content, close_all_dialog, external = kodi_utils.ok_dialog, kodi_utils.container_content, kodi_utils.close_all_dialog, kodi_utils.external
get_property, set_property, get_icon, dialog, open_settings = kodi_utils.get_property, kodi_utils.set_property, kodi_utils.get_icon, kodi_utils.dialog, kodi_utils.open_settings
show_busy_dialog, hide_busy_dialog, notification, confirm_dialog = kodi_utils.show_busy_dialog, kodi_utils.hide_busy_dialog, kodi_utils.notification, kodi_utils.confirm_dialog
img_url, sleep, default_highlights, external_scraper_settings = kodi_utils.img_url, kodi_utils.sleep, kodi_utils.default_highlights, kodi_utils.external_scraper_settings
kodi_refresh, container_refresh_input = kodi_utils.kodi_refresh, kodi_utils.container_refresh_input
json, build_url, select_dialog, clear_property = kodi_utils.json, kodi_utils.build_url, kodi_utils.select_dialog, kodi_utils.clear_property
run_plugin, autoplay_next_episode, quality_filter = kodi_utils.run_plugin, settings.autoplay_next_episode, settings.quality_filter
numeric_input, container_update, activate_window, addon_fanart = kodi_utils.numeric_input, kodi_utils.container_update, kodi_utils.activate_window, kodi_utils.default_addon_fanart
addon_icon, poster_empty = kodi_utils.addon_icon, kodi_utils.empty_poster
movie_extras_buttons_defaults, tvshow_extras_buttons_defaults = kodi_utils.movie_extras_buttons_defaults, kodi_utils.tvshow_extras_buttons_defaults
extras_button_label_values, jsonrpc_get_addons = kodi_utils.extras_button_label_values, kodi_utils.jsonrpc_get_addons
extras_enabled_menus, active_internal_scrapers, auto_play = settings.extras_enabled_menus, settings.active_internal_scrapers, settings.auto_play
audio_filters, extras_open_action = settings.audio_filters, settings.extras_open_action
quality_filter, date_offset = settings.quality_filter, settings.date_offset
single_ep_list = ('episode.progress', 'episode.recently_watched', 'episode.next_trakt', 'episode.next_fenlight', 'episode.trakt_recently_aired', 'episode.trakt_calendar')
scraper_names = ['EXTERNAL SCRAPERS', 'EASYNEWS', 'RD CLOUD', 'PM CLOUD', 'AD CLOUD', 'FOLDERS 1-5']

def clear_sources_folder_choice(params):
	setting_id = params['setting_id']
	set_default(['%s.display_name' % setting_id, '%s.movies_directory' % setting_id, '%s.tv_shows_directory' % setting_id])

def external_scraper_choice(params):
	try: results = jsonrpc_get_addons('xbmc.python.module')
	except: return
	list_items = [{'line1': i['name'], 'icon': i['thumbnail']} for i in results]
	kwargs = {'items': json.dumps(list_items)}
	choice = select_dialog(results, **kwargs)
	if choice == None: return
	module_id, module_name = choice['addonid'], choice['name']
	try:
		append_module_to_syspath('special://home/addons/%s/lib' % module_id)
		main_folder_name = module_id.split('.')[-1]
		manual_module_import('%s.sources_%s' % (main_folder_name, main_folder_name))
		success = True
	except: success = False
	if success:
		try:
			set_setting('external_scraper.module', module_id)
			set_setting('external_scraper.name', module_name)
			set_setting('provider.external', 'true')
			ok_dialog(text='Success.[CR][B]%s[/B] set as External Scraper' % module_name)
		except: ok_dialog(text='Error')
	else:
		ok_dialog(text='The [B]%s[/B] Module is not compatible.[CR]Please choose a different Module...' % module_name.upper())
		return external_scraper_choice(params)

def restore_addon_fanart_choice(params):
	if not confirm_dialog(): return
	set_setting('default_addon_fanart', addon_fanart)

def audio_filters_choice(params={}):
	icon = get_icon('audio')
	list_items = [{'line1': item[0], 'line2': item[1], 'icon': icon} for item in audio_filter_choices]
	try: preselect = [audio_filter_choices.index(item) for item in audio_filter_choices if item[1] in audio_filters()]
	except: preselect = []
	kwargs = {'items': json.dumps(list_items), 'heading': 'Choose Audio Properties to Exclude', 'multi_choice': 'true', 'multi_line': 'true', 'preselect': preselect}
	selection = select_dialog([i[1] for i in audio_filter_choices], **kwargs)
	if selection == None: return
	if selection == []: set_setting('filter_audio', 'empty_setting')
	else: set_setting('filter_audio', ', '.join(selection))

def trailer_choice(params):
	media_type, poster, tmdb_id, trailer_url, all_trailers = params['media_type'], params['poster'], params['tmdb_id'], params['trailer_url'], params['all_trailers']
	if not trailer_url and not all_trailers:
		show_busy_dialog()
		from apis.tmdb_api import tmdb_media_videos
		try: all_trailers = tmdb_media_videos(media_type, tmdb_id)['results']
		except: pass
		hide_busy_dialog()
	if all_trailers:
		if len(all_trailers) == 1: video_id = all_trailers[0].get('key')
		else:
			from modules.utils import clean_file_name
			def _sort_trailers():
				official_trailers = [i for i in all_trailers if i['type'] == 'Trailer' and i['name'].lower() == 'official trailer']
				other_official_trailers = [i for i in all_trailers if i['type'] == 'Trailer' and 'official' in i['name'].lower() and not i in official_trailers]
				other_trailers = [i for i in all_trailers if i['type'] == 'Trailer' and not i in official_trailers  and not i in other_official_trailers]
				teaser_trailers = [i for i in all_trailers if i['type'] == 'Teaser']
				full_trailers = official_trailers + other_official_trailers + other_trailers + teaser_trailers
				features = [i for i in all_trailers if not i in full_trailers]
				return full_trailers + features
			sorted_trailers = _sort_trailers()
			list_items = [{'line1': clean_file_name(i['name']), 'icon': poster} for i in sorted_trailers]
			kwargs = {'items': json.dumps(list_items)}
			video_id = select_dialog([i['key'] for i in sorted_trailers], **kwargs)
			if video_id == None: return 'canceled'
		trailer_url = 'plugin://plugin.video.youtube/play/?video_id=%s' % video_id
	return trailer_url

def genres_choice(params):
	genres_list, genres, poster = params['genres_list'], params['genres'], params['poster']
	genre_list = [i for i in genres_list if i['name'] in genres]
	if not genre_list:
		notification('No Results', 2500)
		return None
	list_items = [{'line1': i['name'], 'icon': poster} for i in genre_list]
	kwargs = {'items': json.dumps(list_items)}
	return select_dialog([i['id'] for i in genre_list], **kwargs)

def keywords_choice(params):
	from apis.tmdb_api import tmdb_movie_keywords, tmdb_tv_keywords
	show_busy_dialog()
	media_type, tmdb_id, poster = params['media_type'], params['tmdb_id'], params['poster']
	if media_type == 'movie': function, key = tmdb_movie_keywords, 'keywords'
	else: function, key = tmdb_tv_keywords, 'results'
	try: results = function(tmdb_id)[key]
	except: results = []
	hide_busy_dialog()
	if not results:
		notification('No Results', 2500)
		return None
	list_items = [{'line1': i['name'], 'icon': poster} for i in results]
	kwargs = {'items': json.dumps(list_items)}
	return select_dialog([i['id'] for i in results], **kwargs)

def imdb_videos_choice(params):
	videos, poster = params['videos'], params['poster']
	try: videos = json.loads(videos)
	except: pass
	videos.sort(key=lambda x: x['quality_rank'])
	list_items = [{'line1': i['quality'], 'icon': poster} for i in videos]
	kwargs = {'items': json.dumps(list_items)}
	return select_dialog([i['url'] for i in videos], **kwargs)

def random_choice(params):
	meta, poster, return_choice = params.get('meta'), params.get('poster'), params.get('return_choice', 'false')
	meta = params.get('meta', None)	
	list_items = [{'line1': 'Single Random Play', 'icon': poster}, {'line1': 'Continual Random Play', 'icon': poster}]
	choices = ['play_random', 'play_random_continual']
	kwargs = {'items': json.dumps(list_items), 'heading': 'Choose Random Play Type...'}
	choice = select_dialog(choices, **kwargs)
	if return_choice == 'true': return choice
	if choice == None: return
	from modules.episode_tools import EpisodeTools
	exec('EpisodeTools(meta).%s()' % choice)

def trakt_manager_choice(params):
	if get_setting('fenlight.trakt.user', 'empty_setting') in ('empty_setting', '') : return notification('No Results', 3500)
	icon = params.get('icon', None) or get_icon('trakt')
	choices = [('Add To Trakt List...', 'Add'), ('Remove From Trakt List...', 'Remove')]
	list_items = [{'line1': item[0], 'icon': icon} for item in choices]
	kwargs = {'items': json.dumps(list_items), 'heading': 'Trakt Lists Manager'}
	choice = select_dialog([i[1] for i in choices], **kwargs)
	if choice == None: return
	from apis import trakt_api
	if choice == 'Add': trakt_api.trakt_add_to_list(params)
	else: trakt_api.trakt_remove_from_list(params)

def playback_choice(params):
	media_type, poster = params.get('media_type'), params.get('poster')
	season, episode = params.get('season', ''), params.get('episode', '')
	meta = params.get('meta')
	try: meta = json.loads(meta)
	except: pass
	if not isinstance(meta, dict):
		function = metadata.movie_meta if media_type == 'movie' else metadata.tvshow_meta
		meta = function('tmdb_id', meta, get_datetime())
	aliases = get_aliases_titles(make_alias_dict(meta, meta['title']))
	items = []
	items += [{'line': 'Rescrape & Select Source', 'function': 'clear_and_rescrape'}]
	items += [{'line': 'Scrape with DEFAULT External Scrapers', 'function': 'scrape_with_default'}]
	items += [{'line': 'Scrape with ALL External Scrapers', 'function': 'scrape_with_disabled'}]
	items += [{'line': 'Scrape With All Filters Ignored', 'function': 'scrape_with_filters_ignored'}]
	if aliases: items += [{'line': 'Scrape with an Alias', 'function': 'scrape_with_aliases'}]
	items += [{'line': 'Scrape with Custom Values', 'function': 'scrape_with_custom_values'}]
	list_items = [{'line1': i['line'], 'icon': poster} for i in items]
	kwargs = {'items': json.dumps(list_items), 'heading': 'Playback'}
	choice = select_dialog([i['function'] for i in items], **kwargs)
	if choice == None: return notification('Cancelled', 2500)
	def clear_caches():
		from caches.base_cache import clear_cache
		from caches.external_cache import ExternalCache
		show_busy_dialog()
		clear_cache('internal_scrapers', silent=True)
		ExternalCache().delete_cache_single(media_type, str(meta['tmdb_id']))
		hide_busy_dialog()
	if choice == 'clear_and_rescrape':
		clear_caches()
		if media_type == 'movie': play_params = {'mode': 'playback.media', 'media_type': 'movie', 'tmdb_id': meta['tmdb_id'], 'autoplay': 'false'}
		else: play_params = {'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': meta['tmdb_id'], 'season': season, 'episode': episode, 'autoplay': 'false'}
	elif choice == 'scrape_with_default':
		if media_type == 'movie': play_params = {'mode': 'playback.media', 'media_type': 'movie', 'tmdb_id': meta['tmdb_id'],
												'default_ext_only': 'true', 'prescrape': 'false', 'autoplay': 'false'}
		else: play_params = {'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': meta['tmdb_id'], 'season': season,
							'episode': episode, 'default_ext_only': 'true', 'prescrape': 'false', 'autoplay': 'false'}
	elif choice == 'scrape_with_disabled':
		if media_type == 'movie': play_params = {'mode': 'playback.media', 'media_type': 'movie', 'tmdb_id': meta['tmdb_id'],
												'disabled_ext_ignored': 'true', 'prescrape': 'false', 'autoplay': 'false'}
		else: play_params = {'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': meta['tmdb_id'], 'season': season,
							'episode': episode, 'disabled_ext_ignored': 'true', 'prescrape': 'false', 'autoplay': 'false'}
	elif choice == 'scrape_with_filters_ignored':
		if media_type == 'movie': play_params = {'mode': 'playback.media', 'media_type': 'movie', 'tmdb_id': meta['tmdb_id'],
												'ignore_scrape_filters': 'true', 'prescrape': 'false', 'autoplay': 'false'}
		else: play_params = {'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': meta['tmdb_id'], 'season': season,
							'episode': episode, 'ignore_scrape_filters': 'true', 'prescrape': 'false', 'autoplay': 'false'}
		set_property('fs_filterless_search', 'true')
	elif choice == 'scrape_with_aliases':
		if len(aliases) == 1: custom_title = aliases[0]
		else:
			poster = meta.get('poster') or meta.get('poster') or poster_empty
			list_items = [{'line1': i, 'icon': poster} for i in aliases]
			kwargs = {'items': json.dumps(list_items)}
			custom_title = select_dialog(aliases, **kwargs)
			if custom_title == None: return notification('Cancelled', 2500)
		custom_title = dialog.input('Title', defaultt=custom_title)
		if not custom_title: return notification('Cancelled', 2500)
		if media_type in ('movie', 'movies'): play_params = {'mode': 'playback.media', 'media_type': 'movie', 'tmdb_id': meta['tmdb_id'],
						'custom_title': custom_title, 'prescrape': 'false'}
		else: play_params = {'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': meta['tmdb_id'], 'season': season, 'episode': episode,
							'custom_title': custom_title, 'prescrape': 'false'}
	else:
		clear_caches()
		default_title, default_year = meta['title'], str(meta['year'])
		if media_type in ('movie', 'movies'): play_params = {'mode': 'playback.media', 'media_type': 'movie', 'tmdb_id': meta['tmdb_id'], 'prescrape': 'false'}
		else: play_params = {'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': meta['tmdb_id'], 'season': season, 'episode': episode, 'prescrape': 'false'}
		if aliases:
			if len(aliases) == 1: alias_title = aliases[0]
			poster = meta.get('poster') or poster_empty
			list_items = [{'line1': i, 'icon': poster} for i in aliases]
			kwargs = {'items': json.dumps(list_items)}
			alias_title = select_dialog(aliases, **kwargs)
			if alias_title: custom_title = dialog.input('Title', defaultt=alias_title)
			else: custom_title = dialog.input('Title', defaultt=default_title)
		else: custom_title = dialog.input('Title', defaultt=default_title)
		if not custom_title: return notification('Cancelled', 2500)
		def _process_params(default_value, custom_value, param_value):
			if custom_value and custom_value != default_value: play_params[param_value] = custom_value
		_process_params(default_title, custom_title, 'custom_title')
		custom_year = dialog.input('Year', type=numeric_input, defaultt=default_year)
		_process_params(default_year, custom_year, 'custom_year')
		if media_type == 'episode':
			custom_season = dialog.input('Season', type=numeric_input, defaultt=season)
			_process_params(season, custom_season, 'custom_season')
			custom_episode = dialog.input('Episode', type=numeric_input, defaultt=episode)
			_process_params(episode, custom_episode, 'custom_episode')
			if any(i in play_params for i in ('custom_season', 'custom_episode')):
				if autoplay_next_episode(): _process_params('', 'true', 'disable_autoplay_next_episode')
		all_choice = confirm_dialog(heading=meta.get('rootname', ''), text='Scrape with ALL External Scrapers?', ok_label='Yes', cancel_label='No')
		if all_choice == None: return notification('Cancelled', 2500)
		if not all_choice:
			default_choice = confirm_dialog(heading=meta.get('rootname', ''), text='Scrape with DEFAULT External Scrapers?', ok_label='Yes', cancel_label='No')
			if default_choice == None: return notification('Cancelled', 2500)
			if default_choice: _process_params('', 'true', 'default_ext_only')
		else:  _process_params('', 'true', 'disabled_ext_ignored')
		disable_filters_choice = confirm_dialog(heading=meta.get('rootname', ''), text='Disable All Filters for Search?', ok_label='Yes', cancel_label='No')
		if disable_filters_choice == None: return notification('Cancelled', 2500)
		if disable_filters_choice:
			_process_params('', 'true', 'ignore_scrape_filters')
			set_property('fs_filterless_search', 'true')
	from modules.sources import Sources
	Sources().playback_prep(play_params)

def set_quality_choice(params):
	quality_setting = params.get('setting_id')
	icon = params.get('icon', None) or ''
	dl = ['Include SD', 'Include 720p', 'Include 1080p', 'Include 4K']
	fl = ['SD', '720p', '1080p', '4K']
	try: preselect = [fl.index(i) for i in get_setting('fenlight.%s' % quality_setting).split(', ')]
	except: preselect = []
	list_items = [{'line1': item, 'icon': icon} for item in dl]
	kwargs = {'items': json.dumps(list_items), 'multi_choice': 'true', 'preselect': preselect}
	choice = select_dialog(fl, **kwargs)
	if choice is None: return
	if choice == []:
		ok_dialog(text='Error')
		return set_quality_choice(params)
	set_setting(quality_setting, ', '.join(choice))

def extras_buttons_choice(params):
	media_type, button_dict, orig_button_dict = params.get('media_type', None), params.get('button_dict', {}), params.get('orig_button_dict', {})
	if not orig_button_dict:
		for _type in ('movie', 'tvshow'):
			setting_id_base = 'extras.%s.button' % _type
			for item in range(10, 18):
				setting_id = setting_id_base + str(item)
				button_action = get_setting('fenlight.%s' % setting_id)
				button_label = extras_button_label_values[_type][button_action]
				button_dict[setting_id] = {'button_action': button_action, 'button_label': button_label, 'button_name': 'Button %s' % str(item - 9)}
				orig_button_dict[setting_id] = {'button_action': button_action, 'button_label': button_label, 'button_name': 'Button %s' % str(item - 9)}
	if media_type == None:
		choices = [('Set [B]Movie[/B] Buttons', 'movie'),
					('Set [B]TV Show[/B] Buttons', 'tvshow'),
					('Restore [B]Movie[/B] Buttons to Default', 'restore.movie'),
					('Restore [B]TV Show[/B] Buttons to Default', 'restore.tvshow'),
					('Restore [B]Movie & TV Show[/B] Buttons to Default', 'restore.both')]
		list_items = [{'line1': i[0]} for i in choices]
		kwargs = {'items': json.dumps(list_items), 'heading': 'Choose Media Type to Set Buttons', 'narrow_window': 'true'}
		choice = select_dialog(choices, **kwargs)
		if choice == None:
			if button_dict != orig_button_dict:
				for k, v in button_dict.items():
					set_setting(k, v['button_action'])
				return ok_dialog(text='Success')
			return
		media_type = choice[1]
		if 'restore' in media_type:
			restore_type = media_type.split('.')[1]
			if restore_type in ('movie', 'both'):
				for item in movie_extras_buttons_defaults:
					set_setting(item[0], item[1])
			if restore_type in ('tvshow', 'both'):
				for item in tvshow_extras_buttons_defaults:
					set_setting(item[0], item[1])
			return ok_dialog(text='Success')
	choices = [('[B]%s[/B]   |   %s' % (v['button_name'], v['button_label']), v['button_name'], v['button_label'], k) for k, v in button_dict.items() if media_type in k]
	list_items = [{'line1': i[0]} for i in choices]
	kwargs = {'items': json.dumps(list_items), 'heading': 'Choose Button to Set', 'narrow_window': 'true'}
	choice = select_dialog(choices, **kwargs)
	if choice == None: return extras_buttons_choice({'button_dict': button_dict, 'orig_button_dict': orig_button_dict})
	button_name, button_label, button_setting = choice[1:]
	choices = [(v, k) for k, v in extras_button_label_values[media_type].items() if not v == button_label]
	choices = [i for i in choices if not i[0] == button_label]
	list_items = [{'line1': i[0]} for i in choices]
	kwargs = {'items': json.dumps(list_items), 'heading': 'Choose Action For [B]%s[/B]' % button_name, 'narrow_window': 'true'}
	choice = select_dialog(choices, **kwargs)
	if choice == None: return extras_buttons_choice({'button_dict': button_dict, 'orig_button_dict': orig_button_dict, 'media_type': media_type})
	button_label, button_action = choice
	button_dict[button_setting] = {'button_action': button_action, 'button_label': button_label, 'button_name': button_name}
	return extras_buttons_choice({'button_dict': button_dict, 'orig_button_dict': orig_button_dict, 'media_type': media_type})

def extras_lists_choice(params={}):
	choices = [('Plot', 2000), ('Cast', 2050), ('Recommended', 2051), ('Reviews', 2052), ('Comments', 2053),
				('Trivia', 2054), ('Blunders', 2055), ('Parental Guide', 2056), ('Videos', 2057),
				('More from Year', 2058), ('More from Genres', 2059),	('More from Networks', 2060),
				('More from Collection', 2061), ('Media Images', 2062)]
	list_items = [{'line1': i[0]} for i in choices]
	current_settings = extras_enabled_menus()
	try: preselect = [choices.index(i) for i in choices if i[1] in current_settings]
	except: preselect = []
	kwargs = {'items': json.dumps(list_items), 'heading': 'Enable Content for Extras Lists', 'multi_choice': 'true', 'preselect': preselect}
	selection = select_dialog(choices, **kwargs)
	if selection  == []: return set_setting('extras.enabled', 'noop')
	elif selection == None: return
	selection = [str(i[1]) for i in selection]
	set_setting('extras.enabled', ','.join(selection))

def set_language_filter_choice(params):
	from modules.meta_lists import language_choices
	filter_setting = params.get('filter_setting')
	multi_choice = params.get('multi_choice', 'false')
	include_none = params.get('include_none', 'false')
	lang_choices = language_choices
	if include_none == 'false': lang_choices.pop('None')
	dl = list(lang_choices.keys())
	fl = list(lang_choices.values())
	try: preselect = [fl.index(i) for i in get_setting('fenlight.%s' % filter_setting).split(', ')]
	except: preselect = []
	list_items = [{'line1': item} for item in dl]
	kwargs = {'items': json.dumps(list_items), 'multi_choice': multi_choice, 'preselect': preselect}
	choice = select_dialog(fl, **kwargs)
	if choice == None: return
	if multi_choice == 'true':
		if choice == []: set_setting(filter_setting, 'eng')
		else: set_setting(filter_setting, ', '.join(choice))
	else: set_setting(filter_setting, choice)

def enable_scrapers_choice(params={}):
	icon = params.get('icon', None) or get_icon('fenlight')
	scrapers = ['external', 'easynews', 'rd_cloud', 'pm_cloud', 'ad_cloud', 'folders']
	cloud_scrapers = {'rd_cloud': 'rd.enabled', 'pm_cloud': 'pm.enabled', 'ad_cloud': 'ad.enabled'}
	preselect = [scrapers.index(i) for i in active_internal_scrapers()]
	list_items = [{'line1': item, 'icon': icon} for item in scraper_names]
	kwargs = {'items': json.dumps(list_items), 'multi_choice': 'true', 'preselect': preselect}
	choice = select_dialog(scrapers, **kwargs)
	if choice is None: return
	for i in scrapers:
		set_setting('provider.%s' % i, ('true' if i in choice else 'false'))
		if i in cloud_scrapers and i in choice: set_setting(cloud_scrapers[i], 'true')

def sources_folders_choice(params):
	return open_window(('windows.settings_manager', 'SettingsManagerFolders'), 'settings_manager_folders.xml')

def results_sorting_choice(params={}):
	choices = [('Quality, Provider, Size', '0'), ('Quality, Size, Provider', '1'),
				('Provider, Quality, Size', '2'), ('Provider, Size, Quality', '3'),
				('Size, Quality, Provider', '4'), ('Size, Provider, Quality', '5')]
	list_items = [{'line1': item[0]} for item in choices]
	kwargs = {'items': json.dumps(list_items), 'narrow_window': 'true'}
	choice = select_dialog(choices, **kwargs)
	if choice:
		set_setting('results.sort_order_display', choice[0])
		set_setting('results.sort_order', choice[1])

def results_format_choice(params={}):
	xml_choices = [
					('List',      img_url % 'rcgKRWk'),
					('Rows',      img_url % 'wHvaixs'),
					('WideList',  img_url % '4UwfSLy')
					]
	choice = open_window(('windows.sources', 'SourcesChoice'), 'sources_choice.xml', xml_choices=xml_choices)
	if choice: set_setting('results.list_format', choice)

def clear_favorites_choice(params={}):
	fl = [('Clear Movies Favorites', 'movie'), ('Clear TV Show Favorites', 'tvshow')]
	list_items = [{'line1': item[0]} for item in fl]
	kwargs = {'items': json.dumps(list_items), 'narrow_window': 'true'}
	media_type = select_dialog([item[1] for item in fl], **kwargs)
	if media_type == None: return
	if not confirm_dialog(): return
	from caches.favorites_cache import favorites_cache
	favorites_cache.clear_favorites(media_type)
	notification('Success', 3000)

def favorites_choice(params):
	media_type, tmdb_id, title = params.get('media_type'), params.get('tmdb_id'), params.get('title')
	from caches.favorites_cache import favorites_cache
	current_favorites = favorites_cache.get_favorites(media_type)
	if any(i['tmdb_id'] == tmdb_id for i in current_favorites): function, text, refresh = favorites_cache.delete_favourite, 'Remove From Favorites?', 'true'
	else: function, text, refresh = favorites_cache.set_favourite, 'Add To Favorites?', 'false'
	if not confirm_dialog(heading=title, text=text): return
	success = function(media_type, tmdb_id, title)
	refresh = params.get('refresh', refresh)
	if success:
		if refresh == 'true': kodi_refresh()
		notification('Success', 3500)
	else: notification('Error', 3500)

def scraper_color_choice(params):
	setting = params.get('setting_id')
	current_setting, original_highlight = get_setting('fenlight.%s' % setting), default_highlights[setting]
	if current_setting != original_highlight:
		action = confirm_dialog(text='Set new Highlight or Restore Default Highlight?', ok_label='Set New', cancel_label='Restore Default', default_control=10)
		if action == None: return
		if not action: return set_setting(setting, original_highlight)
	chosen_color = color_choice({'current_setting': current_setting})
	if chosen_color: set_setting(setting, chosen_color)

def color_choice(params):
	return open_window(('windows.color', 'SelectColor'), 'color.xml', current_setting=params.get('current_setting', None))

def options_menu_choice(params, meta=None):
	def strip_bold(_str):
		return _str.replace('[B]', '').replace('[/B]', '')
	def _builder():
		for item in listing: yield {'line1': item[0], 'line2': item[1] or item[0], 'icon': poster}
	params_get = params.get
	tmdb_id, content, poster, season_poster = params_get('tmdb_id', None), params_get('content', None), params_get('poster', None), params_get('season_poster', None)
	is_external, from_extras = params_get('is_external') in (True, 'True', 'true'), params_get('from_extras', 'false') == 'true'
	unaired = params_get('unaired') in (True, 'True', 'true')
	season, episode, in_progress_menu = params_get('season', ''), params_get('episode', ''), params_get('in_progress_menu', 'false') == 'true'
	if not content: content = container_content()[:-1]
	menu_type = content
	if content.startswith('episode.'): content = 'episode'
	if not meta:
		function = metadata.movie_meta if content == 'movie' else metadata.tvshow_meta
		meta = function('tmdb_id', tmdb_id, get_datetime())
	meta_get = meta.get
	rootname, title, year, imdb_id, tvdb_id = meta_get('rootname', None), meta_get('title'), meta_get('year'), meta_get('imdb_id', None), meta_get('tvdb_id', None)
	window_function = activate_window if is_external else container_update
	listing = []
	listing_append = listing.append
	if not from_extras:
		try: playcount = int(params_get('playcount', '0'))
		except: playcount = 0
		try: progress = int(params_get('progress', '0'))
		except: progress = 0
		if menu_type in ('movie', 'tvshow'):
			if extras_open_action(content):
				if menu_type == 'movie': listing_append(('Playback', '', 'playback'))
				else: listing_append(('Browse', 'Browse %s' % title, 'browse'))
			else: listing_append(('Extras', '', 'extras'))
			if menu_type == 'movie':
				listing_append(('Playback Options', 'Scrapers Options', 'playback_choice'))
				if not unaired:
					if playcount: listing_append(('Mark Unwatched', '', 'mark_unwatched_movie'))
					else: listing_append(('Mark Watched', '', 'mark_watched_movie'))
				if progress: listing_append(('Clear Progress', '', 'clear_progress'))
			else:
				if not unaired:
					if not playcount: listing_append(('Mark Watched', '', 'mark_watched_tvshow'))
					if progress: listing_append(('Mark Unwatched', '', 'mark_unwatched_tvshow'))
			if not is_external: listing_append(('Exit Movie List' if menu_type == 'movie' else 'Exit TV Show List', '', 'exit_menu'))
		else:
			listing_append(('Extras', '', 'extras'))
			if menu_type == 'season':
				if not unaired:
					if not playcount: listing_append(('Mark Watched', '', 'mark_watched_season'))
					if progress: listing_append(('Mark Unwatched', '', 'mark_unwatched_season'))
			else:
				listing_append(('Playback Options', 'Scrapers Options', 'playback_choice'))
				if not unaired:
					if not playcount: listing_append(('Mark Watched', '', 'mark_watched_episode'))
					else: listing_append(('Mark Unwatched', '', 'mark_unwatched_episode'))
				if progress: listing_append(('Clear Progress', '', 'clear_progress'))
		if is_external: listing_append(('Refresh Widgets', '', 'refresh_widgets'))
	if menu_type in ('movie', 'episode') or menu_type in single_ep_list:
		if menu_type == 'movie' and from_extras: listing_append(('Playback Options', 'Scrapers Options', 'playback_choice'))
		if menu_type in single_ep_list:
			listing_append(('Browse', 'Browse %s' % title, 'browse'))
			listing_append(('Browse Season', 'Browse %s Season %s' % (title, season), 'browse_season'))
	if menu_type in ('movie', 'tvshow'):
		if get_setting('fenlight.trakt.user', 'empty_setting') not in ('empty_setting', ''): listing_append(('Trakt Lists Manager', '', 'trakt_manager'))
		listing_append(('Favorites Manager', '', 'favorites_choice'))
		listing_append(('Recommended', 'Based On %s' % rootname, 'recommended'))
		if menu_type == 'tvshow': listing_append(('Play Random', 'Based On %s' % rootname, 'random'))
	if menu_type in ('movie', 'episode') or menu_type in single_ep_list:
		base_str1, base_str2, on_str = '%s%s', 'Currently: [B]%s[/B]', 'On'
		if auto_play(content): autoplay_status, autoplay_toggle, quality_setting = on_str, 'false', 'autoplay_quality_%s' % content
		else: autoplay_status, autoplay_toggle, quality_setting = 'Off', 'true', 'results_quality_%s' % content
		active_int_scrapers = [i.replace('_', '') for i in active_internal_scrapers()]
		current_scrapers_status = ', '.join([i for i in active_int_scrapers]) if len(active_int_scrapers) > 0 else 'N/A'
		current_quality_status =  ', '.join(quality_filter(quality_setting))
		listing_append((base_str1 % ('Auto Play', ' (%s)' % content), base_str2 % autoplay_status, 'toggle_autoplay'))
		if menu_type == 'episode' or menu_type in single_ep_list and autoplay_status == on_str:
			autoplay_next_status, autoplay_next_toggle = (on_str, 'false') if autoplay_next_episode() else ('Off', 'true')
			listing_append((base_str1 % ('Autoplay Next Episode', ''), base_str2 % autoplay_next_status, 'toggle_autoplay_next'))
		listing_append((base_str1 % ('Quality Limit', ' (%s)' % content), base_str2 % current_quality_status, 'set_quality'))
		listing_append((base_str1 % ('', 'Enable Scrapers'), base_str2 % current_scrapers_status, 'enable_scrapers'))
	if menu_type in ('movie', 'tvshow'): listing_append(('RE-CACHE %s INFO' % ('Movies' if menu_type == 'movie' else 'TV Shows'), 'Clear %s Cache' % rootname, 'clear_media_cache'))
	if menu_type in ('movie', 'episode') or menu_type in single_ep_list: listing_append(('Clear Scrapers Cache', '', 'clear_scrapers_cache'))
	if in_progress_menu: listing_append(('TV Shows Progress Manager', '', 'nextep_manager'))
	listing_append(('Open Download Manager', '', 'open_download_manager'))
	listing_append(('Open Tools', '', 'open_tools'))
	if menu_type in ('movie', 'episode') or menu_type in single_ep_list: listing_append(('Open External Scraper Settings', '', 'open_external_scraper_settings'))
	listing_append(('Open Settings', '', 'open_settings'))
	list_items = list(_builder())
	heading = rootname or 'Options...'
	kwargs = {'items': json.dumps(list_items), 'heading': heading, 'multi_line': 'true'}
	choice = select_dialog([i[2] for i in listing], **kwargs)
	if choice == None: return
	if choice == 'playback':
		return run_plugin({'mode': 'playback.media', 'media_type': 'movie', 'tmdb_id': tmdb_id})
	if choice == 'extras':
		return extras_menu_choice({'tmdb_id': tmdb_id, 'media_type': content, 'is_external': str(is_external)})
	if choice == 'mark_watched_movie':
		return run_plugin({'mode': 'watched_status.mark_movie', 'action': 'mark_as_watched', 'title': title, 'tmdb_id': tmdb_id})
	if choice == 'mark_unwatched_movie':
		return run_plugin({'mode': 'watched_status.mark_movie', 'action': 'mark_as_unwatched', 'title': title, 'tmdb_id': tmdb_id})
	if choice == 'mark_watched_episode':
		return run_plugin({'mode': 'watched_status.mark_episode', 'action': 'mark_as_watched', 'title': title, 'tmdb_id': tmdb_id,
							'tvdb_id': tvdb_id, 'season': season, 'episode': episode})
	if choice == 'mark_unwatched_episode':
		return run_plugin({'mode': 'watched_status.mark_episode', 'action': 'mark_as_unwatched', 'title': title, 'tmdb_id': tmdb_id,
							'tvdb_id': tvdb_id, 'season': season, 'episode': episode})
	if choice == 'mark_watched_tvshow':
		return run_plugin({'mode': 'watched_status.mark_tvshow', 'action': 'mark_as_watched', 'title': title, 'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id})
	if choice == 'mark_unwatched_tvshow':
		return run_plugin({'mode': 'watched_status.mark_tvshow', 'action': 'mark_as_unwatched', 'title': title, 'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id})
	if choice == 'mark_watched_season':
		return run_plugin({'mode': 'watched_status.mark_season', 'action': 'mark_as_watched', 'title': title, 'tmdb_id': tmdb_id,
							'tvdb_id': tvdb_id, 'season': season})
	if choice == 'mark_unwatched_season':
		return run_plugin({'mode': 'watched_status.mark_season', 'action': 'mark_as_unwatched', 'title': title, 'tmdb_id': tmdb_id,
							'tvdb_id': tvdb_id, 'season': season})
	if choice == 'clear_progress':
		return run_plugin({'mode': 'watched_status.erase_bookmark', 'media_type': content, 'tmdb_id': tmdb_id, 'season': season, 'episode': episode, 'refresh': 'true'})
	if choice == 'refresh_widgets':
		return kodi_refresh()
	if choice == 'clear_media_cache':
		close_all_dialog()
		return refresh_cached_data(meta)
	if choice == 'clear_scrapers_cache':
		return clear_scrapers_cache()
	if choice == 'open_download_manager':
		close_all_dialog()
		return manager()
	if choice == 'open_tools':
		close_all_dialog()
		return window_function({'mode': 'navigator.tools'})
	if choice == 'open_settings':
		close_all_dialog()
		return open_settings()
	if choice == 'open_external_scraper_settings':
		close_all_dialog()
		return external_scraper_settings()
	if choice == 'playback_choice':
		return playback_choice({'media_type': content, 'poster': poster, 'meta': meta, 'season': season, 'episode': episode})
	if choice == 'browse':
		return window_function({'mode': 'build_season_list', 'tmdb_id': tmdb_id})
	if choice == 'browse_season':
		return window_function({'mode': 'build_episode_list', 'tmdb_id': tmdb_id, 'season': season})
	if choice == 'nextep_manager':
		return window_function({'mode': 'build_next_episode_manager'})
	if choice == 'recommended':
		close_all_dialog()
		mode, action = ('build_movie_list', 'tmdb_movies_recommendations') if menu_type == 'movie' else ('build_tvshow_list', 'tmdb_tv_recommendations')
		return window_function({'mode': mode, 'action': action, 'key_id': tmdb_id, 'name': 'Recommended based on %s' % title})
	if choice == 'random':
		close_all_dialog()
		return random_choice({'meta': meta, 'poster': poster})
	if choice == 'trakt_manager':
		return trakt_manager_choice({'tmdb_id': tmdb_id, 'imdb_id': imdb_id, 'tvdb_id': tvdb_id or 'None', 'media_type': content, 'icon': poster})
	if choice == 'favorites_choice':
		return favorites_choice({'media_type': content, 'tmdb_id': tmdb_id, 'title': title})
	if choice == 'exit_menu':
		return run_plugin({'mode': 'navigator.exit_media_menu'})
	if choice == 'toggle_autoplay':
		set_setting('auto_play_%s' % content, autoplay_toggle)
	elif choice == 'toggle_autoplay_next':
		set_setting('autoplay_next_episode', autoplay_next_toggle)
	elif choice == 'set_quality':
		set_quality_choice({'setting_id': 'autoplay_quality_%s' % content if autoplay_status == on_str else 'results_quality_%s' % content, 'icon': poster})
	elif choice == 'enable_scrapers':
		enable_scrapers_choice({'icon': poster})
	options_menu_choice(params, meta=meta)

def extras_menu_choice(params):
	stacked = params.get('stacked', 'false') == 'true'
	if not stacked: show_busy_dialog()
	media_type = params['media_type']
	function = metadata.movie_meta if media_type == 'movie' else metadata.tvshow_meta
	meta = function('tmdb_id', params['tmdb_id'], get_datetime())
	if not stacked: hide_busy_dialog()
	open_window(('windows.extras', 'Extras'), 'extras.xml', meta=meta, is_external=params.get('is_external', 'true' if external() else 'false'),
															options_media_type=media_type, starting_position=params.get('starting_position', None))

def media_extra_info_choice(params):
	media_type, meta = params.get('media_type'), params.get('meta')
	extra_info, listings = meta.get('extra_info', None), []
	append = listings.append
	try:
		if media_type == 'movie':
			if meta['tagline']: append('[B]Tagline:[/B] %s' % meta['tagline'])
			aliases = get_aliases_titles(make_alias_dict(meta, meta['title']))
			if aliases: append('[B]Aliases:[/B] %s' % ', '.join(aliases))
			append('[B]Status:[/B] %s' % extra_info['status'])
			append('[B]Premiered:[/B] %s' % meta['premiered'])
			append('[B]Rating:[/B] %s (%s Votes)' % (str(round(meta['rating'], 1)), meta['votes']))
			append('[B]Runtime:[/B] %s mins' % int(float(meta['duration'])/60))
			append('[B]Genre/s:[/B] %s' % ', '.join(meta['genre']))
			append('[B]Budget:[/B] %s' % extra_info['budget'])
			append('[B]Revenue:[/B] %s' % extra_info['revenue'])
			append('[B]Director:[/B] %s' % ', '.join(meta['director']))
			append('[B]Writer/s:[/B] %s' % ', '.join(meta['writer']) or 'N/A')
			append('[B]Studio:[/B] %s' % ', '.join(meta['studio']) or 'N/A')
			if extra_info['collection_name']: append('[B]Collection:[/B] %s' % extra_info['collection_name'])
			append('[B]Homepage:[/B] %s' % extra_info['homepage'])
		else:
			append('[B]Type:[/B] %s' % extra_info['type'])
			if meta['tagline']: append('[B]Tagline:[/B] %s' % meta['tagline'])
			aliases = get_aliases_titles(make_alias_dict(meta, meta['title']))
			if aliases: append('[B]Aliases:[/B] %s' % ', '.join(aliases))
			append('[B]Status:[/B] %s' % extra_info['status'])
			append('[B]Premiered:[/B] %s' % meta['premiered'])
			append('[B]Rating:[/B] %s (%s Votes)' % (str(round(meta['rating'], 1)), meta['votes']))
			append('[B]Runtime:[/B] %d mins' % int(float(meta['duration'])/60))
			append('[B]Classification:[/B] %s' % meta['mpaa'])
			append('[B]Genre/s:[/B] %s' % ', '.join(meta['genre']))
			append('[B]Networks:[/B] %s' % ', '.join(meta['studio']))
			append('[B]Created By:[/B] %s' % extra_info['created_by'])
			try:
				last_ep = extra_info['last_episode_to_air']
				append('[B]Last Aired:[/B] %s - [B]S%.2dE%.2d[/B] - %s' \
					% (adjust_premiered_date(last_ep['air_date'], date_offset())[0].strftime('%d %B %Y'),
						last_ep['season_number'], last_ep['episode_number'], last_ep['name']))
			except: pass
			try:
				next_ep = extra_info['next_episode_to_air']
				append('[B]Next Aired:[/B] %s - [B]S%.2dE%.2d[/B] - %s' \
					% (adjust_premiered_date(next_ep['air_date'], date_offset())[0].strftime('%d %B %Y'),
						next_ep['season_number'], next_ep['episode_number'], next_ep['name']))
			except: pass
			append('[B]Seasons:[/B] %s' % meta['total_seasons'])
			append('[B]Episodes:[/B] %s' % meta['total_aired_eps'])
			append('[B]Homepage:[/B] %s' % extra_info['homepage'])
	except: return notification('Error', 2000)
	return '[CR][CR]'.join(listings)

def discover_choice(params):
	open_window(('windows.discover', 'Discover'), 'discover.xml', media_type=params['media_type'])