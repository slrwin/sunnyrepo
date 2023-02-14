# -*- coding: utf-8 -*-
from apis.trakt_api import trakt_fetch_collection_watchlist, trakt_get_hidden_items, trakt_get_my_calendar
from caches.favorites import favorites
from modules import kodi_utils, settings, watched_status as ws
from modules.metadata import tvshow_meta, episodes_meta, all_episodes_meta
from modules.utils import jsondate_to_datetime, adjust_premiered_date, make_day, get_datetime, title_key, date_difference, make_thread_list_enumerate
# logger = kodi_utils.logger

remove_keys, set_view_mode, external_browse, sys = kodi_utils.remove_keys, kodi_utils.set_view_mode, kodi_utils.external_browse, kodi_utils.sys
add_items, set_content, set_sort_method, end_directory = kodi_utils.add_items, kodi_utils.set_content, kodi_utils.set_sort_method, kodi_utils.end_directory
ls, make_listitem, build_url, dict_removals, sys = kodi_utils.local_string, kodi_utils.make_listitem, kodi_utils.build_url, kodi_utils.episode_dict_removals, kodi_utils.sys
kodi_version, xbmc_actor = kodi_utils.kodi_version, kodi_utils.xbmc_actor
get_art_provider, show_specials, calendar_sort_order, ignore_articles = settings.get_art_provider, settings.show_specials, settings.calendar_sort_order, settings.ignore_articles
metadata_user_info, watched_indicators_info, show_unaired_info = settings.metadata_user_info, settings.watched_indicators, settings.show_unaired
nextep_content_settings, nextep_display_settings = settings.nextep_content_settings, settings.nextep_display_settings
date_offset_info, default_all_episodes = settings.date_offset, settings.default_all_episodes
single_ep_display_title, single_ep_format = settings.single_ep_display_title, settings.single_ep_format
tv_meta_function, episodes_meta_function, all_episodes_meta_function = tvshow_meta, episodes_meta, all_episodes_meta
adjust_premiered_date_function, jsondate_to_datetime_function = adjust_premiered_date, jsondate_to_datetime
date_difference_function, make_day_function, title_key_function, get_datetime_function = date_difference, make_day, title_key, get_datetime
get_progress_percent, get_watched_status, get_watched_info, get_bookmarks = ws.get_progress_percent, ws.get_watched_status_episode, ws.get_watched_info_tv, ws.get_bookmarks
get_in_progress_episodes, get_next_episodes, get_recently_watched = ws.get_in_progress_episodes, ws.get_next_episodes, ws.get_recently_watched
string, fen_str, trakt_str, watched_str, unwatched_str =  str, ls(32036), ls(32037), ls(32642), ls(32643)
extras_str, options_str, clearprog_str, refr_widg_str = ls(32645), ls(32646), ls(32651), ls(40001)
build_content, poster_empty, fanart_empty, make_placeholder = kodi_utils.build_content, kodi_utils.empty_poster, kodi_utils.addon_fanart, kodi_utils.make_placeholder_listitem
run_plugin, unaired_label, tmdb_poster_prefix = 'RunPlugin(%s)', '[COLOR red][I]%s[/I][/COLOR]', 'https://image.tmdb.org/t/p/'
upper = string.upper
view_mode, content_type = 'view.episodes', 'episodes'

