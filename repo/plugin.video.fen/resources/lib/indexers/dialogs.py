# -*- coding: utf-8 -*-
import re
from windows import open_window
from caches import refresh_cached_data
from modules import kodi_utils, source_utils, settings, metadata
from modules.utils import get_datetime, title_key
# logger = kodi_utils.logger

ok_dialog, container_content, close_all_dialog, external_browse = kodi_utils.ok_dialog, kodi_utils.container_content, kodi_utils.close_all_dialog, kodi_utils.external_browse
get_property, open_settings, set_property, get_icon, dialog = kodi_utils.get_property, kodi_utils.open_settings, kodi_utils.set_property, kodi_utils.get_icon, kodi_utils.dialog
show_busy_dialog, hide_busy_dialog, notification, confirm_dialog = kodi_utils.show_busy_dialog, kodi_utils.hide_busy_dialog, kodi_utils.notification, kodi_utils.confirm_dialog
pause_settings_change, unpause_settings_change, img_url, sleep = kodi_utils.pause_settings_change, kodi_utils.unpause_settings_change, kodi_utils.img_url, kodi_utils.sleep
get_setting, set_setting, make_settings_dict, execute_builtin = kodi_utils.get_setting, kodi_utils.set_setting, kodi_utils.make_settings_dict, kodi_utils.execute_builtin
json, ls, build_url, translate_path, select_dialog = kodi_utils.json, kodi_utils.local_string, kodi_utils.build_url, kodi_utils.translate_path, kodi_utils.select_dialog
run_plugin, metadata_user_info, autoplay_next_episode, quality_filter = kodi_utils.run_plugin, settings.metadata_user_info, settings.autoplay_next_episode, settings.quality_filter
make_window_properties, get_infolabel, kodi_refresh, item_jump = kodi_utils.make_window_properties, kodi_utils.get_infolabel, kodi_utils.kodi_refresh, kodi_utils.item_jump
numeric_input, confirm_progress_media, container_update = kodi_utils.numeric_input, kodi_utils.confirm_progress_media, kodi_utils.container_update
poster_empty, fanart_empty, clear_property, highlight_prop = kodi_utils.empty_poster, kodi_utils.addon_fanart, kodi_utils.clear_property, kodi_utils.highlight_prop
fen_str, addon_icon, database, maincache_db, custom_context_prop = ls(32036), kodi_utils.addon_icon, kodi_utils.database, kodi_utils.maincache_db, kodi_utils.custom_context_prop
movie_extras_buttons_defaults, tvshow_extras_buttons_defaults = kodi_utils.movie_extras_buttons_defaults, kodi_utils.tvshow_extras_buttons_defaults
extras_button_label_values, path_exists, custom_skin_path = kodi_utils.extras_button_label_values, kodi_utils.path_exists, kodi_utils.custom_skin_path
get_language, extras_enabled_menus, active_internal_scrapers, auto_play = settings.get_language, settings.extras_enabled_menus, settings.active_internal_scrapers, settings.auto_play
extras_open_action, get_art_provider, fanarttv_default, ignore_articles = settings.extras_open_action, settings.get_art_provider, settings.fanarttv_default, settings.ignore_articles
clear_scrapers_cache, get_aliases_titles, make_alias_dict = source_utils.clear_scrapers_cache, source_utils.get_aliases_titles, source_utils.make_alias_dict
toggle_all, enable_disable, set_default_scrapers = source_utils.toggle_all, source_utils.enable_disable, source_utils.set_default_scrapers
autoscrape_next_episode, audio_filters = settings.autoscrape_next_episode, settings.audio_filters
quality_filter, watched_indicators = settings.quality_filter, settings.watched_indicators
default_highlights = kodi_utils.default_highlights
closing_options = (None, 'trakt_manager', 'favorites_choice', 'playback_choice', 'clear_media_cache', 'set_media_artwork', 'clear_scrapers_cache', 'open_external_scrapers_choice',
					'open_fen_settings', 'browse', 'browse_season', 'nextep_manager', 'recommended', 'random', 'playback', 'extras', 'mark_movie',
					'mark_episode', 'mark_watched_tvshow', 'mark_unwatched_tvshow', 'mark_watched_season', 'mark_unwatched_season', 'clear_progress',
					'refresh_widgets', 'exit_menu')

def custom_skins_choice(params):
	current_version = get_setting('custom_skins.version', '0.0.0')
	currently_enabled = '32859' in get_setting('custom_skins.enable')
	new_setting_value = '32860' if currently_enabled else '32859'
	if not currently_enabled:
		if path_exists(translate_path(custom_skin_path)) and current_version != '0.0.0': success = True
		else:
			show_busy_dialog()
			from windows import download_custom_xmls, get_custom_xmls_version
			latest_version = get_custom_xmls_version()
			if latest_version:
				success = download_custom_xmls()
				hide_busy_dialog()
				if success:
					set_setting('custom_skins.version', latest_version)
					ok_dialog(text=ls(33125) % latest_version)
				else: notification(32574)
			else:
				notification(32574)
				success = False
	else: success = True
	if success: set_setting('custom_skins.enable', '$ADDON[plugin.video.fen %s]' % new_setting_value)

def tmdb_image_resolutions_choice(params):
	icon = get_icon('tmdb')
	choices = [(32163, 0), (32164, 1), (32165, 2), (32166, 3)]
	list_items = [{'line1': ls(i[0]), 'icon': icon} for i in choices]
	kwargs = {'items': json.dumps(list_items), 'heading': ls(32149)}
	resolution = select_dialog(choices, **kwargs)
	if resolution == None: return
	if str(get_setting('image_resolutions')) == str(resolution[1]): return
	from caches import clear_cache
	pause_settings_change()
	set_setting('image_resolutions_name', '$ADDON[plugin.video.fen %s]' % resolution[0])
	set_setting('image_resolutions', str(resolution[1]))
	unpause_settings_change()
	make_settings_dict()
	clear_cache('meta', silent=True)
	kodi_refresh()

def extras_buttons_choice(params):
	media_type, button_dict, orig_button_dict = params.get('media_type', None), params.get('button_dict', {}), params.get('orig_button_dict', {})
	if not orig_button_dict:
		for _type in ('movie', 'tvshow'):
			setting_id_base = 'extras.%s.button' % _type
			for item in range(10, 18):
				setting_id = setting_id_base + str(item)
				button_action = get_setting(setting_id)
				button_label = extras_button_label_values[_type][button_action]
				button_dict[setting_id] = {'button_action': button_action, 'button_label': button_label, 'button_name': 'Button %s' % str(item - 9)}
				orig_button_dict[setting_id] = {'button_action': button_action, 'button_label': button_label, 'button_name': 'Button %s' % str(item - 9)}
	if media_type == None:
		choices = [(32028, get_icon('movies'), 'movie'), (32029, get_icon('tv'), 'tvshow')]
		list_items = [{'line1': ls(i[0]), 'icon': i[1]} for i in choices]
		kwargs = {'items': json.dumps(list_items), 'heading': ls(33120)}
		choice = select_dialog(choices, **kwargs)
		if choice == None:
			if button_dict != orig_button_dict:
				pause_settings_change()
				for k, v in button_dict.items(): set_setting(k, v['button_action'])
				unpause_settings_change()
				make_settings_dict()
				return ok_dialog(text=32576)
			return
		media_type = choice[2]
	icon = get_icon('movies' if media_type == 'movie' else 'tv')
	choices = [('[B]%s[/B]   |   %s' % (v['button_name'], ls(v['button_label'])), v['button_name'], v['button_label'], k) for k, v in button_dict.items() if media_type in k]
	list_items = [{'line1': i[0], 'icon': icon} for i in choices]
	kwargs = {'items': json.dumps(list_items), 'heading': ls(33121)}
	choice = select_dialog(choices, **kwargs)
	if choice == None: return extras_buttons_choice({'button_dict': button_dict, 'orig_button_dict': orig_button_dict})
	button_name, button_label, button_setting = choice[1:]
	choices = [(v, k) for k, v in extras_button_label_values[media_type].items() if not v == button_label]
	choices = [i for i in choices if not i[0] == button_label]
	list_items = [{'line1': ls(i[0]), 'icon': icon} for i in choices]
	kwargs = {'items': json.dumps(list_items), 'heading': ls(33122) % button_name}
	choice = select_dialog(choices, **kwargs)
	if choice == None: return extras_buttons_choice({'button_dict': button_dict, 'orig_button_dict': orig_button_dict, 'media_type': media_type})
	button_label, button_action = choice
	button_dict[button_setting] = {'button_action': button_action, 'button_label': button_label, 'button_name': button_name}
	return extras_buttons_choice({'button_dict': button_dict, 'orig_button_dict': orig_button_dict, 'media_type': media_type})

