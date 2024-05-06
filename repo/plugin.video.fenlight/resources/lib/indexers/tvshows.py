# -*- coding: utf-8 -*-
from modules import meta_lists
from modules import kodi_utils, settings
from modules.metadata import tvshow_meta
from modules.utils import manual_function_import, get_datetime, make_thread_list_enumerate, make_thread_list_multi_arg, get_current_timestamp, paginate_list
from modules.watched_status import get_database, watched_info_tvshow, get_watched_status_tvshow, get_progress_status_tvshow
# logger = kodi_utils.logger

string, sys, external, add_items, add_dir, use_minimal_media_info = str, kodi_utils.sys, kodi_utils.external, kodi_utils.add_items, kodi_utils.add_dir, settings.use_minimal_media_info
sleep, meta_function, add_item, xbmc_actor, home, tmdb_api_key = kodi_utils.sleep, tvshow_meta, kodi_utils.add_item, kodi_utils.xbmc_actor, kodi_utils.home, settings.tmdb_api_key
set_category, json, make_listitem, build_url, set_property = kodi_utils.set_category, kodi_utils.json, kodi_utils.make_listitem, kodi_utils.build_url, kodi_utils.set_property
set_content, end_directory, set_view_mode, folder_path = kodi_utils.set_content, kodi_utils.end_directory, kodi_utils.set_view_mode, kodi_utils.folder_path
poster_empty, fanart_empty, nextpage_landscape = kodi_utils.empty_poster, kodi_utils.default_addon_fanart, kodi_utils.nextpage_landscape
extras_open_action, default_all_episodes, page_limit, paginate = settings.extras_open_action, settings.default_all_episodes, settings.page_limit, settings.paginate
widget_hide_next_page, widget_hide_watched, watched_indicators = settings.widget_hide_next_page, settings.widget_hide_watched, settings.watched_indicators
run_plugin, container_update = 'RunPlugin(%s)', 'Container.Update(%s)'
main = ('tmdb_tv_popular', 'tmdb_tv_popular_today', 'tmdb_tv_premieres', 'tmdb_tv_airing_today','tmdb_tv_on_the_air','tmdb_tv_upcoming')
special = ('tmdb_tv_languages', 'tmdb_tv_networks', 'tmdb_tv_providers', 'tmdb_tv_year', 'tmdb_tv_decade', 'tmdb_tv_recommendations', 'tmdb_tv_genres',
'tmdb_tv_search', 'tmdb_tv_keyword_results', 'tmdb_tv_keyword_results_direct')
personal = {'in_progress_tvshows': ('modules.watched_status', 'get_in_progress_tvshows'), 'favorites_tvshows': ('modules.favorites', 'get_favorites'),
'watched_tvshows': ('modules.watched_status', 'get_watched_items')}
trakt_main = ('trakt_tv_trending', 'trakt_tv_trending_recent', 'trakt_recommendations', 'trakt_tv_most_watched', 'trakt_tv_most_favorited')
trakt_special = ('trakt_tv_certifications',)
trakt_personal = ('trakt_collection', 'trakt_watchlist', 'trakt_collection_lists', 'trakt_watchlist_lists', 'trakt_favorites')
meta_list_dict = {'tmdb_tv_languages': meta_lists.languages, 'tmdb_tv_networks': meta_lists.networks, 'tmdb_tv_providers': meta_lists.watch_providers_tvshows,
'tmdb_tv_year': meta_lists.years_tvshows, 'tmdb_tv_decade': meta_lists.decades_tvshows, 'tmdb_tv_genres': meta_lists.tvshow_genres,
'trakt_tv_certifications': meta_lists.tvshow_certifications}
view_mode, content_type = 'view.tvshows', 'tvshows'
internal_nav_check = ('build_season_list', 'build_episode_list')

