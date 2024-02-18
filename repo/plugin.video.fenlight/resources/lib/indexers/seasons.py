# -*- coding: utf-8 -*-
from modules import kodi_utils, settings
from modules.metadata import tvshow_meta
from modules.utils import adjust_premiered_date, get_datetime
from modules.watched_status import get_watched_info_tv, get_watched_status_season
# logger = kodi_utils.logger

poster_empty, fanart_empty, xbmc_actor, set_category, home = kodi_utils.empty_poster, kodi_utils.default_addon_fanart, kodi_utils.xbmc_actor, kodi_utils.set_category, kodi_utils.home
sys, add_items, set_content, end_directory, set_view_mode = kodi_utils.sys, kodi_utils.add_items, kodi_utils.set_content, kodi_utils.end_directory, kodi_utils.set_view_mode
make_listitem, build_url, external, date_offset_info = kodi_utils.make_listitem, kodi_utils.build_url, kodi_utils.external, settings.date_offset
use_minimal_media_info, watched_indicators_info, widget_hide_watched = settings.use_minimal_media_info, settings.watched_indicators, settings.widget_hide_watched
adjust_premiered_date_function, get_datetime_function, get_watched_status, get_watched_info = adjust_premiered_date, get_datetime, get_watched_status_season, get_watched_info_tv
string, run_plugin, unaired_label, tmdb_poster = str, 'RunPlugin(%s)', '[COLOR red][I]%s[/I][/COLOR]', 'https://image.tmdb.org/t/p/w780%s'
view_mode, content_type = 'view.seasons', 'seasons'
season_name_str = 'Season %s'