def default_extras_buttons_choice(params):
	choices = [(32028, get_icon('movies'), 'movie'), (32029, get_icon('tv'), 'tvshow'), (32030, get_icon('genre_fantasy'), 'both')]
	list_items = [{'line1': ls(i[0]), 'icon': i[1]} for i in choices]
	kwargs = {'items': json.dumps(list_items), 'heading': ls(33123)}
	choice = select_dialog(choices, **kwargs)
	if choice == None: return
	media_type = choice[2]
	pause_settings_change()
	if media_type in ('movie', 'both'):
		for item in movie_extras_buttons_defaults: set_setting(item[0], item[1])
	if media_type in ('tvshow', 'both'):
		for item in tvshow_extras_buttons_defaults: set_setting(item[0], item[1])
	unpause_settings_change()
	make_settings_dict()
	ok_dialog(text=32576)

def default_highlight_colors_choice(params):
	silent = params.get('silent', 'false') != 'false'
	if not silent and not confirm_dialog(): return
	pause_settings_change()
	for item in default_highlights:
		try:
			setting, value = item[0], item[1]
			set_setting(setting, value)
			set_setting('%s_name' % setting, '[COLOR=%s]%s[/COLOR]' % (value, value))
		except: pass
	unpause_settings_change()
	make_settings_dict()
	if not silent: notification(32576, 3000)

def audio_filters_choice(params={}):
	from modules.source_utils import audio_filter_choices
	icon = get_icon('audio')
	list_items = [{'line1': item[0], 'line2': item[1], 'icon': icon} for item in audio_filter_choices]
	try: preselect = [audio_filter_choices.index(item) for item in audio_filter_choices if item[1] in audio_filters()]
	except: preselect = []
	kwargs = {'items': json.dumps(list_items), 'heading': ls(32002), 'multi_choice': 'true', 'multi_line': 'true', 'preselect': preselect}
	selection = select_dialog([i[1] for i in audio_filter_choices], **kwargs)
	if selection == None: return
	if selection == []: set_setting('filter_audio', '')
	set_setting('filter_audio', ', '.join(selection))

def movie_sets_to_collection_choice(params):
	from apis.trakt_api import add_to_collection, trakt_sync_activities, trakt_fetch_collection_watchlist
	from modules.metadata import movieset_meta
	collection_id = params.get('collection_id')
	trakt_collection_ids = [i['media_ids']['tmdb'] for i in trakt_fetch_collection_watchlist('collection', 'movies') if i['media_ids']['tmdb']]
	data = movieset_meta(collection_id, metadata_user_info())
	collection_name, parts = data['title'], data['parts']
	tmdb_image_url = 'https://image.tmdb.org/t/p/w342%s'
	list_items = []
	for item in parts:
		tmdb_id, title, release_date, poster_path, release_date = item['id'], item['title'], item['release_date'], item['poster_path'], item['release_date']
		if poster_path: icon = tmdb_image_url % poster_path
		else: icon = poster_empty
		in_collection = tmdb_id in trakt_collection_ids
		if release_date: line1 = '%s (%s)' % (title, release_date.split('-')[0])
		else: line1 =  title
		if in_collection: line2 = ls(33082)
		else: line2 = ls(33083)
		list_items.append({'line1': line1, 'line2': line2, 'icon': icon, 'tmdb_id': tmdb_id, 'in_collection': in_collection, 'release_date': release_date})
	list_items.sort(key=lambda k: k['release_date'] or '2050')
	preselect = [list_items.index(i) for i in list_items if not i['in_collection']]
	kwargs = {'items': json.dumps(list_items), 'heading': collection_name, 'multi_choice': 'true', 'multi_line': 'true', 'preselect': preselect}
	selection = select_dialog([i['tmdb_id'] for i in list_items], **kwargs)
	if selection in (None, []): return
	show_busy_dialog()
	try: result = add_to_collection({'movies': [{'ids': {'tmdb': i}} for i in selection]}, multi=True)
	except: result = {'added': {'movies': 0}}
	hide_busy_dialog()
	movies_to_add = len(selection)
	movies_added = result['added']['movies']
	if movies_added:
		ok_dialog(text=ls(33084) % movies_added)
		trakt_sync_activities()
	else:
		if 'existing' in result and result['existing']['movies'] == movies_to_add: text = 32765
		else: text = 33047
		ok_dialog(text=text)

def link_folders_choice(params):
	from caches.main_cache import main_cache
	def _get_media_type():
		media_type_list = [('movie', ls(32028).replace('s', ''), get_icon('movies')), ('tvshow', ls(32029).replace('s', ''), get_icon('tv'))]
		list_items = [{'line1': item[1], 'line2': ls(33077) % item[1], 'icon': item[2]} for item in media_type_list]
		kwargs = {'items': json.dumps(list_items), 'multi_line': 'true'}
		chosen_media_type = select_dialog([i[0] for i in media_type_list], **kwargs)
		return chosen_media_type
	service, folder_id, action = params.get('service'), params.get('folder_id'), params.get('action')
	string = 'FEN_%s_%s' % (service, folder_id)
	current_link = main_cache.get(string)
	if action == 'remove':
		if not current_link: return
		if not confirm_dialog(text=ls(33075) % current_link['rootname']): return
		dbcon = database.connect(maincache_db)
		dbcur = dbcon.cursor()
		dbcur.execute("DELETE FROM maincache WHERE id=?", (string,))
		dbcon.commit()
		dbcon.close()
		clear_property(string)
		kodi_refresh()
		return ok_dialog(text=32576)
	if current_link:
		if not confirm_dialog(text=ls(33076) % (current_link['media_type'].upper(), current_link['rootname'])): return
	media_type = _get_media_type()
	if media_type == None: return
	query = dialog.input(ls(32228)).lower()
	if not query: return
	from apis.tmdb_api import tmdb_movies_search, tmdb_tv_search
	year = dialog.input('%s (%s)' % (ls(32543), ls(32669)), type=numeric_input)
	if year: query = '%s|%s' % (query, year)
	function = tmdb_movies_search if media_type == 'movie' else tmdb_tv_search
	results = function(query, 1)['results']
	if len(results) == 0: return ok_dialog(text=32490)
	name_key = 'title' if media_type == 'movie' else 'name'
	released_key = 'release_date' if media_type == 'movie' else 'first_air_date'
	tmdb_image_base = 'https://image.tmdb.org/t/p/w300%s'
	function_list = []
	function_list_append = function_list.append
	def _builder():
		for item in results:
			try:
				title = item[name_key]
				try: year = item[released_key].split('-')[0]
				except: year = ''
				if year: rootname = '%s (%s)' % (title, year)
				else: rootname = title
				tmdb_id = item['id']
				poster_path = item['poster_path']
				if poster_path: icon = tmdb_image_base % poster_path
				else: icon = poster_empty
				function_list_append({'rootname': rootname, 'tmdb_id': tmdb_id})
				yield {'line1': rootname, 'icon': icon}
			except: pass
	list_items = list(_builder())
	kwargs = {'items': json.dumps(list_items)}
	chosen = select_dialog(function_list, **kwargs)
	if chosen == None: return
	from datetime import timedelta
	data = {'media_type': 'episode' if media_type == 'tvshow' else media_type, 'rootname': chosen['rootname'], 'tmdb_id': str(chosen['tmdb_id'])}
	main_cache.set(string, data, expiration=timedelta(days=3650))
	kodi_refresh()
	return ok_dialog(text=32576)

