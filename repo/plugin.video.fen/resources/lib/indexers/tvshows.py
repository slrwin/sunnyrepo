# -*- coding: utf-8 -*-
from modules import kodi_utils, settings
from modules.metadata import tvshow_meta
from modules.utils import manual_function_import, get_datetime, make_thread_list_enumerate, get_current_timestamp
from modules.watched_status import get_watched_info_tv, get_watched_status_tvshow
# logger = kodi_utils.logger

meta_function, get_datetime_function, add_item, select_dialog, xbmc_actor = tvshow_meta, get_datetime, kodi_utils.add_item, kodi_utils.select_dialog, kodi_utils.xbmc_actor
kodi_version, get_watched_function, get_watched_info_function = kodi_utils.kodi_version, get_watched_status_tvshow, get_watched_info_tv
set_content, end_directory, set_view_mode, get_infolabel = kodi_utils.set_content, kodi_utils.end_directory, kodi_utils.set_view_mode, kodi_utils.get_infolabel
string, ls, sys, external_browse, add_items, add_dir = str, kodi_utils.local_string, kodi_utils.sys, kodi_utils.external_browse, kodi_utils.add_items, kodi_utils.add_dir
make_listitem, build_url, remove_keys, dict_removals = kodi_utils.make_listitem, kodi_utils.build_url, kodi_utils.remove_keys, kodi_utils.tvshow_dict_removals
metadata_user_info, watched_indicators, page_reference = settings.metadata_user_info, settings.watched_indicators, settings.page_reference
sleep, extras_open_action, get_art_provider, default_all_episodes = kodi_utils.sleep, settings.extras_open_action, settings.get_art_provider, settings.default_all_episodes
poster_empty, fanart_empty, build_content, include_year_in_title = kodi_utils.empty_poster, kodi_utils.addon_fanart, kodi_utils.build_content, settings.include_year_in_title
max_threads, widget_hide_next_page, fen_clearlogo = settings.max_threads, settings.widget_hide_next_page, kodi_utils.addon_clearlogo
make_placeholder = kodi_utils.make_placeholder_listitem
fen_str, trakt_str, watched_str, unwatched_str, exit_str, nextpage_str, browse_str, jumpto_str = ls(32036), ls(32037), ls(32642), ls(32643), ls(32650), ls(32799), ls(32652), ls(32964)
extras_str, options_str, refr_widg_str = ls(32645), ls(32646), ls(40001)
run_plugin, container_update, container_refresh = 'RunPlugin(%s)', 'Container.Update(%s)', 'Container.Refresh(%s)'
tmdb_main = ('tmdb_tv_popular', 'tmdb_tv_premieres', 'tmdb_tv_airing_today','tmdb_tv_on_the_air','tmdb_tv_upcoming')
tmdb_special = {'tmdb_tv_languages': 'language', 'tmdb_tv_networks': 'network_id', 'tmdb_tv_year': 'year', 'tmdb_tv_decade': 'decade', 'tmdb_tv_recommendations': 'tmdb_id',
					'tmdb_tv_genres': 'genre_id', 'tmdb_tv_search': 'query'}
trakt_main = ('trakt_tv_trending', 'trakt_tv_trending_recent', 'trakt_recommendations', 'trakt_tv_most_watched')
trakt_personal, imdb_personal = ('trakt_collection', 'trakt_watchlist', 'trakt_collection_lists'), ('imdb_watchlist', 'imdb_user_list_contents', 'imdb_keywords_list_contents')
personal = {'in_progress_tvshows': ('modules.watched_status', 'get_in_progress_tvshows'), 'favorites_tvshows': ('modules.favorites', 'get_favorites'),
				'watched_tvshows': ('modules.watched_status', 'get_watched_items')}
view_mode, content_type = 'view.tvshows', 'tvshows'


