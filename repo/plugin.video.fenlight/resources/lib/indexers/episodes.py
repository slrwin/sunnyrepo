# -*- coding: utf-8 -*-
from apis.trakt_api import trakt_watchlist, trakt_get_my_calendar
from caches.favorites_cache import favorites_cache
from modules import kodi_utils, settings, watched_status as ws
from modules.watched_status import get_hidden_progress_items
from modules.metadata import tvshow_meta, episodes_meta, all_episodes_meta
from modules.utils import jsondate_to_datetime, adjust_premiered_date, make_day, get_datetime, title_key, date_difference, make_thread_list_enumerate
# logger = kodi_utils.logger

set_view_mode, external, home, sys = kodi_utils.set_view_mode, kodi_utils.external, kodi_utils.home, kodi_utils.sys
add_items, set_content, set_sort_method, end_directory = kodi_utils.add_items, kodi_utils.set_content, kodi_utils.set_sort_method, kodi_utils.end_directory
date_offset_info, default_all_episodes, nextep_include_unwatched = settings.date_offset, settings.default_all_episodes, settings.nextep_include_unwatched
nextep_include_unaired, ep_display_format, widget_hide_watched = settings.nextep_include_unaired, settings.single_ep_display_format, settings.widget_hide_watched
make_listitem, build_url, xbmc_actor, set_category = kodi_utils.make_listitem, kodi_utils.build_url, kodi_utils.xbmc_actor, kodi_utils.set_category
watched_indicators_info, use_minimal_media_info = settings.watched_indicators, settings.use_minimal_media_info
tv_meta_function, episodes_meta_function, all_episodes_meta_function = tvshow_meta, episodes_meta, all_episodes_meta
adjust_premiered_date_function, jsondate_to_datetime_function = adjust_premiered_date, jsondate_to_datetime
make_day_function, title_key_function, get_datetime_function, date_difference_function = make_day, title_key, get_datetime, date_difference
get_progress_percent, get_watched_status, get_watched_info, get_bookmarks = ws.get_progress_percent, ws.get_watched_status_episode, ws.get_watched_info_tv, ws.get_bookmarks
get_in_progress_episodes, get_next_episodes, get_recently_watched = ws.get_in_progress_episodes, ws.get_next_episodes, ws.get_recently_watched
string =  str
poster_empty, fanart_empty = kodi_utils.empty_poster, kodi_utils.get_addon_fanart()
run_plugin, unaired_label, tmdb_poster = 'RunPlugin(%s)', '[COLOR red][I]%s[/I][/COLOR]', 'https://image.tmdb.org/t/p/w780%s'
upper = string.upper
content_type = 'episodes'
list_view, single_view = 'view.episodes', 'view.episodes_single'
category_name_dict = {'episode.progress': 'In Progress Episodes', 'episode.recently_watched': 'Recently Watched Episodes', 'episode.next': 'Next Episodes',
					'episode.trakt': {'true': 'Recently Aired Episodes', None: 'Trakt Calendar'}}

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
				episode_type = item_get('episode_type') or ''
				playcount = get_watched_status(watched_info, string(tmdb_id), season, episode)
				progress = get_progress_percent(bookmarks, tmdb_id, season, episode)
				thumb = item_get('thumb', None) or show_fanart
				try: year = premiered.split('-')[0]
				except: year = show_year or '2050'
				if not item_get('duration'): item['duration'] = show_duration
				if not episode_date or current_date < episode_date:
					display, unaired = unaired_label % ep_name, True
					item['title'] = display
				else: display, unaired = ep_name, False
				options_params = build_url({'mode': 'options_menu_choice', 'content': 'episode', 'tmdb_id': tmdb_id, 'season': season, 'episode': episode,
											'poster': show_poster, 'playcount': playcount, 'progress': progress, 'is_external': is_external, 'unaired': unaired})
				extras_params = build_url({'mode': 'extras_menu_choice', 'tmdb_id': tmdb_id, 'media_type': 'episode', 'is_external': is_external})
				play_options_params = build_url({'mode': 'playback_choice', 'media_type': 'episode', 'poster': show_poster, 'meta': tmdb_id, 'season': season, 'episode': episode})
				url_params = build_url({'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': tmdb_id, 'season': season, 'episode': episode})
				cm_append(('[B]Extras...[/B]', run_plugin % extras_params))
				cm_append(('[B]Options...[/B]', run_plugin % options_params))
				cm_append(('[B]Playback Options...[/B]', run_plugin % play_options_params))
				if not unaired:
					if playcount:
						if hide_watched: continue
						cm_append(('[B]Mark Unwatched %s[/B]' % watched_title, run_plugin % build_url({'mode': 'watched_status.mark_episode', 'action': 'mark_as_unwatched',
													'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id, 'season': season, 'episode': episode,  'title': title})))
					else: cm_append(('[B]Mark Watched %s[/B]' % watched_title, run_plugin % build_url({'mode': 'watched_status.mark_episode', 'action': 'mark_as_watched',
													'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id, 'season': season, 'episode': episode,  'title': title})))
					if progress: cm_append(('[B]Clear Progress[/B]', run_plugin % build_url({'mode': 'watched_status.erase_bookmark', 'media_type': 'episode', 'tmdb_id': tmdb_id,
													'season': season, 'episode': episode, 'refresh': 'true'})))
				if is_home: cm_append(('[B]Refresh Widgets[/B]', run_plugin % build_url({'mode': 'kodi_refresh'})))
				info_tag = listitem.getVideoInfoTag()
				info_tag.setMediaType('episode'), info_tag.setTitle(display), info_tag.setOriginalTitle(orig_title), info_tag.setTvShowTitle(title), info_tag.setGenres(genre)
				info_tag.setPlaycount(playcount), info_tag.setSeason(season), info_tag.setEpisode(episode), info_tag.setPlot(item_get('plot') or tvshow_plot)
				info_tag.setDuration(item_get('duration')), info_tag.setIMDBNumber(imdb_id), info_tag.setUniqueIDs({'imdb': imdb_id, 'tmdb': string(tmdb_id), 'tvdb': string(tvdb_id)})
				info_tag.setFirstAired(premiered)
				if not use_minimal_media:
					info_tag.setTvShowStatus(show_status)
					info_tag.setCountries(country), info_tag.setTrailer(trailer), info_tag.setDirectors(item_get('director'))
					info_tag.setYear(int(year)), info_tag.setRating(item_get('rating')), info_tag.setVotes(item_get('votes')), info_tag.setMpaa(mpaa)
					info_tag.setStudios(studio), info_tag.setWriters(item_get('writer'))
					info_tag.setCast([xbmc_actor(name=item['name'], role=item['role'], thumbnail=item['thumbnail']) for item in cast])
				if progress and not unaired:
					info_tag.setResumePoint(float(progress))
					set_properties({'WatchedProgress': progress})
				listitem.setLabel(display)
				listitem.addContextMenuItems(cm)
				listitem.setArt({'poster': show_poster, 'fanart': show_fanart, 'thumb': thumb, 'icon':thumb, 'clearlogo': show_clearlogo, 'season.poster': season_poster,
								'tvshow.poster': show_poster, 'tvshow.clearlogo': show_clearlogo})
				set_properties({'fenlight.extras_params': extras_params, 'fenlight.options_params': options_params, 'IsPlayable': 'false', 'episode_type': episode_type})
				yield (url_params, listitem, False)
			except: pass
	handle, is_external, is_home, category_name = int(sys.argv[1]), external(), home(), 'Episodes'
	item_list = []
	append = item_list.append
	watched_indicators = watched_indicators_info()
	adjust_hours = date_offset_info()
	use_minimal_media = use_minimal_media_info()
	hide_watched = is_home and widget_hide_watched()
	current_date, watched_info, bookmarks = get_datetime_function(), get_watched_info(watched_indicators), get_bookmarks(watched_indicators, 'episode')
	watched_title = 'Trakt' if watched_indicators == 1 else 'Fen Light'
	meta = tv_meta_function('tmdb_id', params.get('tmdb_id'), current_date)
	meta_get = meta.get
	tmdb_id, tvdb_id, imdb_id, tvshow_plot, orig_title = meta_get('tmdb_id'), meta_get('tvdb_id'), meta_get('imdb_id'), meta_get('plot'), meta_get('original_title')
	title, show_year, rootname, show_duration, show_status = meta_get('title'), meta_get('year') or '2050', meta_get('rootname'), meta_get('duration'), meta_get('status')
	cast, mpaa, trailer, genre, studio, country = meta_get('cast', []), meta_get('mpaa'), string(meta_get('trailer')), meta_get('genre'), meta_get('studio'), meta_get('country')
	season = params['season']
	show_poster = meta_get('poster') or poster_empty
	show_fanart = meta_get('fanart') or fanart_empty
	show_clearlogo = meta_get('clearlogo') or ''
	if season == 'all':
		episodes_data = all_episodes_meta_function(meta)
		season_poster = show_poster
	else:
		episodes_data = episodes_meta_function(season, meta)
		try:
			poster_path = [i['poster_path'] for i in meta_get('season_data') if i['season_number'] == int(season)][0]
			season_poster = tmdb_poster % poster_path if poster_path is not None else show_poster
		except: season_poster = show_poster
	add_items(handle, list(_process()))
	set_sort_method(handle, content_type)
	category_name = 'Season %s' % season
	set_content(handle, content_type)
	set_category(handle, category_name)
	end_directory(handle, cacheToDisc=False if is_external else True)
	set_view_mode(list_view, content_type, is_external)

def build_single_episode(list_type, params={}):
	def _get_category_name():
		cat_name = category_name_dict[list_type]
		if isinstance(cat_name, dict): cat_name = cat_name[params.get('recently_aired')]
		return cat_name
	def _process(_position, ep_data):
		try:
			ep_data_get = ep_data.get
			meta = tv_meta_function('trakt_dict', ep_data_get('media_ids'), current_date)
			if not meta: return
			meta_get = meta.get
			cm = []
			cm_append = cm.append
			listitem = make_listitem()
			set_properties = listitem.setProperties
			orig_season, orig_episode = ep_data_get('season'), ep_data_get('episode')
			unwatched = ep_data_get('unwatched', False)
			season_data = meta_get('season_data')
			if list_type_starts_with('next_'):
				if orig_episode == 0: orig_episode, new_season = 1, False
				else:
					try:
						episode_count = [i for i in season_data if i['season_number'] == orig_season][0]['episode_count']
						if orig_episode >= episode_count:
							orig_season, orig_episode, new_season = orig_season + 1, 1, True
							if orig_season > meta_get('total_seasons'): return
						else: orig_episode, new_season = orig_episode + 1, False
					except: return
			episodes_data = episodes_meta_function(orig_season, meta)
			try: item = [i for i in episodes_data if i['episode'] == orig_episode][0]
			except: return
			item_get = item.get
			season, episode, ep_name = item_get('season'), item_get('episode'), item_get('title')
			episode_date, premiered = adjust_premiered_date_function(item_get('premiered'), adjust_hours)
			episode_type = item_get('episode_type') or ''
			if not episode_date or current_date < episode_date:
				if list_type_starts_with('next_'):
					if episode_date and new_season and not date_difference_function(current_date, episode_date, 7): return
				unaired = True
			else: unaired = False
			tmdb_id, tvdb_id, imdb_id, title, show_year = meta_get('tmdb_id'), meta_get('tvdb_id'), meta_get('imdb_id'), meta_get('title'), meta_get('year') or '2050'
			orig_title, rootname, trailer, genre, studio = meta_get('original_title'), meta_get('rootname'), string(meta_get('trailer')), meta_get('genre'), meta_get('studio')
			cast, mpaa, tvshow_plot, show_status = meta_get('cast', []), meta_get('mpaa'), meta_get('plot'), meta_get('status')
			show_poster = meta_get('poster') or poster_empty
			show_fanart = meta_get('fanart') or fanart_empty
			show_clearlogo = meta_get('clearlogo') or ''
			thumb = item_get('thumb', None) or show_fanart
			try: year = premiered.split('-')[0]
			except: year = show_year or '2050'
			try:
				poster_path = [i['poster_path'] for i in season_data if i['season_number'] == int(season)][0]
				season_poster = tmdb_poster % poster_path if poster_path is not None else show_poster
			except: season_poster = show_poster
			playcount, progress = get_watched_status(watched_info, string(tmdb_id), season, episode), get_progress_percent(bookmarks, tmdb_id, season, episode)
			str_season_zfill2, str_episode_zfill2 = string(season).zfill(2), string(episode).zfill(2)
			if display_format == 0: title_string = '%s: ' % title
			else: title_string = ''
			if display_format in (0, 1): seas_ep = '%sx%s - ' % (str_season_zfill2, str_episode_zfill2)
			else: seas_ep = ''
			if list_type_starts_with('next_'):
				if playcount: return
				if unwatched: display_premiered, highlight_start, highlight_end = '', '[COLOR darkgoldenrod]', '[/COLOR]'
				elif unaired:
					if not include_unaired: return
					if episode_date: display_premiered = '[%s] ' % make_day_function(current_date, episode_date)
					else: display_premiered = '[UNKNOWN] '
					highlight_start, highlight_end = '[COLOR red]', '[/COLOR]'
				else: display_premiered, highlight_start, highlight_end = '', '', ''
				display = '%s%s%s%s%s%s' % (display_premiered, title_string, highlight_start, seas_ep, ep_name, highlight_end)
			elif list_type_compare == 'trakt_calendar':
				if episode_date: display_premiered = make_day_function(current_date, episode_date)
				else: display_premiered = 'UNKNOWN'
				display = '[%s] %s%s%s' % (display_premiered, title_string, seas_ep, ep_name)
			else: display = '%s%s%s' % (title_string, seas_ep, ep_name)
			if not item_get('duration'): item['duration'] = meta_get('duration')
			options_params = build_url({'mode': 'options_menu_choice', 'content': list_type, 'tmdb_id': tmdb_id, 'season': season, 'episode': episode,
										'poster': show_poster, 'playcount': playcount, 'progress': progress, 'is_external': is_external, 'in_progress_menu': 'true'})
			extras_params = build_url({'mode': 'extras_menu_choice', 'tmdb_id': tmdb_id, 'media_type': 'episode', 'is_external': is_external})
			play_options_params = build_url({'mode': 'playback_choice', 'media_type': 'episode', 'poster': show_poster, 'meta': tmdb_id, 'season': season, 'episode': episode})
			url_params = build_url({'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': tmdb_id, 'season': season, 'episode': episode})
			cm_append(('[B]Extras...[/B]', run_plugin % extras_params))
			cm_append(('[B]Options...[/B]', run_plugin % options_params))
			cm_append(('[B]Playback Options...[/B]', run_plugin % play_options_params))
			if not unaired:
				if playcount:
					if hide_watched: return
					cm_append(('[B]Mark Unwatched %s[/B]' % watched_title, run_plugin % build_url({'mode': 'watched_status.mark_episode', 'action': 'mark_as_unwatched',
														'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id, 'season': season, 'episode': episode,  'title': title})))
				else: cm_append(('[B]Mark Watched %s[/B]' % watched_title, run_plugin % build_url({'mode': 'watched_status.mark_episode', 'action': 'mark_as_watched',
														'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id, 'season': season, 'episode': episode,  'title': title})))
				if progress: cm_append(('[B]Clear Progress[/B]', run_plugin % build_url({'mode': 'watched_status.erase_bookmark', 'media_type': 'episode', 'tmdb_id': tmdb_id,
														'season': season, 'episode': episode, 'refresh': 'true'})))
			if is_home: cm_append(('[B]Refresh Widgets[/B]', run_plugin % build_url({'mode': 'kodi_refresh'})))
			info_tag = listitem.getVideoInfoTag()
			info_tag.setMediaType('episode'), info_tag.setOriginalTitle(orig_title), info_tag.setTvShowTitle(title), info_tag.setTitle(display), info_tag.setGenres(genre)
			info_tag.setPlaycount(playcount), info_tag.setSeason(season), info_tag.setEpisode(episode), info_tag.setPlot(item_get('plot') or tvshow_plot)
			info_tag.setDuration(item_get('duration')), info_tag.setIMDBNumber(imdb_id), info_tag.setUniqueIDs({'imdb': imdb_id, 'tmdb': string(tmdb_id), 'tvdb': string(tvdb_id)})
			info_tag.setFirstAired(premiered)
			if not use_minimal_media:
				info_tag.setCountries(meta_get('country', [])), info_tag.setTrailer(trailer), info_tag.setTvShowStatus(show_status)
				info_tag.setStudios(studio), info_tag.setWriters(item_get('writer')), info_tag.setDirectors(item_get('director'))
				info_tag.setYear(int(year)), info_tag.setRating(item_get('rating')), info_tag.setVotes(item_get('votes')), info_tag.setMpaa(mpaa)
				info_tag.setCast([xbmc_actor(name=item['name'], role=item['role'], thumbnail=item['thumbnail']) for item in cast])
			if progress and not unaired:
				info_tag.setResumePoint(float(progress))
				set_properties({'WatchedProgress': progress})
			listitem.setLabel(display)
			listitem.addContextMenuItems(cm)
			listitem.setArt({'poster': show_poster, 'fanart': show_fanart, 'thumb': thumb, 'icon':thumb, 'clearlogo': show_clearlogo,
							'season.poster': season_poster, 'tvshow.poster': show_poster, 'tvshow.clearlogo': show_clearlogo})
			set_properties({'fenlight.extras_params': extras_params, 'fenlight.options_params': options_params, 'IsPlayable': 'false', 'episode_type': episode_type})
			item_list_append({'list_items': (url_params, listitem, False), 'first_aired': premiered, 'name': '%s - %sx%s' % (title, str_season_zfill2, str_episode_zfill2),
							'unaired': unaired, 'last_played': ep_data_get('last_played', resinsert), 'sort_order': string(_position), 'unwatched': ep_data_get('unwatched')})
		except: pass
	handle, is_external, is_home, category_name = int(sys.argv[1]), external(), home(), 'Episodes'
	item_list, unwatched = [], []
	resinsert = ''
	item_list_append = item_list.append
	all_episodes, watched_indicators, use_minimal_media, display_format = default_all_episodes(), watched_indicators_info(), use_minimal_media_info(), ep_display_format(is_external)
	current_date, adjust_hours, hide_watched = get_datetime_function(), date_offset_info(), is_home and widget_hide_watched()
	watched_info, bookmarks, watched_title = get_watched_info(watched_indicators), get_bookmarks(watched_indicators, 'episode'), 'Trakt' if watched_indicators == 1 else 'Fen Light'
	show_all_episodes = all_episodes in (1, 2)
	category_name = _get_category_name()
	if list_type == 'episode.next':
		include_unwatched, include_unaired = nextep_include_unwatched(), nextep_include_unaired()
		data = get_next_episodes(watched_info)
		if watched_indicators == 1:
			resformat, resinsert = '%Y-%m-%dT%H:%M:%S.%fZ', '2000-01-01T00:00:00.000Z'
			list_type = 'episode.next_trakt'
		else:
			resformat, resinsert = '%Y-%m-%d %H:%M:%S', '2000-01-01 00:00:00'
			list_type = 'episode.next_fenlight'
		hidden_data = get_hidden_progress_items(watched_indicators)
		data = [i for i in data if not i['media_ids']['tmdb'] in hidden_data]
		if include_unwatched != 0:
			if include_unwatched in (1, 3):
				try:
					original_list = trakt_watchlist('watchlist', 'tvshow')
					unwatched.extend([{'media_ids': i['media_ids'], 'season': 1, 'episode': 0, 'unwatched': True, 'title': i['title']} \
								for i in original_list])
				except: pass
			if include_unwatched in (2, 3):
				try: unwatched.extend([{'media_ids': {'tmdb': int(i['tmdb_id'])}, 'season': 1, 'episode': 0, 'unwatched': True, 'title': i['title']} \
									for i in favorites_cache.get_favorites('tvshow') if not int(i['tmdb_id']) in [x['media_ids']['tmdb'] for x in data]])
				except: pass
			data += unwatched
	elif list_type == 'episode.progress': data = get_in_progress_episodes()
	elif list_type == 'episode.recently_watched': data = get_recently_watched('episode')
	else:#episode.trakt
		recently_aired = params.get('recently_aired', None)
		data = trakt_get_my_calendar(recently_aired, get_datetime_function())
		list_type = 'episode.trakt_recently_aired' if recently_aired else 'episode.trakt_calendar'
		try: data = sorted(data, key=lambda i: (i['sort_title'], i.get('first_aired', '2100-12-31')), reverse=True)
		except: data = sorted(data, key=lambda i: (i['sort_title']), reverse=True)
	list_type_compare = list_type.split('episode.')[1]
	list_type_starts_with = list_type_compare.startswith
	threads = list(make_thread_list_enumerate(_process, data))
	[i.join() for i in threads]
	if list_type_starts_with('next_'):
		try: item_list = sorted(item_list, key=lambda i: jsondate_to_datetime_function(i['last_played'], resformat), reverse=True)
		except: pass
		if unwatched:
			unwatched = [i for i in item_list if i['unwatched']]
			item_list = [i for i in item_list if not i in unwatched]
		unaired = [i for i in item_list if i['unaired']]
		aired = [i for i in item_list if not i in unaired]
		item_list = aired + unaired + unwatched
	else:
		item_list.sort(key=lambda i: i['sort_order'])
		if list_type_compare in ('trakt_calendar', 'trakt_recently_aired'):
			if list_type_compare == 'trakt_calendar': reverse = False
			else: reverse = True
			try: item_list = sorted(item_list, key=lambda i: i.get('first_aired', '2100-12-31'), reverse=reverse)
			except:
				item_list = [i for i in item_list if i.get('first_aired') not in (None, 'None', '')]
				item_list = sorted(item_list, key=lambda i: i.get('first_aired'), reverse=reverse)
	add_items(handle, [i['list_items'] for i in item_list])
	set_content(handle, content_type)
	set_category(handle, category_name)
	end_directory(handle, cacheToDisc=False)
	set_view_mode(single_view, content_type, is_external)