def navigate_to_page_choice(params):
	def _builder():
		for i in start_list:
			try:
				if page_ref == 0: line1 = '%s %s' % (ls(32022), str(i))
				else:
					page_contents = all_pages[i-1]
					first_entry, last_entry = page_contents[0]['title'], page_contents[-1]['title']
					first_alpha, last_alpha = title_key(first_entry, ignore).replace(' ', '')[0:3], title_key(last_entry, ignore).replace(' ', '')[0:3]
					if first_entry == last_entry: line_end = first_alpha
					else: line_end = '%s - %s' % (first_alpha, last_alpha)
					if page_ref == 1: line1 = line_end
					else: line1 = '%s %s   |   %s' % (ls(32022), str(i), line_end)
					if i == current_page: line1 = '[COLOR %s][B]%s   |   %s[/B][/COLOR]' % (get_property(highlight_prop), line1, current_page_str)
			except: line1 = ''
			yield {'line1': line1, 'icon': item_jump}
	try:
		media_type, total_pages, all_pages, current_page_str = params.get('media_type'), int(params.get('total_pages')), json.loads(params.get('all_pages')), ls(32995)
		ignore, page_ref = ignore_articles(), int(params.get('page_reference', '0'))
		start_list = [i for i in range(1, int(params.get('total_pages'))+1)]
		current_page = int(params.get('current_page'))
		list_items = list(_builder())
		kwargs = {'items': json.dumps(list_items), 'heading': ls(32036)}
		new_page = select_dialog(start_list, **kwargs)
		if new_page == None or new_page == current_page: return
		url_params = {'mode': params.get('transfer_mode', ''), 'action': params.get('transfer_action', ''), 'new_page': new_page, 'media_type': params.get('media_type', ''),
					'query': params.get('query', ''), 'user': params.get('user', ''), 'slug': params.get('slug', ''), 'refreshed': 'true'}
		container_update(url_params)
	except: return

def media_artwork_choice(meta, changed_artwork=False):
	meta = dict(meta)
	all_images = meta.get('images', {'poster': [], 'fanart': [], 'clearlogo': [], 'banner': [], 'clearart': [], 'landscape': [], 'discart': [], 'keyart': []})
	if not metadata_user_info()['extra_fanart_enabled']:
		for k in ('banner', 'clearart', 'landscape', 'discart', 'keyart'): all_images.pop(k, None)
		all_images = [{k: [i for i in v if 'image.tmdb' in i] for k, v in all_images.items()}][0]
	if all(i == [] for i in all_images.values()): return notification(33069, 2000)
	kwargs = {'images': all_images, 'meta': meta}
	custom_images = open_window(('windows.artwork_chooser', 'SelectArtwork'), 'artwork_chooser.xml', **kwargs)
	if custom_images:
		from caches.meta_cache import metacache
		for image_type, image in custom_images.items():
			meta[image_type] = image
		metacache.set(meta['mediatype'], 'tmdb_id', meta)
		return kodi_refresh()

def trailer_choice(media_type, poster, tmdb_id, trailer_url, all_trailers=[]):
	if get_language() != 'en' and not trailer_url and not all_trailers:
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
			kwargs = {'items': json.dumps(list_items), 'window_xml': 'media_select.xml'}
			video_id = select_dialog([i['key'] for i in sorted_trailers], **kwargs)
			if video_id == None: return 'canceled'
		trailer_url = 'plugin://plugin.video.youtube/play/?video_id=%s' % video_id
	return trailer_url

def genres_choice(media_type, genres, poster, return_genres=False):
	from modules.meta_lists import movie_genres, tvshow_genres
	def _process_dicts(genre_str, _dict):
		final_genres_list = []
		append = final_genres_list.append
		for key, value in _dict.items():
			if key in genre_str: append({'genre': key, 'value': value})
		return final_genres_list
	if media_type in ('movie', 'movies'): genre_action, meta_type, action = movie_genres, 'movie', 'tmdb_movies_genres'
	else: genre_action, meta_type, action = tvshow_genres, 'tvshow', 'tmdb_tv_genres'
	genre_list = _process_dicts(genres, genre_action)
	if return_genres: return genre_list
	if len(genre_list) == 0:
		notification(32760, 2500)
		return None
	mode = 'build_%s_list' % meta_type
	list_items = [{'line1': i['genre'], 'icon': poster} for i in genre_list]
	kwargs = {'items': json.dumps(list_items), 'window_xml': 'media_select.xml'}
	return select_dialog([{'mode': mode, 'action': action, 'genre_id': i['value'][0]} for i in genre_list], **kwargs)

def imdb_keywords_choice(media_type, imdb_id, poster):
	from apis.imdb_api import imdb_keywords
	show_busy_dialog()
	keywords_info = imdb_keywords(imdb_id)
	if len(keywords_info) == 0:
		hide_busy_dialog()
		notification(32760, 2500)
		return None
	meta_type = 'movie' if media_type == 'movies' else 'tvshow'
	mode = 'build_%s_list' % meta_type
	list_items = [{'line1': i, 'icon': poster} for i in keywords_info]
	kwargs = {'items': json.dumps(list_items), 'enable_context_menu': 'true', 'media_type': media_type, 'window_xml': 'media_select.xml'}
	hide_busy_dialog()
	return select_dialog([{'mode': mode, 'action': 'imdb_keywords_list_contents', 'list_id': i, 'media_type': media_type} for i in keywords_info], **kwargs)

def imdb_videos_choice(videos, poster):
	try: videos = json.loads(videos)
	except: pass
	videos.sort(key=lambda x: x['quality_rank'])
	list_items = [{'line1': i['quality'], 'icon': poster} for i in videos]
	kwargs = {'items': json.dumps(list_items), 'window_xml': 'media_select.xml'}
	return select_dialog([i['url'] for i in videos], **kwargs)

def random_choice(params):
	meta, poster, return_choice, window_xml = params.get('meta'), params.get('poster'), params.get('return_choice', 'false'), params.get('window_xml', 'select.xml')
	meta = params.get('meta', None)	
	list_items = [{'line1': ls(32541), 'icon': poster}, {'line1': ls(32542), 'icon': poster}]
	choices = ['play_random', 'play_random_continual']
	kwargs = {'items': json.dumps(list_items), 'heading': ls(32540), 'window_xml': window_xml}
	choice = select_dialog(choices, **kwargs)
	if return_choice == 'true': return choice
	if choice == None: return
	from modules.episode_tools import EpisodeTools
	exec('EpisodeTools(meta).%s()' % choice)

def trakt_manager_choice(params):
	if not get_setting('trakt.user', ''): return notification(32760, 3500)
	icon = params.get('icon', None) or get_icon('trakt')
	choices = [('%s %s...' % (ls(32602), ls(32199)), 'Add'), ('%s %s...' % (ls(32603), ls(32199)), 'Remove')]
	list_items = [{'line1': item[0], 'icon': icon} for item in choices]
	kwargs = {'items': json.dumps(list_items), 'heading': ls(32198).replace('[B]', '').replace('[/B]', ''), 'window_xml': params.get('window_xml', 'select.xml')}
	choice = select_dialog([i[1] for i in choices], **kwargs)
	if choice == None: return
	from apis import trakt_api
	if choice == 'Add': trakt_api.trakt_add_to_list(params)
	else: trakt_api.trakt_remove_from_list(params)