class TVShows:
	def __init__(self, params):
		self.params = params
		self.params_get = self.params.get
		self.category_name = self.params_get('category_name', None) or self.params_get('name', None) or 'TV Shows'
		self.id_type, self.list, self.action = self.params_get('id_type', 'tmdb_id'), self.params_get('list', []), self.params_get('action', None)
		self.items, self.new_page, self.total_pages, self.is_external, self.is_home = [], {}, None, external(), home()
		self.widget_hide_next_page = self.is_home and widget_hide_next_page()
		self.widget_hide_watched = self.is_home and widget_hide_watched()
		self.custom_order = self.params_get('custom_order', 'false') == 'true'
		self.paginate_start = int(self.params_get('paginate_start', '0'))
		self.in_progress_menu = 'true' if self.action == 'in_progress_tvshows' else 'false'
		self.append = self.items.append
	
	def fetch_list(self):
		handle = int(sys.argv[1])
		try:
			is_random = self.params_get('random', 'false') == 'true'
			try: page_no = int(self.params_get('new_page', '1'))
			except: page_no = self.params_get('new_page')
			if page_no == 1 and not self.is_external:
				folderpath = folder_path()
				if not any([x in folderpath for x in internal_nav_check]): set_property('fenlight.exit_params', folderpath)
			if self.action in personal: var_module, import_function = personal[self.action]
			else: var_module, import_function = 'apis.%s_api' % self.action.split('_')[0], self.action
			try: function = manual_function_import(var_module, import_function)
			except: pass
			if self.action in main:
				data = function(page_no)
				self.list = [i['id'] for i in data['results']]
				if not is_random and  data['total_pages'] > page_no: self.new_page = {'new_page': string(page_no + 1)}
			elif self.action in special:
				key_id = self.params_get('key_id') or self.params_get('query')
				if not key_id: return
				data = function(key_id, page_no)
				self.list = [i['id'] for i in data['results']]
				if not is_random and data['total_pages'] > page_no: self.new_page = {'new_page': string(page_no + 1), 'key_id': key_id}
			elif self.action in personal:
				data = function('tvshow', page_no)
				data, total_pages = self.paginate_list(data, page_no)
				self.list = [i['media_id'] for i in data]
				if total_pages > 2: self.total_pages = total_pages
				if total_pages > page_no: self.new_page = {'new_page': string(page_no + 1), 'paginate_start': self.paginate_start}
			elif self.action in trakt_main:
				self.id_type = 'trakt_dict'
				data = function(page_no)
				try: self.list = [i['show']['ids'] for i in data]
				except: self.list = [i['ids'] for i in data]
				if not is_random and self.action != 'trakt_recommendations': self.new_page = {'new_page': string(page_no + 1)}
			elif self.action in trakt_special:
				self.id_type = 'trakt_dict'
				key_id = self.params_get('key_id', None)
				if not key_id: return
				data = function(key_id, page_no)
				self.list = [i['show']['ids'] for i in data]
				if not is_random: self.new_page = {'new_page': string(page_no + 1), 'key_id': key_id}
			elif self.action in trakt_personal:
				self.id_type = 'trakt_dict'
				data = function('shows', page_no)
				if self.action in ('trakt_collection_lists', 'trakt_watchlist_lists', 'trakt_favorites'): total_pages = 1
				else: data, total_pages = self.paginate_list(data, page_no)
				self.list = [i['media_ids'] for i in data]
				if total_pages > 2: self.total_pages = total_pages
				try:
					if total_pages > page_no: self.new_page = {'new_page': string(page_no + 1), 'paginate_start': self.paginate_start}
				except: pass
			elif self.action == 'tmdb_tv_discover':
				url = self.params_get('url')
				data = function(url, page_no)
				self.list = [i['id'] for i in data['results']]
				if data['total_pages'] > page_no: self.new_page = {'url': url, 'new_page': string(data['page'] + 1)}
			add_items(handle, self.worker())
			if self.new_page and not self.widget_hide_next_page:
							self.new_page.update({'mode': 'build_tvshow_list', 'action': self.action, 'category_name': self.category_name})
							add_dir(self.new_page, 'Next Page (%s) >>' % self.new_page['new_page'], handle, 'nextpage', nextpage_landscape)
		except: pass
		set_content(handle, content_type)
		set_category(handle, self.category_name)
		end_directory(handle, cacheToDisc=False if self.is_external else True)
		if not self.is_external:
			if self.params_get('refreshed') == 'true': sleep(1000)
			set_view_mode(view_mode, content_type, self.is_external)

	def build_tvshow_content(self, _position, _id):
		try:
			meta = meta_function(self.id_type, _id, self.tmdb_api_key, self.current_date, self.current_time)
			if not meta or 'blank_entry' in meta: return
			cm = []
			cm_append = cm.append
			listitem = make_listitem()
			set_properties = listitem.setProperties
			meta_get = meta.get
			premiered = meta_get('premiered')
			trailer, title, year = meta_get('trailer'), meta_get('title'), meta_get('year') or '2050'
			tvdb_id, imdb_id = meta_get('tvdb_id'), meta_get('imdb_id')
			poster, fanart, clearlogo, landscape = meta_get('poster') or poster_empty, meta_get('fanart') or fanart_empty, meta_get('clearlogo') or '', meta_get('landscape') or ''
			tmdb_id, total_seasons, total_aired_eps = meta_get('tmdb_id'), meta_get('total_seasons'), meta_get('total_aired_eps')
			unaired = total_aired_eps == 0
			if unaired: progress, playcount, total_watched, total_unwatched = 0, 0, 0, total_aired_eps
			else:
				playcount, total_watched, total_unwatched = get_watched_status_tvshow(self.watched_info.get(string(tmdb_id), None), total_aired_eps)
				if total_watched: progress = get_progress_status_tvshow(total_watched, total_aired_eps)
				else: progress = 0
				visible_progress = 0 if progress == 100 else progress
			options_params = build_url({'mode': 'options_menu_choice', 'content': 'tvshow', 'tmdb_id': tmdb_id, 'poster': poster, 'playcount': playcount,
										'progress': progress, 'is_external': self.is_external, 'unaired': unaired, 'in_progress_menu': self.in_progress_menu})
			extras_params = build_url({'mode': 'extras_menu_choice', 'tmdb_id': tmdb_id, 'media_type': 'tvshow', 'is_external': self.is_external})
			if self.all_episodes:
				if self.all_episodes == 1 and total_seasons > 1: url_params = build_url({'mode': 'build_season_list', 'tmdb_id': tmdb_id})
				else: url_params = build_url({'mode': 'build_episode_list', 'tmdb_id': tmdb_id, 'season': 'all'})
			else: url_params = build_url({'mode': 'build_season_list', 'tmdb_id': tmdb_id})
			if self.open_extras:
				cm_append(('[B]Browse...[/B]', container_update % url_params))
				url_params = extras_params
			else: cm_append(('[B]Extras...[/B]', run_plugin % extras_params))
			cm_append(('[B]Options...[/B]', run_plugin % options_params))
			if playcount:
				if self.widget_hide_watched: return
			elif not unaired:
				cm_append(('[B]Mark Watched %s[/B]' % self.watched_title, run_plugin % build_url({'mode': 'watched_status.mark_tvshow', 'action': 'mark_as_watched',
																			'title': title,'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id})))
			if progress:
				cm_append(('[B]Mark Unwatched %s[/B]' % self.watched_title, run_plugin % build_url({'mode': 'watched_status.mark_tvshow', 'action': 'mark_as_unwatched',
																			'title': title, 'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id})))
				set_properties({'watchedepisodes': string(total_watched), 'unwatchedepisodes': string(total_unwatched)})
			set_properties({'watchedprogress': string(visible_progress), 'totalepisodes': string(total_aired_eps), 'totalseasons': string(total_seasons)})
			if self.is_home: cm_append(('[B]Refresh Widgets[/B]', run_plugin % build_url({'mode': 'kodi_refresh'})))
			else: cm_append(('[B]Exit TV Show List[/B]', run_plugin % build_url({'mode': 'navigator.exit_media_menu'})))
			listitem.setLabel(title)
			listitem.addContextMenuItems(cm)
			listitem.setArt({'poster': poster, 'fanart': fanart, 'icon': poster, 'clearlogo': clearlogo, 'landscape': landscape, 'thumb': landscape, 'icon': landscape,
							'tvshow.poster': poster, 'tvshow.clearlogo': clearlogo})
			info_tag = listitem.getVideoInfoTag()
			info_tag.setMediaType('tvshow'), info_tag.setTitle(title), info_tag.setTvShowTitle(title), info_tag.setOriginalTitle(meta_get('original_title'))
			info_tag.setUniqueIDs({'imdb': imdb_id, 'tmdb': string(tmdb_id), 'tvdb': string(tvdb_id)}), info_tag.setIMDBNumber(imdb_id)
			info_tag.setPlot(meta_get('plot')), info_tag.setPlaycount(playcount), info_tag.setGenres(meta_get('genre')), info_tag.setYear(int(year))
			if not self.use_minimal_media:
				info_tag.setTagLine(meta_get('tagline')), info_tag.setStudios(meta_get('studio')), info_tag.setWriters(meta_get('writer')), info_tag.setDirectors(meta_get('director'))
				info_tag.setVotes(meta_get('votes')), info_tag.setMpaa(meta_get('mpaa')), info_tag.setDuration(meta_get('duration')), info_tag.setCountries(meta_get('country'))
				info_tag.setTrailer(meta_get('trailer')), info_tag.setPremiered(premiered)
				info_tag.setTvShowStatus(meta_get('status')), info_tag.setRating(meta_get('rating'))
				info_tag.setCast([xbmc_actor(name=item['name'], role=item['role'], thumbnail=item['thumbnail']) for item in meta_get('cast', [])])
			set_properties({'fenlight.extras_params': extras_params, 'fenlight.options_params': options_params})
			self.append(((url_params, listitem, self.is_folder), _position))
		except: pass

	def worker(self):
		self.current_date, self.current_time, self.use_minimal_media, self.tmdb_api_key = get_datetime(), get_current_timestamp(), use_minimal_media_info(), tmdb_api_key()
		self.all_episodes, self.open_extras = default_all_episodes(), extras_open_action('tvshow')
		self.is_folder = False if self.open_extras else True
		self.watched_indicators = watched_indicators()
		self.watched_title = 'Trakt' if self.watched_indicators == 1 else 'Fen Light'
		self.watched_info = watched_info_tvshow(get_database(self.watched_indicators))
		if self.custom_order:
			threads = list(make_thread_list_multi_arg(self.build_tvshow_content, self.list))
			[i.join() for i in threads]
		else:
			threads = list(make_thread_list_enumerate(self.build_tvshow_content, self.list))
			[i.join() for i in threads]
			self.items.sort(key=lambda k: k[1])
			self.items = [i[0] for i in self.items]
		return self.items

	def paginate_list(self, data, page_no):
		if paginate(self.is_home):
			limit = page_limit(self.is_home)
			data, total_pages = paginate_list(data, page_no, limit, self.paginate_start)
			if self.is_home: self.paginate_start = limit
		else: total_pages = 1
		return data, total_pages