def build_season_list(params):
	def _process():
		running_ep_count = total_aired_eps
		for item in season_data:
			try:
				listitem = make_listitem()
				set_properties = listitem.setProperties
				cm = []
				cm_append, item_get = cm.append, item.get
				overview, poster_path, air_date = item_get('overview'), item_get('poster_path'), item_get('air_date')
				season_number, episode_count = item_get('season_number'), item_get('episode_count')
				season_name = item_get('name', None)
				title = item_get('name', None) or season_name_str % season_number
				first_airdate, premiered = adjust_premiered_date_function(air_date, adjust_hours)
				poster = tmdb_poster % poster_path if poster_path is not None else show_poster
				if season_number == 0: unaired = False
				elif episode_count == 0: unaired = True
				elif season_number != total_seasons: unaired = False
				else:
					if not first_airdate or current_date < first_airdate: unaired = True
					else: unaired = False
				if unaired:
					episode_count = 0
				elif not season_number == 0:
					running_ep_count -= episode_count
					if running_ep_count < 0: episode_count = running_ep_count + episode_count
				try: year = air_date.split('-')[0]
				except: year = show_year or '2050'
				plot = overview or show_plot
				if unaired: title = unaired_label % title
				playcount, watched, unwatched = get_watched_status(watched_info, str_tmdb_id, season_number, episode_count)
				try: progress = int((float(watched)/episode_count)*100)
				except: progress = 0
				url_params = build_url({'mode': 'build_episode_list', 'tmdb_id': tmdb_id, 'season': season_number})
				extras_params = build_url({'mode': 'extras_menu_choice', 'tmdb_id': tmdb_id, 'media_type': 'tvshow', 'is_external': is_external})
				options_params = build_url({'mode': 'options_menu_choice', 'content': 'season', 'tmdb_id': tmdb_id, 'poster': show_poster, 'playcount': playcount,
											'progress': progress, 'season': season_number, 'is_external': is_external, 'unaired': unaired, 'season_poster': poster})
				cm_append(('[B]Extras...[/B]', run_plugin % extras_params))
				cm_append(('[B]Options...[/B]', run_plugin % options_params))
				if playcount:
					if hide_watched: continue
				elif not unaired:
					cm_append(('[B]Mark Watched %s[/B]' % watched_title, run_plugin % build_url({'mode': 'watched_status.mark_season', 'action': 'mark_as_watched',
														'title': show_title, 'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id, 'season': season_number})))
				if progress:
					cm_append(('[B]Mark Unwatched %s[/B]' % watched_title, run_plugin % build_url({'mode': 'watched_status.mark_season', 'action': 'mark_as_unwatched',
														'title': show_title, 'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id, 'season': season_number})))
					set_properties({'watchedepisodes': string(watched), 'unwatchedepisodes': string(unwatched)})
				set_properties({'totalepisodes': string(episode_count), 'watchedprogress': string(progress),
								'fenlight.extras_params': extras_params, 'fenlight.options_params': options_params})
				if is_home: cm_append(('[B]Refresh Widgets[/B]', run_plugin % build_url({'mode': 'kodi_refresh'})))
				info_tag = listitem.getVideoInfoTag()
				info_tag.setMediaType('season'), info_tag.setTitle(title), info_tag.setOriginalTitle(orig_title), info_tag.setTvShowTitle(show_title), info_tag.setIMDBNumber(imdb_id)
				info_tag.setSeason(season_number), info_tag.setPlot(plot), info_tag.setDuration(episode_run_time), info_tag.setPlaycount(playcount), info_tag.setGenres(genre)
				info_tag.setUniqueIDs({'imdb': imdb_id, 'tmdb': str_tmdb_id, 'tvdb': str_tvdb_id})
				if not use_minimal_media:
					info_tag.setTvShowStatus(status), info_tag.setFirstAired(premiered), info_tag.setStudios(studio), info_tag.setYear(int(year))
					info_tag.setRating(rating), info_tag.setVotes(votes), info_tag.setMpaa(mpaa), info_tag.setCountries(country), info_tag.setTrailer(trailer)
					info_tag.setCast([xbmc_actor(name=item['name'], role=item['role'], thumbnail=item['thumbnail']) for item in cast])
				listitem.setLabel(title)
				listitem.setArt({'poster': poster, 'season.poster': poster, 'fanart': show_fanart, 'clearlogo': show_clearlogo,
								'tvshow.poster': poster, 'tvshow.clearlogo': show_clearlogo})
				listitem.addContextMenuItems(cm)
				yield (url_params, listitem, True)
			except: pass
	handle, is_external, is_home, category_name = int(sys.argv[1]), external(), home(), 'Season'
	watched_indicators, use_minimal_media, adjust_hours, hide_watched = watched_indicators_info(), use_minimal_media_info(), date_offset_info(), is_home and widget_hide_watched()
	watched_info, current_date = get_watched_info(watched_indicators), get_datetime_function()
	meta = tvshow_meta('tmdb_id', params['tmdb_id'], current_date)
	meta_get = meta.get
	tmdb_id, tvdb_id, imdb_id, show_title, show_year = meta_get('tmdb_id'), meta_get('tvdb_id'), meta_get('imdb_id'), meta_get('title'), meta_get('year') or '2050'
	orig_title, status, show_plot, total_aired_eps = meta_get('original_title', ''), meta_get('status'), meta_get('plot'), meta_get('total_aired_eps')
	str_tmdb_id, str_tvdb_id, rating, genre = string(tmdb_id), string(tvdb_id), meta_get('rating'), meta_get('genre')
	cast, mpaa, votes, trailer, studio, country = meta_get('cast', []), meta_get('mpaa'), meta_get('votes'), string(meta_get('trailer')), meta_get('studio'), meta_get('country')
	episode_run_time, season_data, total_seasons = meta_get('duration'), meta_get('season_data'), meta_get('total_seasons')
	show_poster = meta_get('poster') or poster_empty
	show_fanart = meta_get('fanart') or fanart_empty
	show_clearlogo = meta_get('clearlogo') or ''
	season_data = [i for i in season_data if not i['season_number'] == 0]
	season_data.sort(key=lambda k: k['season_number'])
	watched_title = 'Trakt' if watched_indicators == 1 else 'Fen Light'
	add_items(handle, list(_process()))
	category_name = show_title
	set_content(handle, content_type)
	set_category(handle, category_name)
	end_directory(handle, cacheToDisc=False if is_external else True)
	set_view_mode(view_mode, content_type, is_external)