class TVShows:
	def __init__(self, params):
		self.params = params
		self.params_get = self.params.get
		self.id_type, self.list, self.action = self.params_get('id_type', 'tmdb_id'), self.params_get('list', []), self.params_get('action', None)
		self.items, self.new_page, self.total_pages, self.is_widget, self.max_threads = [], {}, None, external_browse(), max_threads()
		self.widget_hide_next_page = False if not self.is_widget else widget_hide_next_page()
		self.exit_list_params = self.params_get('exit_list_params', None) or get_infolabel('Container.FolderPath')
		self.append = self.items.append
	
	def fetch_list(self):
		handle = int(sys.argv[1])
		if build_content():
			try:
				mode = self.params_get('mode')
				try: page_no = int(self.params_get('new_page', '1'))
				except ValueError: page_no = self.params_get('new_page')
				if self.action in personal: var_module, import_function = personal[self.action]
				else: var_module, import_function = 'apis.%s_api' % self.action.split('_')[0], self.action
				try: function = manual_function_import(var_module, import_function)
				except: pass
				if self.action in tmdb_main:
					data = function(page_no)
					self.list = [i['id'] for i in data['results']]
					if data['total_pages'] > page_no: self.new_page = {'new_page': string(page_no + 1)}
				elif self.action in tmdb_special:
					key = tmdb_special[self.action]
					function_var = self.params_get(key, None)
					if not function_var: return
					data = function(function_var, page_no)
					self.list = [i['id'] for i in data['results']]
					if data['total_pages'] > page_no: self.new_page = {'new_page': string(page_no + 1), key: function_var}
				elif self.action in personal:
					data, all_pages, total_pages = function('tvshow', page_no)
					self.list = [i['media_id'] for i in data]
					if total_pages > 2: self.total_pages = total_pages
					if total_pages > page_no: self.new_page = {'new_page': string(page_no + 1)}
				elif self.action in trakt_main:
					self.id_type = 'trakt_dict'
					data = function(page_no)
					try: self.list = [i['show']['ids'] for i in data]
					except: self.list = [i['ids'] for i in data]
					if self.action != 'trakt_recommendations': self.new_page = {'new_page': string(page_no + 1)}
				elif self.action in trakt_personal:
					self.id_type = 'trakt_dict'
					data, all_pages, total_pages = function('shows', page_no)
					self.list = [i['media_ids'] for i in data]
					if total_pages > 2: self.total_pages = total_pages
					try:
						if total_pages > page_no: self.new_page = {'new_page': string(page_no + 1)}
					except: pass
				elif self.action in imdb_personal:
					self.id_type = 'imdb_id'
					list_id = self.params_get('list_id', None)
					data, next_page = function('tvshow', list_id, page_no)
					self.list = [i['imdb_id'] for i in data]
					if next_page: self.new_page = {'list_id': list_id, 'new_page': string(page_no + 1)}
				elif self.action == 'tmdb_tv_discover':
					from indexers.discover import set_history
					name, query = self.params['name'], self.params['query']
					if page_no == 1: set_history('tvshow', name, query)
					data = function(query, page_no)
					self.list = [i['id'] for i in data['results']]
					if data['page'] < data['total_pages']: self.new_page = {'query': query, 'name': name, 'new_page': string(data['page'] + 1)}
				elif self.action == 'trakt_tv_certifications':
					self.id_type = 'trakt_dict'
					data = function(self.params['certification'], page_no)
					self.list = [i['show']['ids'] for i in data]
					self.new_page = {'new_page': string(page_no + 1), 'certification': self.params['certification']}
				if self.total_pages and not self.is_widget:
					page_ref = page_reference()
					if page_ref != 3:
						url_params = {'mode': 'navigate_to_page_choice', 'media_type': 'TV Shows', 'current_page': page_no, 'total_pages': self.total_pages, 'transfer_mode': mode,
									'transfer_action': self.action, 'query': self.params_get('search_name', ''), 'all_pages': all_pages, 'page_reference': page_ref}
						add_dir(url_params, jumpto_str, handle, 'item_jump', isFolder=False)
				add_items(handle, self.worker())
				if self.new_page and not self.widget_hide_next_page:
						self.new_page.update({'mode': mode, 'action': self.action, 'exit_list_params': self.exit_list_params})
						add_dir(self.new_page, nextpage_str % self.new_page['new_page'], handle, 'item_next')
			except: pass
		else: add_items(handle, make_placeholder())
		set_content(handle, content_type)
		end_directory(handle, False if self.is_widget else None)
		if not self.is_widget:
			if self.params_get('refreshed') == 'true': sleep(1000)
			set_view_mode(view_mode, content_type)

	def build_tvshow_content(self, item_position, _id):
		try:
			meta = meta_function(self.id_type, _id, self.meta_user_info, self.current_date, self.current_time)
			if not meta or 'blank_entry' in meta: return
			meta_get = meta.get
			tmdb_id, total_seasons, total_aired_eps = meta_get('tmdb_id'), meta_get('total_seasons'), meta_get('total_aired_eps')
			playcount, overlay, total_watched, total_unwatched = get_watched_function(self.watched_info, string(tmdb_id), total_aired_eps)
			try: progress = int((float(total_watched)/total_aired_eps)*100)
			except: progress = 0
			cm = []
			cm_append = cm.append
			listitem = make_listitem()
			set_properties = listitem.setProperties
			rootname, title, year, trailer = meta_get('rootname'), meta_get('title'), meta_get('year'), meta_get('trailer')
			tvdb_id, imdb_id = meta_get('tvdb_id'), meta_get('imdb_id')
			poster = meta_get('custom_poster') or meta_get(self.poster_main) or meta_get(self.poster_backup) or poster_empty
			fanart = meta_get('custom_fanart') or meta_get(self.fanart_main) or meta_get(self.fanart_backup) or fanart_empty
			clearlogo = meta_get('custom_clearlogo') or meta_get(self.clearlogo_main) or meta_get(self.clearlogo_backup) or ''
			if self.fanart_enabled:
				banner, clearart = meta_get('custom_banner') or meta_get('banner') or '', meta_get('custom_clearart') or meta_get('clearart') or ''
				landscape = meta_get('custom_landscape') or meta_get('landscape') or ''
			else: banner, clearart, landscape = '', '', ''
			options_params = build_url({'mode': 'options_menu_choice', 'content': 'tvshow', 'tmdb_id': tmdb_id, 'poster': poster, 'playcount': playcount,
										'progress': progress, 'exit_menu': self.exit_list_params, 'is_widget': self.is_widget})
			extras_params = build_url({'mode': 'extras_menu_choice', 'tmdb_id': tmdb_id, 'media_type': 'tvshow', 'is_widget': self.is_widget})
			if self.all_episodes:
				if self.all_episodes == 1 and total_seasons > 1: url_params = build_url({'mode': 'build_season_list', 'tmdb_id': tmdb_id})
				else: url_params = build_url({'mode': 'build_episode_list', 'tmdb_id': tmdb_id, 'season': 'all'})
			else: url_params = build_url({'mode': 'build_season_list', 'tmdb_id': tmdb_id})
			if self.open_extras:
				cm_append((browse_str, container_update % url_params))
				url_params = extras_params
			else: cm_append((extras_str, run_plugin % extras_params))
			cm_append((options_str, run_plugin % options_params))
			if not playcount:
				cm_append((watched_str % self.watched_title, run_plugin % build_url({'mode': 'watched_status.mark_tvshow', 'action': 'mark_as_watched', 'title': title, 'year': year,
																					'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id})))
			elif self.widget_hide_watched: return
			if progress:
				cm_append((unwatched_str % self.watched_title, run_plugin % build_url({'mode': 'watched_status.mark_tvshow', 'action': 'mark_as_unwatched', 'title': title,
																						'year': year, 'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id})))
				set_properties({'watchedepisodes': string(total_watched), 'unwatchedepisodes': string(total_unwatched)})
			set_properties({'watchedprogress': string(progress), 'totalepisodes': string(total_aired_eps), 'totalseasons': string(total_seasons)})
			if not self.is_widget: cm_append((exit_str, container_refresh % self.exit_list_params))
			display = rootname if self.include_year else title
			listitem.setLabel(display)
			listitem.addContextMenuItems(cm)
			listitem.setArt({'poster': poster, 'fanart': fanart, 'icon': poster, 'banner': banner, 'clearart': clearart, 'clearlogo': clearlogo, 'thumb': landscape,
							'landscape': landscape, 'tvshow.poster': poster, 'tvshow.clearart': clearart, 'tvshow.clearlogo': clearlogo})
			if kodi_version >= 20:
				if self.is_widget: cm_append((refr_widg_str, run_plugin % build_url({'mode': 'kodi_refresh'})))
				info_tag = listitem.getVideoInfoTag()
				info_tag.setMediaType('tvshow')
				info_tag.setTitle(display)
				info_tag.setTvShowTitle(title)
				info_tag.setOriginalTitle(meta_get('original_title'))
				info_tag.setTvShowStatus(meta_get('status'))
				info_tag.setPlot(meta_get('plot'))
				info_tag.setYear(int(year))
				info_tag.setRating(meta_get('rating'))
				info_tag.setVotes(meta_get('votes'))
				info_tag.setMpaa(meta_get('mpaa'))
				info_tag.setDuration(meta_get('duration'))
				info_tag.setCountries(meta_get('country'))
				info_tag.setPlaycount(playcount)
				info_tag.setTrailer(meta_get('trailer'))
				info_tag.setPremiered(meta_get('premiered'))
				info_tag.setTagLine(meta_get('tagline'))
				info_tag.setStudios((meta_get('studio') or '',))
				info_tag.setUniqueIDs({'imdb': imdb_id, 'tmdb': string(tmdb_id), 'tvdb': string(tvdb_id)})
				info_tag.setIMDBNumber(imdb_id)
				info_tag.setGenres(meta_get('genre').split(', '))
				info_tag.setWriters(meta_get('writer').split(', '))
				info_tag.setDirectors(meta_get('director').split(', '))
				info_tag.setCast([xbmc_actor(name=item['name'], role=item['role'], thumbnail=item['thumbnail']) for item in meta_get('cast', [])])
				if self.is_widget: listitem.setInfo('video', {'overlay': overlay})# needs to stay until setPlaycount works
			else:
				meta.update({'playcount': playcount, 'overlay': overlay})
				listitem.setCast(meta_get('cast', []))
				listitem.setInfo('video', remove_keys(meta, dict_removals))
				listitem.setUniqueIDs({'imdb': imdb_id, 'tmdb': string(tmdb_id), 'tvdb': string(tvdb_id)})
			set_properties({'fen.sort_order': string(item_position), 'fen.playcount': string(playcount), 'fen.extras_params': extras_params, 'fen.options_params': options_params})
			if self.is_widget: set_properties({'fen.widget': 'true'})
			self.append((url_params, listitem, self.is_folder))
		except: pass

	def worker(self):
		self.is_widget_arg = 'true' if self.is_widget else 'false'
		self.current_date, self.current_time = get_datetime_function(), get_current_timestamp()
		self.meta_user_info, self.watched_indicators, self.include_year = metadata_user_info(), watched_indicators(), include_year_in_title('tvshow')
		self.watched_info, self.all_episodes, self.open_extras = get_watched_info_function(self.watched_indicators), default_all_episodes(), extras_open_action('tvshow')
		self.fanart_enabled, self.widget_hide_watched = self.meta_user_info['extra_fanart_enabled'], self.is_widget and self.meta_user_info['widget_hide_watched']
		self.is_folder, self.watched_title = False if self.open_extras else True, trakt_str if self.watched_indicators == 1 else fen_str
		self.poster_main, self.poster_backup, self.fanart_main, self.fanart_backup, self.clearlogo_main, self.clearlogo_backup = get_art_provider()
		threads = list(make_thread_list_enumerate(self.build_tvshow_content, self.list, self.max_threads))
		[i.join() for i in threads]
		self.items.sort(key=lambda k: int(k[1].getProperty('fen.sort_order')))
		return self.items