def build_episode_list(params):
	def _process():
		for item in episodes_data:
			try:
				cm = []
				listitem = make_listitem()
				set_properties = listitem.setProperties
				cm_append = cm.append
				item_get = item.get
				season, episode, ep_name = item_get('season'), item_get('episode'), item_get('title')
				episode_date, premiered = adjust_premiered_date_function(item_get('premiered'), adjust_hours)
				playcount, overlay = get_watched_status(watched_info, string(tmdb_id), season, episode)
				progress = get_progress_percent(bookmarks, tmdb_id, season, episode)
				tmdb_thumb = item_get('thumb', None)
				if fanart_enabled:
					if fanart_default: thumb = tmdb_thumb or season_art.get('seasonthumb_%s' % season, '') or show_fanart
					else: thumb = tmdb_thumb or show_fanart or season_art.get('seasonthumb_%s' % season, '')
				else: thumb = tmdb_thumb or show_fanart
				if not item_get('duration'): item['duration'] = show_duration
				options_params = build_url({'mode': 'options_menu_choice', 'content': 'episode', 'tmdb_id': tmdb_id, 'season': season, 'episode': episode,
											'poster': show_poster, 'playcount': playcount, 'progress': progress, 'is_widget': is_widget})
				extras_params = build_url({'mode': 'extras_menu_choice', 'tmdb_id': tmdb_id, 'media_type': 'episode', 'is_widget': is_widget})
				url_params = build_url({'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': tmdb_id, 'season': season, 'episode': episode})
				if not episode_date or current_date < episode_date:
					if not show_unaired: continue
					if season != 0:
						display, unaired = unaired_label % ep_name, True
						item['title'] = display
				else: display, unaired = ep_name, False
				cm_append((extras_str, run_plugin % extras_params))
				cm_append((options_str, run_plugin % options_params))
				clearprog_params, unwatched_params, watched_params = '', '', ''
				if not unaired:
					if playcount:
						if hide_watched: continue
						unwatched_params = build_url({'mode': 'watched_status.mark_episode', 'action': 'mark_as_unwatched', 'tmdb_id': tmdb_id,
													'tvdb_id': tvdb_id, 'season': season, 'episode': episode,  'title': title, 'year': year})
						cm_append((unwatched_str % watched_title, run_plugin % unwatched_params))
					else:
						watched_params = build_url({'mode': 'watched_status.mark_episode', 'action': 'mark_as_watched', 'tmdb_id': tmdb_id,
													'tvdb_id': tvdb_id, 'season': season, 'episode': episode,  'title': title, 'year': year})
						cm_append((watched_str % watched_title, run_plugin % watched_params))
					if progress:
						clearprog_params = build_url({'mode': 'watched_status.erase_bookmark', 'media_type': 'episode', 'tmdb_id': tmdb_id,
													'season': season, 'episode': episode, 'refresh': 'true'})
						cm_append((clearprog_str, run_plugin % clearprog_params))
						set_properties({'watchedprogress': progress, 'resumetime': progress, 'fen.in_progress': 'true'})
				if kodi_version >= 20:
					if is_widget: cm_append((refr_widg_str, run_plugin % build_url({'mode': 'kodi_refresh'})))
					info_tag = listitem.getVideoInfoTag()
					info_tag.setMediaType('episode')
					info_tag.setTitle(display)
					info_tag.setOriginalTitle(orig_title)
					info_tag.setTvShowTitle(title)
					info_tag.setTvShowStatus(show_status)
					info_tag.setSeason(season)
					info_tag.setEpisode(episode)
					info_tag.setPlot(item_get('plot'))
					info_tag.setYear(int(year))
					info_tag.setRating(item_get('rating'))
					info_tag.setVotes(item_get('votes'))
					info_tag.setMpaa(mpaa)
					info_tag.setDuration(item_get('duration'))
					info_tag.setPlaycount(playcount)
					info_tag.setTrailer(trailer)
					info_tag.setFirstAired(item_get('premiered'))
					info_tag.setStudios((studio or '',))
					info_tag.setUniqueIDs({'imdb': imdb_id, 'tmdb': string(tmdb_id), 'tvdb': string(tvdb_id)})
					info_tag.setIMDBNumber(imdb_id)
					info_tag.setGenres(genre.split(', '))
					info_tag.setWriters(item_get('writer').split(', '))
					info_tag.setDirectors(item_get('director').split(', '))
					info_tag.setCast([xbmc_actor(name=item['name'], role=item['role'], thumbnail=item['thumbnail']) for item in cast + item_get('guest_stars', [])])
					if is_widget: listitem.setInfo('video', {'overlay': overlay})# needs to stay until setPlaycount works
				else:
					item.update({'trailer': trailer, 'tvshowtitle': title, 'premiered': premiered, 'genre': genre, 'mpaa': mpaa, 'studio': studio, 'status': show_status,
								'playcount': playcount, 'overlay': overlay})
					listitem.setCast(cast + item_get('guest_stars', []))
					listitem.setUniqueIDs({'imdb': imdb_id, 'tmdb': string(tmdb_id), 'tvdb': string(tvdb_id)})
					listitem.setInfo('video', remove_keys(item, dict_removals))
				listitem.setLabel(display)
				listitem.addContextMenuItems(cm)
				listitem.setArt({'poster': show_poster, 'fanart': show_fanart, 'thumb': thumb, 'icon':thumb, 'banner': show_banner, 'clearart': show_clearart,
								'clearlogo': show_clearlogo, 'landscape': show_landscape, 'season.poster': season_poster, 'tvshow.poster': show_poster,
								'tvshow.clearart': show_clearart, 'tvshow.clearlogo': show_clearlogo, 'tvshow.landscape': show_landscape, 'tvshow.banner': show_banner})
				set_properties({'fen.playcount': string(playcount), 'fen.extras_params': extras_params, 'fen.options_params': options_params,
								'fen.unwatched_params': unwatched_params, 'fen.watched_params': watched_params, 'fen.clearprog_params': clearprog_params})
				if is_widget: set_properties({'fen.widget': 'true'})
				yield (url_params, listitem, False)
			except: pass
	handle, is_widget = int(sys.argv[1]), external_browse()
	if build_content():
		item_list = []
		append = item_list.append		
		meta_user_info, watched_indicators, show_unaired, adjust_hours = metadata_user_info(), watched_indicators_info(), show_unaired_info(), date_offset_info()
		current_date, watched_info, bookmarks = get_datetime_function(), get_watched_info(watched_indicators), get_bookmarks(watched_indicators, 'episode')
		watched_title = trakt_str if watched_indicators == 1 else fen_str
		fanart_enabled, hide_watched = meta_user_info['extra_fanart_enabled'], is_widget and meta_user_info['widget_hide_watched']
		meta = tv_meta_function('tmdb_id', params.get('tmdb_id'), meta_user_info, current_date)
		meta_get = meta.get
		tmdb_id, tvdb_id, imdb_id, tvshow_plot, orig_title = meta_get('tmdb_id'), meta_get('tvdb_id'), meta_get('imdb_id'), meta_get('plot'), meta_get('original_title')
		title, year, rootname, show_duration, show_status = meta_get('title'), meta_get('year'), meta_get('rootname'), meta_get('duration'), meta_get('status')
		cast, mpaa, trailer, genre, studio = meta_get('cast', []), meta_get('mpaa'), string(meta_get('trailer')), meta_get('genre'), meta_get('studio')
		season = params['season']
		poster_main, poster_backup, fanart_main, fanart_backup, clearlogo_main, clearlogo_backup = get_art_provider()
		fanart_default = poster_main == 'poster2'
		show_poster = meta_get('custom_poster') or meta_get(poster_main) or meta_get(poster_backup) or poster_empty
		show_fanart = meta_get('custom_fanart') or meta_get(fanart_main) or meta_get(fanart_backup) or fanart_empty
		show_clearlogo = meta_get('custom_clearlogo') or meta_get(clearlogo_main) or meta_get(clearlogo_backup) or ''
		if fanart_enabled:
			season_art = meta_get('season_art', {})
			show_banner = meta_get('custom_banner') or meta_get('banner') or ''
			show_clearart = meta_get('custom_clearart') or meta_get('clearart') or ''
			show_landscape = meta_get('custom_landscape') or meta_get('landscape') or ''
		else: show_banner, show_clearart, show_landscape = '', '', ''
		if season == 'all':
			episodes_data = all_episodes_meta_function(meta, meta_user_info, show_specials())
			season_poster = show_poster
		else:
			episodes_data = episodes_meta_function(season, meta, meta_user_info)
			try:
				poster_path = [i['poster_path'] for i in meta_get('season_data') if i['season_number'] == int(season)][0]
				tmdb_poster = '%s%s%s' % (tmdb_poster_prefix, meta_user_info['image_resolution']['poster'], poster_path) if poster_path is not None else show_poster
			except: tmdb_poster = show_poster
			if fanart_default: season_poster = season_art.get('seasonposter_%s' % season, '') or tmdb_poster
			else: season_poster = tmdb_poster
		add_items(handle, list(_process()))
		set_sort_method(handle, content_type)
	else: add_items(handle, make_placeholder())
	set_content(handle, content_type)
	end_directory(handle, False if is_widget else None)
	if not is_widget: set_view_mode(view_mode, content_type)