def playback_choice(media_type, poster, meta, season, episode, window_xml):
	aliases = get_aliases_titles(make_alias_dict(meta, meta['title']))
	items = []
	items += [{'line': ls(32014), 'function': 'clear_and_rescrape'}]
	items += [{'line': ls(32185), 'function': 'scrape_with_default'}]
	items += [{'line': ls(32006), 'function': 'scrape_with_disabled'}]
	items += [{'line': ls(32807), 'function': 'scrape_with_filters_ignored'}]
	if aliases: items += [{'line': ls(32212), 'function': 'scrape_with_aliases'}]
	items += [{'line': ls(32135), 'function': 'scrape_with_custom_values'}]
	list_items = [{'line1': i['line'], 'icon': poster} for i in items]
	kwargs = {'items': json.dumps(list_items), 'heading': ls(32174), 'window_xml': window_xml}
	choice = select_dialog([i['function'] for i in items], **kwargs)
	if choice == None: return notification(32736, 2500)
	def clear_caches():
		from caches import clear_cache
		from caches.providers_cache import ExternalProvidersCache
		show_busy_dialog()
		clear_cache('internal_scrapers', silent=True)
		ExternalProvidersCache().delete_cache_single(media_type, str(meta['tmdb_id']))
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
			poster_main, poster_backup = get_art_provider()[0:2]
			poster = meta.get('custom_poster') or meta.get(poster_main) or meta.get(poster_backup) or poster_empty
			list_items = [{'line1': i, 'icon': poster} for i in aliases]
			kwargs = {'items': json.dumps(list_items), 'window_xml': 'media_select.xml'}
			custom_title = select_dialog(aliases, **kwargs)
			if custom_title == None: return notification(32736, 2500)
		custom_title = dialog.input(ls(32228), defaultt=custom_title)
		if not custom_title: return notification(32736, 2500)
		if media_type in ('movie', 'movies'): play_params = {'mode': 'playback.media', 'media_type': 'movie', 'tmdb_id': meta['tmdb_id'],
						'custom_title': custom_title, 'prescrape': 'false'}
		else: play_params = {'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': meta['tmdb_id'], 'season': season, 'episode': episode,
							'custom_title': custom_title, 'prescrape': 'false'}
	else:
		clear_caches()
		default_title, default_year = meta['title'], str(meta['year'])
		allscrapers_str, def_scrapers_str = '%s?' % ls(32006), '%s?' % ls(32185)
		title_str, year_str, season_str, episode_str = ls(32228), ls(32543), ls(32537), ls(32203).lower().capitalize()
		if media_type in ('movie', 'movies'): play_params = {'mode': 'playback.media', 'media_type': 'movie', 'tmdb_id': meta['tmdb_id'], 'prescrape': 'false'}
		else: play_params = {'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': meta['tmdb_id'], 'season': season, 'episode': episode, 'prescrape': 'false'}
		if aliases:
			if len(aliases) == 1: alias_title = aliases[0]
			poster_main, poster_backup = get_art_provider()[0:2]
			poster = meta.get('custom_poster') or meta.get(poster_main) or meta.get(poster_backup) or poster_empty
			list_items = [{'line1': i, 'icon': poster} for i in aliases]
			kwargs = {'items': json.dumps(list_items), 'window_xml': 'media_select.xml'}
			alias_title = select_dialog(aliases, **kwargs)
			if alias_title: custom_title = dialog.input(title_str, defaultt=alias_title)
			else: return notification(32736, 2500)
		else: custom_title = dialog.input(title_str, defaultt=default_title)
		if not custom_title: return notification(32736, 2500)
		def _process_params(default_value, custom_value, param_value):
			if custom_value and custom_value != default_value: play_params[param_value] = custom_value
		_process_params(default_title, custom_title, 'custom_title')
		custom_year = dialog.input(year_str, type=numeric_input, defaultt=default_year)
		_process_params(default_year, custom_year, 'custom_year')
		if media_type == 'episode':
			custom_season = dialog.input(season_str, type=numeric_input, defaultt=season)
			_process_params(season, custom_season, 'custom_season')
			custom_episode = dialog.input(episode_str, type=numeric_input, defaultt=episode)
			_process_params(episode, custom_episode, 'custom_episode')
			if any(i in play_params for i in ('custom_season', 'custom_episode')):
				if autoplay_next_episode(): _process_params('', 'true', 'disable_autoplay_next_episode')
		all_choice = confirm_progress_media(meta=meta, text=allscrapers_str, enable_buttons=True)
		if all_choice == None: return notification(32736, 2500)
		if not all_choice:
			default_choice = confirm_progress_media(meta=meta, text=def_scrapers_str, enable_buttons=True)
			if default_choice == None: return notification(32736, 2500)
			if default_choice: _process_params('', 'true', 'default_ext_only')
		else:  _process_params('', 'true', 'disabled_ext_ignored')
		disable_filters_choice = confirm_progress_media(meta=meta, text=32808, enable_buttons=True)
		if disable_filters_choice == None: return notification(32736, 2500)
		if disable_filters_choice:
			_process_params('', 'true', 'ignore_scrape_filters')
			set_property('fs_filterless_search', 'true')
	from modules.sources import Sources
	Sources().playback_prep(play_params)

def set_quality_choice(params):
	quality_setting = params.get('quality_setting')
	icon = params.get('icon', None) or get_icon('fen')
	include = ls(32188)
	dl = ['%s SD' % include, '%s 720p' % include, '%s 1080p' % include, '%s 4K' % include]
	fl = ['SD', '720p', '1080p', '4K']
	try: preselect = [fl.index(i) for i in get_setting(quality_setting).split(', ')]
	except: preselect = []
	list_items = [{'line1': item, 'icon': icon} for item in dl]
	kwargs = {'items': json.dumps(list_items), 'multi_choice': 'true', 'preselect': preselect, 'window_xml': params.get('window_xml', 'select.xml')}
	choice = select_dialog(fl, **kwargs)
	if choice is None: return
	if choice == []:
		ok_dialog(text=32574)
		return set_quality_choice(params)
	set_setting(quality_setting, ', '.join(choice))

def extras_lists_choice(params={}):
	fl = [2050, 2051, 2052, 2053, 2054, 2055, 2056, 2057, 2058, 2059, 2060, 2061, 2062]
	dl = [
			{'name': ls(32664),                            'image': img_url % 'DrqssE5'},
			{'name': ls(32503),                            'image': img_url % 'FZ6xrxr'},
			{'name': ls(32607),                            'image': img_url % 'CAvVerM'},
			{'name': ls(32984),                            'image': img_url % 'nz8PVph'},
			{'name': ls(32986),                            'image': img_url % 'jmFttcs'},
			{'name': ls(32989),                            'image': img_url % 'H5JLFoD'},
			{'name': ls(33032),                            'image': img_url % 'cdpBetd'},
			{'name': ls(32616),                            'image': img_url % 'mbPvLrG'},
			{'name': ls(32617),                            'image': img_url % '6TVW6r8'},
			{'name': '%s %s' % (ls(32612), ls(32543)),     'image': img_url % '6cVE5WT'},
			{'name': '%s %s' % (ls(32612), ls(32470)),     'image': img_url % 'ahJK4ZX'},
			{'name': '%s %s' % (ls(32612), ls(32480)),     'image': img_url % 'adtLIuW'},
			{'name': '%s %s' % (ls(32612), ls(32499)),     'image': img_url % 'wn2MpHK'}
			]
	try: preselect = [fl.index(i) for i in extras_enabled_menus()]
	except: preselect = []
	kwargs = {'items': json.dumps(dl), 'preselect': preselect}
	selection = open_window(('windows.extras', 'ExtrasChooser'), 'extras_chooser.xml', **kwargs)
	if selection  == []: return set_setting('extras.enabled_menus', 'noop')
	elif selection == None: return
	selection = [str(fl[i]) for i in selection]
	set_setting('extras.enabled_menus', ','.join(selection))

def set_language_filter_choice(params):
	from modules.meta_lists import language_choices
	filter_setting = params.get('filter_setting')
	lang_choices = language_choices
	lang_choices.pop('None')
	dl = list(lang_choices.keys())
	fl = list(lang_choices.values())
	try: preselect = [fl.index(i) for i in get_setting(filter_setting).split(', ')]
	except: preselect = []
	list_items = [{'line1': item} for item in dl]
	kwargs = {'items': json.dumps(list_items), 'multi_choice': 'true', 'preselect': preselect}
	choice = select_dialog(fl, **kwargs)
	if choice == None: return
	if choice == []: return set_setting(filter_setting, 'eng')
	set_setting(filter_setting, ', '.join(choice))

def easynews_use_custom_farm_choice(params={}):
	from apis.easynews_api import clear_media_results_database
	new_setting = 'True' if get_setting('easynews.use_custom_farm', 'False') == 'False' else 'False'
	set_setting('easynews.use_custom_farm', new_setting)
	clear_media_results_database()

def easynews_server_choice(params={}):
	from apis.easynews_api import ports, farms, clear_media_results_database
	test = [item.keys() for item in farms]
	list_items = [{'line1': item['name']} for item in farms]
	kwargs = {'items': json.dumps(list_items), 'heading': ls(32696)}
	farm_choice = select_dialog(farms, **kwargs)
	if not farm_choice: return notification(32736)
	list_items = [{'line1': str(item)} for item in ports]
	kwargs = {'items': json.dumps(list_items), 'heading': ls(32696)}
	port_choice = select_dialog(ports, **kwargs) or get_setting('easynews.port', '443')
	server_name = '%s:%s' % (farm_choice['name'], port_choice)
	pause_settings_change()
	set_setting('easynews.server_name', server_name)
	set_setting('easynews.farm', farm_choice['server_name'])
	set_setting('easynews.port', port_choice)
	unpause_settings_change()
	clear_media_results_database()

def enable_scrapers_choice(params={}):
	icon = params.get('icon', None) or get_icon('fen')
	scrapers = ['external', 'furk', 'easynews', 'rd_cloud', 'pm_cloud', 'ad_cloud', 'folders']
	cloud_scrapers = {'rd_cloud': 'rd.enabled', 'pm_cloud': 'pm.enabled', 'ad_cloud': 'ad.enabled'}
	scraper_names = [ls(32118).upper(), ls(32069).upper(), ls(32070).upper(), ls(32098).upper(), ls(32097).upper(), ls(32099).upper(), ls(32108).upper()]
	preselect = [scrapers.index(i) for i in active_internal_scrapers()]
	list_items = [{'line1': item, 'icon': icon} for item in scraper_names]
	kwargs = {'items': json.dumps(list_items), 'multi_choice': 'true', 'preselect': preselect, 'window_xml': params.get('window_xml', 'select.xml')}
	choice = select_dialog(scrapers, **kwargs)
	if choice is None: return
	for i in scrapers:
		set_setting('provider.%s' % i, ('true' if i in choice else 'false'))
		if i in cloud_scrapers and i in choice: set_setting(cloud_scrapers[i], 'true')

def folder_sources_choice(params):
	if params['folder_path']:
		browse = confirm_dialog(text=33109, ok_label=32838, cancel_label=33108, default_control=10)
		if browse is None: return
		if browse: function, params['mode'] = container_update, 'navigator.folder_navigator'
		else: function, params['mode'] = run_plugin, 'folder_scraper_manager_choice'
	else: function, params['mode'] = run_plugin, 'folder_scraper_manager_choice'
	function(params)

def folder_scraper_manager_choice(params):
	def _set_settings(refresh=True):
		set_setting(name_setting % setting_id, display_name)
		set_setting(settings_dict[media_type] % setting_id, folder_path)
		sleep(250)
		if refresh: kodi_refresh()
	setting_id, media_type, folder_path = params['setting_id'], params['media_type'], params.get('folder_path', '')
	display_name, default_name = params.get('display_name', ''), params['default_name']
	set_folder_path = True
	name_setting, movie_dir_setting, tvshow_dir_setting = '%s.display_name', '%s.movies_directory', '%s.tv_shows_directory'
	settings_dict = {'movie': movie_dir_setting, 'tvshow': tvshow_dir_setting}
	if folder_path:
		confirm = confirm_dialog(heading=display_name, text=ls(32529) % default_name, ok_label=32531, cancel_label=32530)
		if confirm is None: return
		elif confirm:
			ok_dialog(heading=default_name, text=ls(32532) % default_name)
			display_name, folder_path = default_name, 'None'
			_set_settings(refresh=False)
			media_type = 'tvshow' if media_type == 'movie' else 'movie'
			return _set_settings()
		else:
			if not confirm_dialog(heading=display_name, text=32640, default_control=10): set_folder_path = False
	if set_folder_path:
		folder_path = dialog.browse(0, fen_str, '')
		if not folder_path:
			if confirm_dialog(heading=display_name, text=32704): return folder_scraper_manager_choice(params)
			else: return	
	display_name = dialog.input(ls(32115), defaultt=display_name or setting_id)
	if not display_name:
		if confirm_dialog(heading=display_name, text=32714): return folder_scraper_manager_choice(params)
		else: return
	_set_settings()

def results_sorting_choice(params={}):
	quality, provider, size = ls(32241), ls(32583), ls(32584)
	choices = [('%s, %s, %s' % (quality, provider, size), '0'), ('%s, %s, %s' % (quality, size, provider), '1'), ('%s, %s, %s' % (provider, quality, size), '2'),
			   ('%s, %s, %s' % (provider, size, quality), '3'), ('%s, %s, %s' % (size, quality, provider), '4'), ('%s, %s, %s' % (size, provider, quality), '5')]
	list_items = [{'line1': item[0]} for item in choices]
	kwargs = {'items': json.dumps(list_items)}
	choice = select_dialog(choices, **kwargs)
	if choice:
		set_setting('results.sort_order_display', choice[0])
		set_setting('results.sort_order', choice[1])

def results_format_choice(params={}):
	xml_choices = [
					('List',                 img_url % '5qdaSAr'),
					('InfoList',             img_url % 'wePo8Vv'),
					('MediaList',            img_url % 'xXWixYv'),
					('Rows',                 img_url % '44OzIVW'),
					('Shift',                img_url % 'Z8AtLTn'),
					('Thumbs',               img_url % 'TLHIutH'),
					]
	choice = open_window(('windows.sources', 'SourceResultsChooser'), 'sources_chooser.xml', xml_choices=xml_choices)
	if choice: set_setting('results.format', choice)

def set_subtitle_choice():
	choices = ((ls(32192), '0'), (ls(32193), '1'), (ls(32027), '2'))
	list_items = [{'line1': item[0]} for item in choices]
	kwargs = {'items': json.dumps(list_items)}
	choice = select_dialog([i[1] for i in choices], **kwargs)
	if choice: return set_setting('subtitles.subs_action', choice)

def clear_favorites_choice(params={}):
	favorites_str = ls(32453)
	fl = [('%s %s' % (ls(32028), favorites_str), 'movie'), ('%s %s' % (ls(32029), favorites_str), 'tvshow')]
	list_items = [{'line1': item[0]} for item in fl]
	kwargs = {'items': json.dumps(list_items), 'heading': ls(32036)}
	media_type = select_dialog([item[1] for item in fl], **kwargs)
	if media_type == None: return
	if not confirm_dialog(): return
	from caches.favorites import favorites
	favorites.clear_favorites(media_type)
	notification(32576, 3000)

def favorites_choice(params):
	media_type, tmdb_id, title = params.get('media_type'), params.get('tmdb_id'), params.get('title')
	from caches.favorites import favorites
	current_favorites = favorites.get_favorites(media_type)
	if any(i['tmdb_id'] == tmdb_id for i in current_favorites): function, text, refresh = favorites.delete_favourite, '%s %s?' % (ls(32603), ls(32453)), 'true'
	else: function, text, refresh = favorites.set_favourite, '%s %s?' % (ls(32602), ls(32453)), 'false'
	if not confirm_dialog(heading=title, text=text): return
	success = function(media_type, tmdb_id, title)
	refresh = params.get('refresh', refresh)
	if success:
		if refresh == 'true': kodi_refresh()
		notification(32576, 3500)
	else: notification(32574, 3500)