def build_single_episode(list_type, params={}):
	def _process(item_position, ep_data):
		try:
			ep_data_get = ep_data.get
			meta = tv_meta_function('trakt_dict', ep_data_get('media_ids'), meta_user_info, current_date)
			if not meta: return
			cm = []
			cm_append = cm.append
			listitem = make_listitem()
			set_properties = listitem.setProperties
			meta_get = meta.get
			orig_season, orig_episode = ep_data_get('season'), ep_data_get('episode')
			if list_type_starts_with('next_'):
				season_data = meta_get('season_data')
				curr_season_data = [i for i in season_data if i['season_number'] == orig_season][0]
				if orig_episode >= curr_season_data['episode_count']: orig_season, orig_episode, new_season = orig_season + 1, 1, True
				else: orig_episode, new_season = orig_episode + 1, False
			episodes_data = episodes_meta_function(orig_season, meta, meta_user_info)
			try: item = [i for i in episodes_data if i['episode'] == orig_episode][0]
			except: return
			item_get = item.get
			season, episode, ep_name = item_get('season'), item_get('episode'), item_get('title')
			episode_date, premiered = adjust_premiered_date_function(item_get('premiered'), adjust_hours)
			if not episode_date or current_date < episode_date:
				if list_type_starts_with('next_'):
					if not episode_date: return
					if not nextep_include_unaired: return
					if episode_date and new_season and not date_difference_function(current_date, episode_date, 7): return
				elif not show_unaired: return
				unaired = True
				set_properties({'fen.unaired': 'true'})
			else:
				unaired = False
				set_properties({'fen.unaired': 'false'})
			tmdb_id, tvdb_id, imdb_id, title, year = meta_get('tmdb_id'), meta_get('tvdb_id'), meta_get('imdb_id'), meta_get('title'), meta_get('year')
			orig_title, rootname, trailer, genre, studio = meta_get('rootname'), string(meta_get('trailer')), meta_get('genre'), meta_get('studio'), meta_get('original_title')
			cast, mpaa, tvshow_plot, show_status = meta_get('cast', []), meta_get('mpaa'), meta_get('plot'), meta_get('status')
			show_poster = meta_get('custom_poster') or meta_get(poster_main) or meta_get(poster_backup) or poster_empty
			show_fanart = meta_get('custom_fanart') or meta_get(fanart_main) or meta_get(fanart_backup) or fanart_empty
			show_clearlogo = meta_get('custom_clearlogo') or meta_get(clearlogo_main) or meta_get(clearlogo_backup) or ''
			tmdb_thumb = item_get('thumb', None)
			try:
				poster_path = [i['poster_path'] for i in meta_get('season_data') if i['season_number'] == int(season)][0]
				tmdb_poster = '%s%s%s' % (tmdb_poster_prefix, meta_user_info['image_resolution']['poster'], poster_path) if poster_path is not None else show_poster
			except: tmdb_poster = show_poster
			if fanart_enabled:
				season_art = meta_get('season_art', {})
				show_banner = meta_get('custom_banner') or meta_get('banner') or ''
				show_clearart = meta_get('custom_clearart') or meta_get('clearart') or ''
				show_landscape = meta_get('custom_landscape') or meta_get('landscape') or ''
				if fanart_default:
					season_poster = season_art.get('seasonposter_%s' % season, '') or tmdb_poster
					thumb = tmdb_thumb or season_art.get('seasonthumb_%s' % season, '') or show_fanart
				else:
					season_poster = tmdb_poster or season_art.get('seasonposter_%s' % orig_season, '')
					thumb = tmdb_thumb or show_fanart or season_art.get('seasonthumb_%s' % season, '')
			else: show_banner, show_clearart, show_landscape, season_art, season_poster, thumb = '', '', '', {}, tmdb_poster, tmdb_thumb or show_fanart
			(playcount, overlay), progress = get_watched_status(watched_info, string(tmdb_id), season, episode), get_progress_percent(bookmarks, tmdb_id, season, episode)
			str_season_zfill2, str_episode_zfill2 = string(season).zfill(2), string(episode).zfill(2)
			if display_title == 0: title_string = '%s: ' % title
			else: title_string = ''
			if display_title in (0,1): seas_ep = '%sx%s - ' % (str_season_zfill2, str_episode_zfill2)
			else: seas_ep = ''
			if list_type_starts_with('next_'):
				unwatched = ep_data_get('unwatched', False)
				display_premiered = make_day_function(current_date, episode_date, date_format) if episode_date else 'UNKNOWN'
				airdate = '[[COLOR magenta]%s[/COLOR]] ' % display_premiered if nextep_include_airdate else '' 
				highlight_color = nextep_unwatched_color if unwatched else nextep_unaired_color if unaired else ''
				italics_open, italics_close = ('[I]', '[/I]') if highlight_color else ('', '')
				if highlight_color: episode_info = '%s[COLOR%s]%s%s[/COLOR]%s' % (italics_open, highlight_color, seas_ep, ep_name, italics_close)
				else: episode_info = '%s%s%s%s' % (italics_open, seas_ep, ep_name, italics_close)
				display = '%s%s%s' % (airdate, upper(title_string), episode_info)
			elif list_type_compare == 'trakt_calendar':
				if episode_date: display_premiered = make_day_function(current_date, episode_date, date_format)
				else: display_premiered = 'UNKNOWN'
				display = '[%s]%s%s%s' % (display_premiered, upper(title_string), seas_ep, ep_name)
				if unaired:
					displays = display.split(']')
					display = '[COLOR red]%s][/COLOR]%s' % (displays[0], displays[1])
			else:
				color_tags = ('[COLOR red]', '[/COLOR]') if unaired else ('', '')
				display = '%s%s%s%s%s' % (upper(title_string), color_tags[0], seas_ep, ep_name, color_tags[1])
			if not item_get('duration'): item['duration'] = meta_get('duration')
			options_params = build_url({'mode': 'options_menu_choice', 'content': list_type, 'tmdb_id': tmdb_id, 'season': season, 'episode': episode,
										'poster': show_poster, 'playcount': playcount, 'progress': progress, 'is_widget': is_widget})
			extras_params = build_url({'mode': 'extras_menu_choice', 'tmdb_id': tmdb_id, 'media_type': 'episode', 'is_widget': is_widget})
			url_params = build_url({'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': tmdb_id, 'season': season, 'episode': episode})
			cm_append((extras_str, run_plugin % extras_params))
			cm_append((options_str, run_plugin % options_params))
			clearprog_params, unwatched_params, watched_params = '', '', ''
			if not unaired:
				if playcount:
					if hide_watched: return
					unwatched_params = build_url({'mode': 'watched_status.mark_episode', 'action': 'mark_as_unwatched', 'tmdb_id': tmdb_id,
												'tvdb_id': tvdb_id, 'season': season, 'episode': episode,  'title': title, 'year': year})
					cm_append((unwatched_str % watched_title, run_plugin % unwatched_params))
				else:
					watched_params = build_url({'mode': 'watched_status.mark_episode', 'action': 'mark_as_watched', 'tmdb_id': tmdb_id,
												'tvdb_id': tvdb_id, 'season': season, 'episode': episode,  'title': title, 'year': year})
					cm_append((watched_str % watched_title, run_plugin % watched_params))
				if progress:
					clearprog_params = build_url({'mode': 'watched_status.erase_bookmark', 'media_type': 'episode', 'tmdb_id': tmdb_id,
												'season': season, 'episode': episode, 'refresh': 'true'})
					cm_append((clearprog_str, run_plugin % clearprog_params))
					set_properties({'WatchedProgress': progress, 'resumetime': progress, 'fen.in_progress': 'true'})
			if kodi_version == 20:
				if is_widget: cm_append((refr_widg_str, run_plugin % build_url({'mode': 'kodi_refresh'})))
				info_tag = listitem.getVideoInfoTag()
				info_tag.setMediaType('episode')
				info_tag.setTitle(display)
				info_tag.setOriginalTitle(orig_title)
				info_tag.setTvShowTitle(title)
				info_tag.setTvShowStatus(show_status)
				info_tag.setSeason(season)
				info_tag.setEpisode(episode)
				info_tag.setPlot(item_get('plot'))
				info_tag.setYear(int(year))
				info_tag.setRating(item_get('rating'))
				info_tag.setVotes(item_get('votes'))
				info_tag.setMpaa(mpaa)
				info_tag.setDuration(item_get('duration'))
				info_tag.setPlaycount(playcount)
				info_tag.setTrailer(trailer)
				info_tag.setFirstAired(item_get('premiered'))
				info_tag.setStudios((studio or '',))
				info_tag.setUniqueIDs({'imdb': imdb_id, 'tmdb': string(tmdb_id), 'tvdb': string(tvdb_id)})
				info_tag.setIMDBNumber(imdb_id)
				info_tag.setGenres(genre.split(', '))
				info_tag.setWriters(item_get('writer').split(', '))
				info_tag.setDirectors(item_get('director').split(', '))
				info_tag.setCast([xbmc_actor(name=item['name'], role=item['role'], thumbnail=item['thumbnail']) for item in cast + item_get('guest_stars', [])])
				if is_widget: listitem.setInfo('video', {'overlay': overlay})# needs to stay until setPlaycount works
			else:
				item.update({'trailer': trailer, 'tvshowtitle': title, 'premiered': premiered, 'genre': genre, 'mpaa': mpaa, 'studio': studio, 'status': show_status,
							'playcount': playcount, 'overlay': overlay, 'title': display})
				listitem.setCast(cast + item_get('guest_stars', []))
				listitem.setUniqueIDs({'imdb': imdb_id, 'tmdb': string(tmdb_id), 'tvdb': string(tvdb_id)})
				listitem.setInfo('video', remove_keys(item, dict_removals))
			listitem.setLabel(display)
			listitem.addContextMenuItems(cm)
			listitem.setArt({'poster': show_poster, 'fanart': show_fanart, 'thumb': thumb, 'icon':thumb, 'banner': show_banner, 'clearart': show_clearart, 'clearlogo': show_clearlogo,
							'landscape': show_landscape, 'season.poster': season_poster, 'tvshow.poster': show_poster, 'tvshow.clearart': show_clearart,
							'tvshow.clearlogo': show_clearlogo, 'tvshow.landscape': show_landscape, 'tvshow.banner': show_banner})
			set_properties({'fen.widget': 'false', 'fen.first_aired': premiered, 'fen.name': '%s - %sx%s' % (title, str_season_zfill2, str_episode_zfill2)})
			if list_type_starts_with('next_'):
				last_played = ep_data_get('last_played', resinsert)
				set_properties({'fen.last_played': last_played})
			else: set_properties({'fen.sort_order': string(item_position)})
			set_properties({'fen.playcount': string(playcount), 'fen.extras_params': extras_params, 'fen.options_params': options_params,
								'fen.unwatched_params': unwatched_params, 'fen.watched_params': watched_params, 'fen.clearprog_params': clearprog_params})
			if is_widget: set_properties({'fen.widget': 'true'})
			append((url_params, listitem, False))
		except: pass
	handle, is_widget = int(sys.argv[1]), external_browse()
	if build_content():
		item_list = []
		append = item_list.append
		display_title, date_format, art_keys, all_episodes = single_ep_display_title(), single_ep_format(), get_art_provider(), default_all_episodes()
		meta_user_info, watched_indicators, show_unaired = metadata_user_info(), watched_indicators_info(), show_unaired_info()
		current_date, adjust_hours, ignore_articles_setting = get_datetime_function(), date_offset_info(), ignore_articles()
		watched_info, bookmarks, watched_title = get_watched_info(watched_indicators), get_bookmarks(watched_indicators, 'episode'), trakt_str if watched_indicators == 1 else fen_str
		fanart_enabled, hide_watched, show_all_episodes = meta_user_info['extra_fanart_enabled'], is_widget and meta_user_info['widget_hide_watched'], all_episodes in (1, 2)
		poster_main, poster_backup, fanart_main, fanart_backup, clearlogo_main, clearlogo_backup = art_keys
		fanart_default = poster_main == 'poster2'
		if list_type == 'episode.progress': data = get_in_progress_episodes()
		elif list_type == 'episode.recently_watched': data = get_recently_watched('episode')[0]
		elif list_type == 'episode.next':
			nextep_settings = nextep_content_settings()
			include_unwatched = nextep_settings['include_unwatched']
			data = get_next_episodes(watched_info)
			if watched_indicators == 1:
				list_type = 'episode.next_trakt'
				try:
					hidden_data = trakt_get_hidden_items('progress_watched')
					data = [i for i in data if not i['media_ids']['tmdb'] in hidden_data]
				except: pass
			else: list_type = 'episode.next_fen'
			if include_unwatched != 0:
				unwatched = []
				if include_unwatched in (1, 3):
					try: unwatched.extend([{'media_ids': i['media_ids'], 'season': 1, 'episode': 0, 'unwatched': True, 'title': i['title']} \
									for i in trakt_fetch_collection_watchlist('watchlist', 'tvshow')])
					except: pass
				if include_unwatched in (2, 3):
					try: unwatched.extend([{'media_ids': {'tmdb': int(i['tmdb_id'])}, 'season': 1, 'episode': 0, 'unwatched': True, 'title': i['title']} \
										for i in favorites.get_favorites('tvshow') if not int(i['tmdb_id']) in [x['media_ids']['tmdb'] for x in data]])
					except: pass
				data += unwatched
		else:#episode.trakt
			recently_aired = params.get('recently_aired', None)
			data = trakt_get_my_calendar(recently_aired, get_datetime_function())
			list_type = 'episode.trakt_recently_aired' if recently_aired else 'episode.trakt_calendar'
			data = sorted(data, key=lambda k: (k['sort_title'], k['first_aired']), reverse=True)
		list_type_compare = list_type.split('episode.')[1]
		list_type_starts_with = list_type_compare.startswith
		if list_type_starts_with('next_'):
			nextep_settings, nextep_disp_settings = nextep_content_settings(), nextep_display_settings()
			nextep_unaired_color, nextep_unwatched_color = nextep_disp_settings['unaired_color'], nextep_disp_settings['unwatched_color']
			nextep_include_airdate, nextep_include_unaired = nextep_disp_settings['include_airdate'], nextep_settings['include_unaired']
			if watched_indicators == 1: resformat, resinsert = '%Y-%m-%dT%H:%M:%S.%fZ', '2000-01-01T00:00:00.000Z'
			else: resformat, resinsert = '%Y-%m-%d %H:%M:%S', '2000-01-01 00:00:00'
		threads = list(make_thread_list_enumerate(_process, data))
		[i.join() for i in threads]
		if list_type_starts_with('next_'):
			def func(function):
				if sort_key == 'fen.name': return title_key_function(function, ignore_articles_setting)
				elif sort_key == 'fen.last_played': return jsondate_to_datetime_function(function, resformat)
				else: return function
			sort_key = nextep_settings['sort_key']
			sort_direction = nextep_settings['sort_direction']
			if nextep_settings['sort_airing_today_to_top']:
				airing_today = [i for i in item_list
								if date_difference_function(current_date, jsondate_to_datetime_function(i[1].getProperty('fen.first_aired'), '%Y-%m-%d').date(), 0)]
				airing_today = sorted(airing_today, key=lambda i: i[1].getProperty('fen.first_aired'))
				remainder = [i for i in item_list if not i in airing_today]
				remainder = sorted(remainder, key=lambda i: func(i[1].getProperty(sort_key)), reverse=sort_direction)
				unaired = [i for i in remainder if i[1].getProperty('fen.unaired') == 'true']
				aired = [i for i in remainder if not i in unaired]
				remainder = aired + unaired
				item_list = airing_today + remainder
			else:
				item_list = sorted(item_list, key=lambda i: func(i[1].getProperty(sort_key)), reverse=sort_direction)
				unaired = [i for i in item_list if i[1].getProperty('fen.unaired') == 'true']
				aired = [i for i in item_list if not i in unaired]
				item_list = aired + unaired
		else:
			item_list.sort(key=lambda k: int(k[1].getProperty('fen.sort_order')))
			if list_type_compare in ('trakt_calendar', 'trakt_recently_aired'):
				if list_type_compare == 'trakt_calendar': reverse = calendar_sort_order() == 0
				else: reverse = True
				item_list.sort(key=lambda k: int(k[1].getProperty('fen.sort_order')))
				item_list = sorted(item_list, key=lambda i: i[1].getProperty('fen.first_aired'), reverse=reverse)
		add_items(handle, item_list)
	else: add_items(handle, make_placeholder())
	set_content(handle, content_type)
	end_directory(handle, cacheToDisc=False)
	if not is_widget: set_view_mode(view_mode, content_type)