def scraper_quality_color_choice(params):
	setting = params.get('setting')
	default_setting = get_setting(setting)
	chosen_color = color_choice({'default_setting': default_setting})
	if chosen_color:
		set_setting(setting, chosen_color)
		set_setting('%s_name' % setting, '[COLOR=%s]%s[/COLOR]' % (chosen_color, chosen_color))

def scraper_color_choice(params):
	setting = params.get('setting')
	choices = [('furk', 'provider.furk_colour'),
				('easynews', 'provider.easynews_colour'),
				('debrid_cloud', 'provider.debrid_cloud_colour'),
				('folders', 'provider.folders_colour'),
				('hoster', 'hoster.identify'),
				('torrent', 'torrent.identify'),
				('rd', 'provider.rd_colour'),
				('pm', 'provider.pm_colour'),
				('ad', 'provider.ad_colour')]
	setting = [i[1] for i in choices if i[0] == setting][0]
	default_setting = get_setting(setting)
	chosen_color = color_choice({'default_setting': default_setting})
	if chosen_color:
		set_setting(setting, chosen_color)
		set_setting('%s_name' % setting, '[COLOR=%s]%s[/COLOR]' % (chosen_color, chosen_color))

def highlight_color_choice(params={}):
	default_setting = get_setting('fen.highlight')
	chosen_color = color_choice({'default_setting': default_setting})
	if chosen_color:
		set_setting('fen.highlight', chosen_color)
		set_setting('fen.highlight_name', '[COLOR=%s]%s[/COLOR]' % (chosen_color, chosen_color))
		set_property(highlight_prop, chosen_color)

def color_choice(params):
	return open_window(('windows.color_chooser', 'SelectColor'), 'color_chooser.xml', default_setting=params.get('default_setting', None))

def meta_language_choice(params={}):
	from modules.meta_lists import meta_languages
	langs = meta_languages
	langs.sort(key=lambda x: x['name'])
	list_items = [{'line1': i['name']} for i in langs]
	kwargs = {'items': json.dumps(list_items), 'heading': ls(32145)}
	choice = select_dialog(langs, **kwargs)
	if choice == None: return None
	from caches.meta_cache import delete_meta_cache
	set_setting('meta_language', choice['iso'])
	set_setting('meta_language_display', choice['name'])
	delete_meta_cache(silent=True)

def external_scrapers_choice(params={}):
	icon = translate_path('special://home/addons/script.module.cocoscrapers/icon.png')
	all_color, hosters_color, torrent_color = 'mediumvioletred', get_setting('hoster.identify'), get_setting('torrent.identify')
	enable_string, disable_string, specific_string, all_string = ls(32055), ls(32024), ls(32536), ls(32129)
	scrapers_string, hosters_string, torrent_string = ls(32533), ls(33031), ls(32535)
	fs_default_string = ls(32137)
	all_scrapers_string = '%s %s' % (all_string, scrapers_string)
	hosters_scrapers_string = '%s %s' % (hosters_string, scrapers_string)
	torrent_scrapers_string = '%s %s' % (torrent_string, scrapers_string)
	enable_string_base = '%s %s %s %s' % (enable_string, all_string, '%s', scrapers_string)
	disable_string_base = '%s %s %s %s' % (disable_string, all_string, '%s', scrapers_string)
	enable_disable_string_base = '%s/%s %s %s %s' % (enable_string, disable_string, specific_string, '%s', scrapers_string)
	all_scrapers_base = '[COLOR %s]%s [/COLOR]' % (all_color, all_scrapers_string.upper())
	debrid_scrapers_base = '[COLOR %s]%s [/COLOR]' % (hosters_color, hosters_scrapers_string.upper())
	torrent_scrapers_base = '[COLOR %s]%s [/COLOR]' % (torrent_color, torrent_scrapers_string.upper())
	tools_menu = \
		[(all_scrapers_base, fs_default_string, {'mode': 'set_default_scrapers'}),
		(all_scrapers_base, enable_string_base % '', {'mode': 'toggle_all', 'folder': 'all', 'setting': 'true'}),
		(all_scrapers_base, disable_string_base % '', {'mode': 'toggle_all', 'folder': 'all', 'setting': 'false'}),
		(all_scrapers_base, enable_disable_string_base % '', {'mode': 'enable_disable', 'folder': 'all'}),
		(debrid_scrapers_base, enable_string_base % hosters_string, {'mode': 'toggle_all', 'folder': 'hosters', 'setting': 'true'}),
		(debrid_scrapers_base, disable_string_base % hosters_string, {'mode': 'toggle_all', 'folder': 'hosters', 'setting': 'false'}),
		(debrid_scrapers_base, enable_disable_string_base % hosters_string, {'mode': 'enable_disable', 'folder': 'hosters'}),
		(torrent_scrapers_base, enable_string_base % torrent_string, {'mode': 'toggle_all', 'folder': 'torrents', 'setting': 'true'}),
		(torrent_scrapers_base, disable_string_base % torrent_string, {'mode': 'toggle_all', 'folder': 'torrents', 'setting': 'false'}),
		(torrent_scrapers_base, enable_disable_string_base % torrent_string, {'mode': 'enable_disable', 'folder': 'torrents'})]
	list_items = [{'line1': item[0], 'line2': item[1], 'icon': icon} for item in tools_menu]
	kwargs = {'items': json.dumps(list_items), 'multi_line': 'true'}
	chosen_tool = select_dialog(tools_menu, **kwargs)
	if chosen_tool == None: return
	params = chosen_tool[2]
	mode = params['mode']
	if mode == 'toggle_all': toggle_all(params['folder'], params['setting'])
	elif mode == 'enable_disable': enable_disable(params['folder'])
	elif mode == 'set_default_scrapers': set_default_scrapers()
	sleep(500)
	return external_scrapers_choice()

def options_menu_choice(params, meta=None):
	def strip_bold(_str):
		return _str.replace('[B]', '').replace('[/B]', '')
	def _builder():
		for item in listing: yield {'line1': item[0], 'line2': item[1] or item[0], 'icon': poster}
	pause_settings_change()
	params_get = params.get
	tmdb_id, content, poster, window_xml = params_get('tmdb_id', None), params_get('content', None), params_get('poster', None), params_get('window_xml', 'select.xml')
	is_widget, from_extras = params_get('is_widget') in (True, 'True', 'true'), params_get('from_extras', 'false') == 'true'
	season, episode = params_get('season', ''), params_get('episode', '')
	if not content: content = container_content()[:-1]
	single_ep_list = ('episode.progress', 'episode.recently_watched', 'episode.next_trakt', 'episode.next_fen', 'episode.trakt_recently_aired', 'episode.trakt_calendar')
	menu_type = content
	if content.startswith('episode.'): content = 'episode'
	if not meta:
		function = metadata.movie_meta if content == 'movie' else metadata.tvshow_meta
		meta = function('tmdb_id', tmdb_id, metadata_user_info(), get_datetime())
	meta_get = meta.get
	rootname = meta_get('rootname', None)
	window_action = 'ActivateWindow(Videos,%s,return)' if is_widget else 'Container.Update(%s)'
	title, year, imdb_id, tvdb_id = meta_get('title'), meta_get('year'), meta_get('imdb_id', None), meta_get('tvdb_id', None)
	listing = []
	listing_append = listing.append
	if get_property(custom_context_prop) == 'true' and not from_extras:
		try: playcount = int(params_get('playcount', '0'))
		except: playcount = 0
		try: progress = int(params_get('progress', '0'))
		except: progress = 0
		if menu_type in ('movie', 'tvshow'):
			if extras_open_action(content):
				if menu_type == 'movie': listing_append((strip_bold(ls(32174)), '', 'playback'))
				else: listing_append((ls(32838), '%s %s' % (ls(32838), title), 'browse'))
			else: listing_append((strip_bold(ls(32645)).replace('...', ''), '', 'extras'))
			if menu_type == 'movie':
				if playcount: watched_action, watchedstr = 'mark_as_unwatched', strip_bold(ls(32643)).replace(' %s', '')
				else: watched_action, watchedstr = 'mark_as_watched', strip_bold(ls(32642)).replace(' %s', '')
				listing_append((watchedstr, '', 'mark_movie'))
				if progress: listing_append((strip_bold(ls(32651)), '', 'clear_progress'))
			else:
				if not playcount: listing_append((strip_bold(ls(32642)).replace(' %s', ''), '', 'mark_watched_tvshow'))
				if progress: listing_append((strip_bold(ls(32643)).replace(' %s', ''), '', 'mark_unwatched_tvshow'))
			if not is_widget: listing_append((strip_bold(ls(32649) if menu_type == 'movie' else ls(32650)), '', 'exit_menu'))
		else:
			listing_append((strip_bold(ls(32645)).replace('...', ''), '', 'extras'))
			if menu_type == 'season':
				if not playcount: listing_append((strip_bold(ls(32642)).replace(' %s', ''), '', 'mark_watched_season'))
				if progress: listing_append((strip_bold(ls(32643)).replace(' %s', ''), '', 'mark_unwatched_season'))
			else:
				if playcount: watched_action, watchedstr = 'mark_as_unwatched', strip_bold(ls(32643)).replace(' %s', '')
				else: watched_action, watchedstr = 'mark_as_watched', strip_bold(ls(32642)).replace(' %s', '')
				listing_append((watchedstr, '', 'mark_episode'))
				if progress: listing_append((strip_bold(ls(32651)), '', 'clear_progress'))
		if is_widget: listing_append((ls(32611), '', 'refresh_widgets'))
	if menu_type in ('movie', 'episode') or menu_type in single_ep_list:
		listing_append((ls(32187), '%s %s' % (ls(32533), ls(32841)), 'playback_choice'))
		if menu_type in single_ep_list:
			listing_append((ls(32838), '%s %s' % (ls(32838), title), 'browse'))
			listing_append((ls(32544).replace(' %s', ''), ls(32544) % (title, season), 'browse_season'))
			if menu_type == 'episode.next_trakt' and watched_indicators() == 1: listing_append((ls(32599), '', 'nextep_manager'))
	if menu_type in ('movie', 'tvshow'):
		listing_append((ls(32198), '', 'trakt_manager'))
		listing_append((ls(32197), '', 'favorites_choice'))
		listing_append((ls(32503), ls(32004) % rootname, 'recommended'))
		if menu_type == 'tvshow': listing_append((ls(32613), ls(32004) % rootname, 'random'))
	if menu_type in ('movie', 'episode') or menu_type in single_ep_list:
		base_str1, base_str2, on_str, off_str = '%s%s', '%s: [B]%s[/B]' % (ls(32598), '%s'), ls(32090), ls(32027)
		if auto_play(content): autoplay_status, autoplay_toggle, quality_setting = on_str, 'false', 'autoplay_quality_%s' % content
		else: autoplay_status, autoplay_toggle, quality_setting = off_str, 'true', 'results_quality_%s' % content
		active_int_scrapers = [i.replace('_', '') for i in active_internal_scrapers()]
		current_scrapers_status = ', '.join([i for i in active_int_scrapers]) if len(active_int_scrapers) > 0 else 'N/A'
		current_quality_status =  ', '.join(quality_filter(quality_setting))
		listing_append((base_str1 % (ls(32175), ' (%s)' % content), base_str2 % autoplay_status, 'toggle_autoplay'))
		if menu_type == 'episode' or menu_type in single_ep_list:
			if autoplay_status == on_str:
				autoplay_next_status, autoplay_next_toggle = (on_str, 'false') if autoplay_next_episode() else (off_str, 'true')
				listing_append((base_str1 % (ls(32178), ''), base_str2 % autoplay_next_status, 'toggle_autoplay_next'))
			else:
				autoscrape_next_status, autoscrape_next_toggle = (on_str, 'false') if autoscrape_next_episode() else (off_str, 'true')
				listing_append((base_str1 % (ls(33086), ''), base_str2 % autoscrape_next_status, 'toggle_autoscrape_next'))
		listing_append((base_str1 % (ls(32105), ' (%s)' % content), base_str2 % current_quality_status, 'set_quality'))
		listing_append((base_str1 % ('', '%s %s' % (ls(32055), ls(32533))), base_str2 % current_scrapers_status, 'enable_scrapers'))
	if menu_type in ('movie', 'tvshow') and not from_extras:
		listing_append((ls(32604) % (ls(32028) if menu_type == 'movie' else ls(32029)), ls(32497) % rootname, 'clear_media_cache'))
		listing_append((ls(33043), ls(33066) % rootname, 'set_media_artwork'))
	if menu_type in ('movie', 'episode') or menu_type in single_ep_list: listing_append((ls(32637), '', 'clear_scrapers_cache'))
	listing_append(('%s %s' % (ls(32118), ls(32513)), '', 'open_external_scrapers_choice'))
	listing_append(('%s %s %s' % (ls(32641), ls(32036), ls(32247)), '', 'open_fen_settings'))
	list_items = list(_builder())
	heading = rootname or strip_bold(ls(32646))
	kwargs = {'items': json.dumps(list_items), 'heading': heading, 'multi_line': 'true', 'window_xml': window_xml}
	choice = select_dialog([i[2] for i in listing], **kwargs)
	if choice in closing_options: unpause_settings_change()
	if choice == None: return
	if choice == 'playback':
		return run_plugin({'mode': 'playback.media', 'media_type': 'movie', 'tmdb_id': tmdb_id})
	elif choice == 'extras':
		return extras_menu_choice({'tmdb_id': tmdb_id, 'media_type': content, 'is_widget': str(is_widget)})
	elif choice == 'mark_movie':
		return run_plugin({'mode': 'watched_status.mark_movie', 'action': watched_action, 'title': title, 'year': year, 'tmdb_id': tmdb_id})
	elif choice == 'mark_episode':
		return run_plugin({'mode': 'watched_status.mark_episode', 'action': watched_action, 'title': title, 'year': year, 'tmdb_id': tmdb_id,
							'tvdb_id': tvdb_id, 'season': season, 'episode': episode})
	elif choice == 'mark_watched_tvshow':
		return run_plugin({'mode': 'watched_status.mark_tvshow', 'action': 'mark_as_watched', 'title': title, 'year': year, 'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id})
	elif choice == 'mark_unwatched_tvshow':
		return run_plugin({'mode': 'watched_status.mark_tvshow', 'action': 'mark_as_unwatched', 'title': title, 'year': year, 'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id})
	elif choice == 'mark_watched_season':
		return run_plugin({'mode': 'watched_status.mark_season', 'action': 'mark_as_watched', 'title': title, 'year': year, 'tmdb_id': tmdb_id,
							'tvdb_id': tvdb_id, 'season': season})
	elif choice == 'mark_unwatched_season':
		return run_plugin({'mode': 'watched_status.mark_season', 'action': 'mark_as_unwatched', 'title': title, 'year': year, 'tmdb_id': tmdb_id,
							'tvdb_id': tvdb_id, 'season': season})
	elif choice == 'clear_progress':
		return run_plugin({'mode': 'watched_status.erase_bookmark', 'media_type': content, 'tmdb_id': tmdb_id, 'season': season, 'episode': episode, 'refresh': 'true'})
	elif choice == 'refresh_widgets':
		return kodi_refresh()
	elif choice == 'clear_media_cache':
		return refresh_cached_data(meta)
	elif choice == 'set_media_artwork':
		return media_artwork_choice(meta)
	elif choice == 'clear_scrapers_cache':
		return clear_scrapers_cache()
	elif choice == 'open_external_scrapers_choice':
		return external_scrapers_choice()
	elif choice == 'open_fen_settings':
		return open_settings('0.0')
	elif choice == 'playback_choice':
		return playback_choice(content, poster, meta, season, episode, window_xml)
	elif choice == 'browse':
		return execute_builtin(window_action % build_url({'mode': 'build_season_list', 'tmdb_id': tmdb_id}))
	elif choice == 'browse_season':
		return execute_builtin(window_action % build_url({'mode': 'build_episode_list', 'tmdb_id': tmdb_id, 'season': season}))
	elif choice == 'nextep_manager':
		return execute_builtin(window_action % build_url({'mode': 'build_next_episode_manager'}))
	elif choice == 'recommended':
		close_all_dialog()
		mode, action = ('build_movie_list', 'tmdb_movies_recommendations') if menu_type == 'movie' else ('build_tvshow_list', 'tmdb_tv_recommendations')
		return execute_builtin(window_action % build_url({'mode': mode, 'action': action, 'tmdb_id': tmdb_id}))
	elif choice == 'random':
		close_all_dialog()
		return random_choice({'meta': meta, 'poster': poster})
	elif choice == 'trakt_manager':
		return trakt_manager_choice({'tmdb_id': tmdb_id, 'imdb_id': meta_get('imdb_id'), 'tvdb_id': meta_get('tvdb_id', 'None'),
									'media_type': content, 'window_xml': window_xml, 'icon': poster})
	elif choice == 'favorites_choice':
		return favorites_choice({'media_type': content, 'tmdb_id': tmdb_id, 'title': meta_get('title')})
	elif choice == 'exit_menu':
		return execute_builtin('Container.Refresh(%s)' % params_get('exit_menu', ''))
	elif choice == 'toggle_autoplay':
		set_setting('auto_play_%s' % content, autoplay_toggle)
	elif choice == 'toggle_autoplay_next':
		set_setting('autoplay_next_episode', autoplay_next_toggle)
	elif choice == 'toggle_autoscrape_next':
		set_setting('autoscrape_next_episode', autoscrape_next_toggle)
	elif choice == 'set_quality':
		set_quality_choice({'quality_setting': 'autoplay_quality_%s' % content if autoplay_status == on_str else 'results_quality_%s' % content,
							'window_xml': window_xml, 'icon': poster})
	elif choice == 'enable_scrapers':
		enable_scrapers_choice({'window_xml': window_xml, 'icon': poster})
	make_settings_dict()
	make_window_properties(override=True)
	options_menu_choice(params, meta=meta)

def person_search_choice(params):
	from indexers.people import person_data_dialog
	person_data_dialog({'query': params['query'], 'is_widget': params.get('is_widget', 'true' if external_browse() else 'false')})

def extras_menu_choice(params):
	show_busy_dialog()
	media_type = params['media_type']
	function = metadata.movie_meta if media_type == 'movie' else metadata.tvshow_meta
	meta = function('tmdb_id', params['tmdb_id'], metadata_user_info(), get_datetime())
	hide_busy_dialog()
	open_window(('windows.extras', 'Extras'), 'extras.xml', meta=meta, is_widget=params.get('is_widget', 'true' if external_browse() else 'false'), options_media_type=media_type)

def media_extra_info_choice(params):
	media_type, meta = params.get('media_type'), params.get('meta')
	extra_info, body = meta.get('extra_info', None), []
	append = body.append
	tagline_str, premiered_str, rating_str, votes_str, runtime_str = ls(32619), ls(32620), ls(32621), ls(32623), ls(32622)
	genres_str, budget_str, revenue_str, director_str, writer_str = ls(32624), ls(32625), ls(32626), ls(32627), ls(32628)
	studio_str, collection_str, homepage_str, status_str, type_str, classification_str = ls(32615), ls(32499), ls(32629), ls(32630), ls(32631), ls(32632)
	network_str, created_by_str, last_aired_str, next_aired_str, seasons_str, episodes_str = ls(32480), ls(32633), ls(32634), ls(32635), ls(32636), ls(32506)
	try:
		if media_type == 'movie':
			def _process_budget_revenue(info):
				if isinstance(info, int): info = '${:,}'.format(info)
				return info
			if meta['tagline']: append('[B]%s:[/B] %s' % (tagline_str, meta['tagline']))
			aliases = get_aliases_titles(make_alias_dict(meta, meta['title']))
			if aliases: append('[B]%s:[/B] %s' % (ls(33044), ', '.join(aliases)))
			append('[B]%s:[/B] %s' % (status_str, extra_info['status']))
			append('[B]%s:[/B] %s' % (premiered_str, meta['premiered']))
			append('[B]%s:[/B] %s (%s %s)' % (rating_str, str(round(meta['rating'], 1)), meta['votes'], votes_str))
			append('[B]%s:[/B] %s mins' % (runtime_str, int(float(meta['duration'])/60)))
			append('[B]%s:[/B] %s' % (genres_str, meta['genre']))
			append('[B]%s:[/B] %s' % (budget_str, _process_budget_revenue(extra_info['budget'])))
			append('[B]%s:[/B] %s' % (revenue_str, _process_budget_revenue(extra_info['revenue'])))
			append('[B]%s:[/B] %s' % (director_str, meta['director']))
			append('[B]%s:[/B] %s' % (writer_str, meta['writer'] or 'N/A'))
			append('[B]%s:[/B] %s' % (studio_str, meta['studio'] or 'N/A'))
			if extra_info['collection_name']: append('[B]%s:[/B] %s' % (collection_str, extra_info['collection_name']))
			append('[B]%s:[/B] %s' % (homepage_str, extra_info['homepage']))
		else:
			append('[B]%s:[/B] %s' % (type_str, extra_info['type']))
			if meta['tagline']: append('[B]%s:[/B] %s' % (tagline_str, meta['tagline']))
			aliases = get_aliases_titles(make_alias_dict(meta, meta['title']))
			if aliases: append('[B]%s:[/B] %s' % (ls(33044), ', '.join(aliases)))
			append('[B]%s:[/B] %s' % (status_str, extra_info['status']))
			append('[B]%s:[/B] %s' % (premiered_str, meta['premiered']))
			append('[B]%s:[/B] %s (%s %s)' % (rating_str, str(round(meta['rating'], 1)), meta['votes'], votes_str))
			append('[B]%s:[/B] %d mins' % (runtime_str, int(float(meta['duration'])/60)))
			append('[B]%s:[/B] %s' % (classification_str, meta['mpaa']))
			append('[B]%s:[/B] %s' % (genres_str, meta['genre']))
			append('[B]%s:[/B] %s' % (network_str, meta['studio']))
			append('[B]%s:[/B] %s' % (created_by_str, extra_info['created_by']))
			if extra_info.get('last_episode_to_air', False):
				last_ep = extra_info['last_episode_to_air']
				lastep_str = '[%s] S%.2dE%.2d - %s' % (last_ep['air_date'], last_ep['season_number'], last_ep['episode_number'], last_ep['name'])
				append('[B]%s:[/B] %s' % (last_aired_str, lastep_str))
			if extra_info.get('next_episode_to_air', False):
				next_ep = extra_info['next_episode_to_air']
				nextep_str = '[%s] S%.2dE%.2d - %s' % (next_ep['air_date'], next_ep['season_number'], next_ep['episode_number'], next_ep['name'])
				append('[B]%s:[/B] %s' % (next_aired_str, nextep_str))
			append('[B]%s:[/B] %s' % (seasons_str, meta['total_seasons']))
			append('[B]%s:[/B] %s' % (episodes_str, meta['total_aired_eps']))
			append('[B]%s:[/B] %s' % (homepage_str, extra_info['homepage']))
	except: return notification(32574, 2000)
	return '[CR][CR]'.join(body)
