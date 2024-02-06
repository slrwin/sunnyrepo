# -*- coding: utf-8 -*-
from caches.navigator_cache import navigator_cache as nc
from caches.settings_cache import get_setting, set_setting
from modules import meta_lists as ml, kodi_utils as k, settings as s
from modules.watched_status import get_recently_watched
# logger = k.logger

tp, sys, build_url, notification, addon, make_listitem, list_dirs = k.translate_path, k.sys, k.build_url, k.notification, k.addon, k.make_listitem, k.list_dirs
add_item, set_content, end_directory, set_view_mode, add_items, get_infolabel = k.add_item, k.set_content, k.end_directory, k.set_view_mode, k.add_items, k.get_infolabel
set_sort_method, set_category, container_refresh_input, current_window_object = k.set_sort_method, k.set_category, k.container_refresh_input, k.current_window_object
json, close_all_dialog, sleep, home, get_property, fanart = k.json, k.close_all_dialog, k.sleep, k.home, k.get_property, k.get_addon_fanart()
download_directory, easynews_authorized, get_icon, unquote, container_refresh = s.download_directory, s.easynews_authorized, k.get_icon, k.unquote, k.container_refresh
get_shortcut_folders, currently_used_list, get_shortcut_folder_contents = nc.get_shortcut_folders, nc.currently_used_list, nc.get_shortcut_folder_contents
get_main_lists, authorized_debrid_check = nc.get_main_lists, s.authorized_debrid_check
log_loc, old_log_loc = tp('special://logpath/kodi.log'), tp('special://logpath/kodi.old.log')
folder_icon = get_icon('folder')
run_plugin = 'RunPlugin(%s)'
mm_str, sf_str = 'menu_editor.%s', 'menu_editor.shortcut_folder_edit'
random_list_dict = {'movie': nc.random_movie_lists, 'tvshow': nc.random_tvshow_lists, 'trakt': nc.random_trakt_lists}
search_mode_dict = {'movie': ('movie_queries', {'mode': 'search.get_key_id', 'media_type': 'movie', 'isFolder': 'false'}),
				'tvshow': ('tvshow_queries', {'mode': 'search.get_key_id', 'media_type': 'tv_show', 'isFolder': 'false'}),
				'people': ('people_queries', {'mode': 'search.get_key_id', 'search_type': 'people', 'isFolder': 'false'}),
				'tmdb_keyword_movie': ('keyword_tmdb_movie_queries', {'mode': 'search.get_key_id', 'search_type': 'tmdb_keyword', 'media_type': 'movie', 'isFolder': 'false'}),
				'tmdb_keyword_tvshow': ('keyword_tmdb_tvshow_queries', {'mode': 'search.get_key_id', 'search_type': 'tmdb_keyword', 'media_type': 'tvshow', 'isFolder': 'false'}),
				'easynews_video': ('easynews_video_queries', {'mode': 'search.get_key_id', 'search_type': 'easynews_video', 'isFolder': 'false'})}

class Navigator:
	def __init__(self, params):
		self.params = params
		self.params_get = self.params.get
		self.category_name = self.params_get('name', 'Fen Light')
		self.list_name = self.params_get('action', 'RootList')
		self.is_home = home()

	def main(self):
		add_items(int(sys.argv[1]), list(self.build_main_list()))
		self.end_directory()

	def discover(self):
		self.add({'mode': 'navigator.discover_contents', 'media_type': 'movie'}, 'Discover Movies', 'movies')
		self.add({'mode': 'navigator.discover_contents', 'media_type': 'tvshow'}, 'Discover TV Shows', 'tv')
		self.end_directory()

	def premium(self):
		if authorized_debrid_check('rd'): self.add({'mode': 'navigator.real_debrid'}, 'Real Debrid', 'realdebrid')
		if authorized_debrid_check('pm'): self.add({'mode': 'navigator.premiumize'}, 'Premiumize', 'premiumize')
		if authorized_debrid_check('ad'): self.add({'mode': 'navigator.alldebrid'}, 'All Debrid', 'alldebrid')
		if easynews_authorized(): self.add({'mode': 'navigator.easynews'}, 'Easynews', 'easynews')
		self.end_directory()

	def easynews(self):
		self.add({'mode': 'navigator.search_history', 'action': 'easynews_video'}, 'Search', 'search')
		self.add({'mode': 'easynews.account_info', 'isFolder': 'false'}, 'Account Info', 'easynews')
		self.end_directory()

	def real_debrid(self):
		self.add({'mode': 'real_debrid.rd_cloud'}, 'Cloud Storage', 'realdebrid')
		self.add({'mode': 'real_debrid.rd_downloads'}, 'History', 'realdebrid')
		self.add({'mode': 'real_debrid.rd_account_info', 'isFolder': 'false'}, 'Account Info', 'realdebrid')
		self.end_directory()

	def premiumize(self):
		self.add({'mode': 'premiumize.pm_cloud'}, 'Cloud Storage', 'premiumize')
		self.add({'mode': 'premiumize.pm_transfers'}, 'History', 'premiumize')
		self.add({'mode': 'premiumize.pm_account_info', 'isFolder': 'false'}, 'Account Info', 'premiumize')
		self.end_directory()

	def alldebrid(self):
		self.add({'mode': 'alldebrid.ad_cloud'}, 'Cloud Storage', 'alldebrid')
		self.add({'mode': 'alldebrid.ad_account_info', 'isFolder': 'false'}, 'Account Info', 'alldebrid')
		self.end_directory()

	def favorites(self):
		self.add({'mode': 'build_movie_list', 'action': 'favorites_movies', 'name': 'Movies'}, 'Movies', 'movies')
		self.add({'mode': 'build_tvshow_list', 'action': 'favorites_tvshows', 'name': 'TV Shows'}, 'TV Shows', 'tv')
		self.end_directory()

	def my_content(self):
		if get_setting('fenlight.trakt.user', 'empty_setting') not in ('empty_setting', ''):
			self.add({'mode': 'navigator.trakt_collections'}, 'Trakt Collection', 'trakt')
			self.add({'mode': 'navigator.trakt_watchlists'}, 'Trakt Watchlist', 'trakt')
			self.add({'mode': 'trakt.list.get_trakt_lists', 'list_type': 'my_lists', 'build_list': 'true', 'category_name': 'My Lists'}, 'Trakt My Lists', 'trakt')
			self.add({'mode': 'trakt.list.get_trakt_lists', 'list_type': 'liked_lists', 'build_list': 'true', 'category_name': 'Liked Lists'}, 'Trakt Liked Lists', 'trakt')
			self.add({'mode': 'navigator.trakt_favorites', 'category_name': 'Favorites'}, 'Trakt Favorites', 'trakt')
			self.add({'mode': 'navigator.trakt_recommendations', 'category_name': 'Recommended'}, 'Trakt Recommended', 'trakt')
			self.add({'mode': 'build_my_calendar'}, 'Trakt Calendar', 'trakt')
		self.add({'mode': 'trakt.list.get_trakt_trending_popular_lists', 'list_type': 'trending', 'category_name': 'Trending User Lists'}, 'Trending User Lists', 'trakt')
		self.add({'mode': 'trakt.list.get_trakt_trending_popular_lists', 'list_type': 'popular', 'category_name': 'Popular User Lists'}, 'Popular User Lists', 'trakt')
		self.add({'mode': 'search.get_key_id', 'search_type': 'trakt_lists', 'isFolder': 'false'}, 'Search Lists...', 'search')
		self.end_directory()

	def random_lists(self):
		self.add({'mode': 'navigator.build_random_lists', 'menu_type': 'movie'}, 'Movie Lists', 'movies')
		self.add({'mode': 'navigator.build_random_lists', 'menu_type': 'tvshow'}, 'TV Show Lists', 'tv')
		if get_setting('fenlight.trakt.user', 'empty_setting') not in ('empty_setting', ''):
			self.add({'mode': 'navigator.build_random_lists', 'menu_type': 'trakt'}, 'Trakt Lists', 'trakt')
		self.end_directory()

	def trakt_collections(self):
		self.category_name = 'Collection'
		self.add({'mode': 'build_movie_list', 'action': 'trakt_collection', 'category_name': 'Movies Collection'}, 'Movies', 'trakt')
		self.add({'mode': 'build_tvshow_list', 'action': 'trakt_collection', 'category_name': 'TV Shows Collection'}, 'TV Shows', 'trakt')
		self.add({'mode': 'build_movie_list', 'action': 'trakt_collection_lists', 'new_page': 'recent', 'category_name': 'Recently Added Movies'}, 'Recently Added Movies', 'trakt')
		self.add({'mode': 'build_tvshow_list', 'action': 'trakt_collection_lists', 'new_page': 'recent', 'category_name': 'Recently Added TV Shows'},
					'Recently Added TV Shows', 'trakt')
		self.add({'mode': 'build_my_calendar', 'recently_aired': 'true'}, 'Recently Aired Episodes', 'trakt')
		self.end_directory()

	def trakt_watchlists(self):
		self.category_name = 'Watchlist'
		self.add({'mode': 'build_movie_list', 'action': 'trakt_watchlist', 'category_name': 'Movies Watchlist'}, 'Movies', 'trakt')
		self.add({'mode': 'build_tvshow_list', 'action': 'trakt_watchlist', 'category_name': 'TV Shows Watchlist'}, 'TV Shows', 'trakt')
		self.add({'mode': 'build_movie_list', 'action': 'trakt_watchlist_lists', 'new_page': 'recent', 'category_name': 'Recently Added Movies'}, 'Recently Added Movies', 'trakt')
		self.add({'mode': 'build_tvshow_list', 'action': 'trakt_watchlist_lists', 'new_page': 'recent', 'category_name': 'Recently Added TV Shows'},
					'Recently Added TV Shows', 'trakt')
		self.end_directory()

	def trakt_recommendations(self):
		self.category_name = 'Recommended'
		self.add({'mode': 'build_movie_list', 'action': 'trakt_recommendations', 'new_page': 'movies', 'category_name': 'Recommended Movies'}, 'Movies', 'trakt')
		self.add({'mode': 'build_tvshow_list', 'action': 'trakt_recommendations', 'new_page': 'shows', 'category_name': 'Recommended TV Shows'}, 'TV Shows', 'trakt')
		self.end_directory()

	def trakt_favorites(self):
		self.category_name = 'Favorites'
		self.add({'mode': 'build_movie_list', 'action': 'trakt_favorites', 'category_name': 'Favorite Movies'}, 'Movies', 'trakt')
		self.add({'mode': 'build_tvshow_list', 'action': 'trakt_favorites', 'category_name': 'Favorite TV Shows'}, 'TV Shows', 'trakt')
		self.end_directory()

	def people(self):
		self.add({'mode': 'build_tmdb_people', 'action': 'popular', 'isFolder': 'false', 'name': 'Popular'}, 'Popular', 'popular')
		self.add({'mode': 'build_tmdb_people', 'action': 'day', 'isFolder': 'false', 'name': 'Trending'}, 'Trending', 'trending')
		self.add({'mode': 'build_tmdb_people', 'action': 'week', 'isFolder': 'false', 'name': 'Trending This Week'}, 'Trending This Week', 'trending_recent')
		self.end_directory()

	def search(self):
		self.add({'mode': 'navigator.search_history', 'action': 'movie', 'name': 'Movies'}, 'Movies', 'search_movie')
		self.add({'mode': 'navigator.search_history', 'action': 'tvshow', 'name': 'TV Shows'}, 'TV Shows', 'search_tv')
		self.add({'mode': 'navigator.search_history', 'action': 'people', 'name': 'People'}, 'People', 'search_people')
		self.add({'mode': 'navigator.search_history', 'action': 'tmdb_keyword_movie', 'name': 'Keywords (Movies)'}, 'Keywords (Movies)', 'search_tmdb')
		self.add({'mode': 'navigator.search_history', 'action': 'tmdb_keyword_tvshow', 'name': 'Keywords (TV Shows)'}, 'Keywords (TV Shows)', 'search_tmdb')
		self.end_directory()

	def downloads(self):
		self.add({'mode': 'downloader.manager', 'name': 'Download Manager', 'isFolder': 'false'}, 'Download Manager', 'downloads')
		self.add({'mode': 'downloader.viewer', 'folder_type': 'movie', 'name': 'Movies'}, 'Movies', 'movies')
		self.add({'mode': 'downloader.viewer', 'folder_type': 'episode', 'name': 'TV Shows'}, 'TV Shows', 'tv')
		self.add({'mode': 'downloader.viewer', 'folder_type': 'premium', 'name': 'Premium Files'}, 'Premium Files', 'premium')
		self.add({'mode': 'browser_image', 'folder_path': download_directory('image'), 'isFolder': 'false'}, 'Images', 'people')
		self.end_directory()

	def tools(self):
		self.add({'mode': 'open_settings', 'isFolder': 'false'}, 'Settings', 'settings')
		if get_property('fenlight.external_scraper.module') not in ('empty_setting', ''):
			self.add({'mode': 'open_external_scraper_settings', 'isFolder': 'false'}, 'Open External Scraper Settings', 'settings')
		self.add({'mode': 'navigator.tips'}, 'Tips for Use', 'settings2')
		self.add({'mode': 'navigator.set_view_modes'}, 'Set Views', 'settings2')
		self.add({'mode': 'build_next_episode_manager'}, 'TV Shows Progress Manager', 'settings2')
		self.add({'mode': 'navigator.shortcut_folders'}, 'Shortcut Folders Manager', 'settings2')
		self.add({'mode': 'navigator.changelog_utils'}, 'Changelog & Log Utils', 'settings2')
		self.add({'mode': 'navigator.maintenance'}, 'Database & Cache Maintenance', 'settings2')
		self.add({'mode': 'update_check', 'isFolder': 'false'}, 'Check For Updates', 'settings2')
		self.add({'mode': 'toggle_language_invoker', 'isFolder': 'false'}, 'Toggle Language Invoker (ADVANCED!!)', 'settings2')
		self.end_directory()

	def maintenance(self):
		self.add({'mode': 'check_databases_integrity_cache', 'isFolder': 'false'}, 'Check for Corrupt Databases', 'settings')
		self.add({'mode': 'clean_databases_cache', 'isFolder': 'false'}, 'Clean Databases', 'settings')
		self.add({'mode': 'sync_settings', 'silent': 'false', 'isFolder': 'false'}, 'Remake Settings Cache', 'settings')
		self.add({'mode': 'clear_all_cache', 'isFolder': 'false'}, 'Clear All Cache (Excluding Favorites)', 'settings')
		self.add({'mode': 'clear_favorites_choice', 'isFolder': 'false'}, 'Clear Favorites Cache', 'settings')
		self.add({'mode': 'search.clear_search', 'isFolder': 'false'}, 'Clear Search History Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'main', 'isFolder': 'false'}, 'Clear Main Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'meta', 'isFolder': 'false'}, 'Clear Meta Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'list', 'isFolder': 'false'}, 'Clear Lists Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'trakt', 'isFolder': 'false'}, 'Clear Trakt Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'imdb', 'isFolder': 'false'}, 'Clear IMDb Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'internal_scrapers', 'isFolder': 'false'}, 'Clear Internal Scrapers Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'external_scrapers', 'isFolder': 'false'}, 'Clear External Scrapers Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'rd_cloud', 'isFolder': 'false'}, 'Clear Real Debrid Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'pm_cloud', 'isFolder': 'false'}, 'Clear Premiumize Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'ad_cloud', 'isFolder': 'false'}, 'Clear All Debrid Cache', 'settings')
		self.end_directory()

	def set_view_modes(self):
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.main', 'content': '', 'name': 'menus'}, 'Menus', 'settings', False)
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.movies', 'content': 'movies'}, 'Movies', 'settings', False)
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.tvshows', 'content': 'tvshows'}, 'TV Shows', 'settings', False)
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.seasons', 'content': 'seasons'}, 'Seasons', 'settings', False)
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.episodes', 'content': 'episodes'}, 'Episodes', 'settings', False)
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.episodes_single', 'content': 'episodes', 'name': 'episode lists'}, 'Episode Lists', 'settings', False)
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.premium', 'content': 'files', 'name': 'premium files'}, 'Premium Files', 'settings', False)
		self.end_directory()

	def changelog_utils(self):
		fenlight_clogpath = tp('special://home/addons/plugin.video.fenlight/resources/text/changelog.txt')
		self.add({'mode': 'show_text', 'heading': 'Changelog', 'file': fenlight_clogpath, 'font_size': 'large', 'isFolder': 'false'}, 'Changelog', 'lists', False)
		self.add({'mode': 'show_text', 'heading': 'Kodi Log Viewer', 'file': log_loc, 'kodi_log': 'true', 'isFolder': 'false'}, 'Kodi Log Viewer', 'lists', False)
		self.add({'mode': 'show_text', 'heading': 'Kodi Log Viewer (Old)', 'file': old_log_loc, 'kodi_log': 'true', 'isFolder': 'false'},
			'Kodi Log Viewer (Old)', 'lists', False)
		self.add({'mode': 'upload_logfile', 'isFolder': 'false'}, 'Upload Kodi Log to Pastebin', 'lists', False)
		self.end_directory()

	def certifications(self):
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie': mode, action, certifications = 'build_movie_list', 'tmdb_movies_certifications', ml.movie_certifications
		else: mode, action, certifications = 'build_tvshow_list', 'trakt_tv_certifications', ml.tvshow_certifications
		if 'random' in self.params: return self.handle_random(menu_type, action)
		for i in certifications: self.add({'mode': mode, 'action': action, 'key_id': i['id'], 'name': i['name']}, i['name'], 'certifications')
		self.end_directory()

	def languages(self):
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie': mode, action = 'build_movie_list', 'tmdb_movies_languages'
		else: mode, action = 'build_tvshow_list', 'tmdb_tv_languages'
		if 'random' in self.params: return self.handle_random(menu_type, action)
		for i in ml.languages: self.add({'mode': mode, 'action': action, 'key_id': i['id'], 'name': i['name']}, i['name'], 'languages')
		self.end_directory()

	def years(self):
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie': mode, action, years = 'build_movie_list', 'tmdb_movies_year', ml.years_movies
		else: mode, action, years = 'build_tvshow_list', 'tmdb_tv_year', ml.years_tvshows
		if 'random' in self.params: return self.handle_random(menu_type, action)
		for i in years: self.add({'mode': mode, 'action': action, 'key_id': i['id'], 'name': i['name']}, i['name'], 'calender')
		self.end_directory()

	def decades(self):
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie': mode, action, decades = 'build_movie_list', 'tmdb_movies_decade', ml.decades_movies
		else: mode, action, decades = 'build_tvshow_list', 'tmdb_tv_decade', ml.decades_tvshows
		if 'random' in self.params: return self.handle_random(menu_type, action)
		for i in decades: self.add({'mode': mode, 'action': action, 'key_id': i['id'], 'name': i['name']}, i['name'], 'calendar_decades')
		self.end_directory()

	def networks(self):
		if self.params_get('menu_type') == 'movie': return
		mode, action, networks = 'build_tvshow_list', 'tmdb_tv_networks', sorted(ml.networks, key=lambda k: k['name'])
		if 'random' in self.params: return self.handle_random(menu_type, action)
		for i in networks: self.add({'mode': mode, 'action': action, 'key_id': i['id'], 'name': i['name']}, i['name'], i['icon'])
		self.end_directory()

	def providers(self):
		menu_type = self.params_get('menu_type')
		image_insert = 'https://image.tmdb.org/t/p/original/%s'
		if menu_type == 'movie': mode, action, providers = 'build_movie_list', 'tmdb_movies_providers', ml.watch_providers_movies
		else: mode, action, providers = 'build_tvshow_list', 'tmdb_tv_providers', ml.watch_providers_tvshows
		if 'random' in self.params: return self.handle_random(menu_type, action)
		for i in providers: self.add({'mode': mode, 'action': action, 'key_id': i['id'], 'name': i['name']}, i['name'], image_insert % i['icon'], original_image=True)
		self.end_directory()

	def genres(self):
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie': genre_list, mode, action = ml.movie_genres, 'build_movie_list', 'tmdb_movies_genres'
		else: genre_list, mode, action = ml.tvshow_genres, 'build_tvshow_list', 'tmdb_tv_genres'
		if 'random' in self.params: return self.handle_random(menu_type, action)
		for i in genre_list: self.add({'mode': mode, 'action': action, 'key_id': i['id'], 'name': i['name']}, i['name'], i['icon'])
		self.end_directory()

	def search_history(self):
		from caches.main_cache import main_cache
		def _builder():
			for i in data:
				try:
					listitem = make_listitem()
					key_id = unquote(i)
					url_params['key_id'] = key_id
					url_params['setting_id'] = setting_id
					url = build_url(url_params)
					if not self.is_home:
						cm = []
						cm.append(('[B]Remove from history[/B]', 'RunPlugin(%s)' % build_url({'mode': 'search.remove', 'setting_id':setting_id, 'key_id': key_id})))
						cm.append(('[B]Clear All History[/B]', 'RunPlugin(%s)' % build_url({'mode': 'search.clear_all', 'setting_id':setting_id, 'refresh': 'true'})))
						listitem.addContextMenuItems(cm)
					listitem.setLabel(key_id)
					listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon})
					info_tag = listitem.getVideoInfoTag()
					# info_tag.setMediaType('video')
					info_tag.setPlot(' ')
					yield (url, listitem, False)
				except: pass
		handle = int(sys.argv[1])
		icon = get_icon('search_history')
		setting_id, action_dict = search_mode_dict[self.list_name]
		url_params = dict(action_dict)
		data = main_cache.get(setting_id) or []
		self.add(action_dict, '[B]NEW SEARCH...[/B]', 'search_new', False)
		add_items(handle, list(_builder()))
		set_content(handle, '')
		set_category(handle, self.params_get('name') or 'History')
		end_directory(handle, cacheToDisc=False)
		set_view_mode('view.main', '')

	def keyword_results(self):
		from apis.tmdb_api import tmdb_keywords_by_query
		def _builder():
			for item in results:
				try:
					name = item['name'].upper()
					url_params = {'mode': mode, 'action': action, 'key_id': item['id'], 'iconImage': 'tmdb', 'category_name': name}
					url = build_url(url_params)
					listitem = make_listitem()
					listitem.setLabel(name)
					listitem.setArt({'icon': tmdb_icon, 'poster': tmdb_icon, 'thumb': tmdb_icon, 'fanart': fanart, 'banner': tmdb_icon})
					info_tag = listitem.getVideoInfoTag()
					# info_tag.setMediaType('video')
					info_tag.setPlot(' ')
					yield (url, listitem, True)
				except: pass
		handle = int(sys.argv[1])
		tmdb_icon = get_icon('tmdb')
		media_type, key_id = self.params_get('media_type'), self.params_get('key_id') or self.params_get('query')
		try: page_no = int(self.params_get('new_page', '1'))
		except: page_no = self.params_get('new_page')
		mode = 'build_movie_list' if media_type == 'movie' else 'build_tvshow_list'
		action = 'tmdb_movie_keyword_results' if media_type == 'movie' else 'tmdb_tv_keyword_results'
		data = tmdb_keywords_by_query(key_id, page_no)
		results = data['results']
		add_items(handle, list(_builder()))
		if data['total_pages'] > page_no:
			new_page = {'mode': 'navigator.keyword_results', 'key_id': key_id, 'category_name': self.category_name, 'new_page': str(data['page'] + 1)}
			self.add(new_page, 'Next Page (%s) >>' % new_page['new_page'], 'nextpage', False)
		set_content(handle, 'files')
		set_category(handle, 'Search Results for %s' % key_id.upper())
		end_directory(handle)
		set_view_mode('view.main')

	def choose_view(self):
		view_type, content = self.params['view_type'], self.params['content']
		name = self.params.get('name') or content
		handle = int(sys.argv[1])
		self.add({'mode': 'navigator.set_view', 'view_type': view_type, 'name': name, 'isFolder': 'false'}, 'Set view and then click here', 'settings', False)
		set_content(handle, content)
		end_directory(handle)
		set_view_mode(view_type, content, False)

	def set_view(self):
		set_setting(self.params['view_type'], str(current_window_object().getFocusId()))
		notification('%s: %s' % (self.params['name'].upper(), get_infolabel('Container.Viewmode').upper()), time=500)

	def folder_navigator(self):
		from os.path import join as pjoin
		from modules.utils import clean_file_name, normalize
		def _process():
			for info in results:
				try:
					path = info[0]
					clean_title = clean_file_name(normalize(path))
					display = clean_title
					url = pjoin(folder_path, path)
					listitem = make_listitem()
					listitem.addContextMenuItems(cm)
					listitem.setLabel(display)
					listitem.setArt({'fanart': fanart})
					info_tag = listitem.getVideoInfoTag()
					# info_tag.setMediaType('video')
					info_tag.setPlot(' ')
					yield (url, listitem, info[1])
				except: pass
		folder_path = self.params_get('folder_path')
		dirs, files = list_dirs(folder_path)
		results = [(i, True) for i in dirs] + [(i, False) for i in files]
		item_list = list(_process())
		handle = int(sys.argv[1])
		add_items(handle, item_list)
		set_sort_method(handle, 'files')
		self.end_directory()
		set_view_mode('view.main', '')
	
	def shortcut_folders(self):
		def _builder():
			for i in folders:
				try:
					name = i[0]
					listitem = make_listitem()
					url = build_url({'mode': 'navigator.build_shortcut_folder_contents', 'name': name, 'iconImage': 'folder'})
					if not self.is_home:
						cm = []
						cm.append(('[B]Rename[/B]', run_plugin % build_url({'mode': 'menu_editor.shortcut_folder_rename'})))
						cm.append(('[B]Delete Shortcut Folder[/B]' , run_plugin % build_url({'mode': 'menu_editor.shortcut_folder_delete'})))
						cm.append(('[B]Make New Shortcut Folder[/B]' , run_plugin % build_url({'mode': 'menu_editor.shortcut_folder_make'})))
						listitem.addContextMenuItems(cm)
					listitem.setLabel(name)
					listitem.setArt({'icon': folder_icon, 'poster': folder_icon, 'thumb': folder_icon, 'fanart': fanart, 'banner': folder_icon})
					info_tag = listitem.getVideoInfoTag()
					# info_tag.setMediaType('video')
					info_tag.setPlot(' ')
					yield (url, listitem, True)
				except: pass
		folders = get_shortcut_folders()
		if folders: add_items(int(sys.argv[1]), list(_builder()))
		else: self.add({'mode': 'menu_editor.shortcut_folder_make', 'isFolder': 'false'}, '[I]Make New Shortcut Folder...[/I]', 'new')
		self.end_directory()

	def build_shortcut_folder_contents(self):
		def _process():
			for pos, item in enumerate(contents):
				try:
					item_get = item.get
					name = item_get('name')
					iconImage = item_get('iconImage', None)
					if iconImage: icon = iconImage if iconImage.startswith('http') else get_icon(item_get('iconImage'))
					else: icon = folder_icon
					listitem = make_listitem()
					cm = []
					cm.append(('[B]Move[/B]', run_plugin % build_url({'mode': sf_str, 'active_list': list_name, 'position': pos, 'action': 'move'})))
					cm.append(('[B]Remove[/B]' , run_plugin % build_url({'mode': sf_str, 'active_list': list_name, 'position': pos, 'action': 'remove'})))
					cm.append(('[B]Add Content[/B]' , run_plugin % build_url({'mode': 'menu_editor.shortcut_folder_add', 'name': list_name})))
					cm.append(('[B]Rename[/B]' , run_plugin % build_url({'mode': sf_str, 'active_list': list_name, 'position': pos, 'action': 'rename'})))
					cm.append(('[B]Clear All[/B]' , run_plugin % build_url({'mode': sf_str, 'active_list': list_name, 'position': pos, 'action': 'clear'})))
					listitem.addContextMenuItems(cm)
					listitem.setLabel(name)
					listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon})
					info_tag = listitem.getVideoInfoTag()
					# info_tag.setMediaType('video')
					info_tag.setPlot(' ')
					isFolder = item.get('isFolder', 'true') == 'true'
					yield (build_url(item), listitem, isFolder)
				except: pass
		list_name = self.params_get('name')
		contents = get_shortcut_folder_contents(list_name)
		if contents: add_items(int(sys.argv[1]), list(_process()))
		else: self.add({'mode': 'menu_editor.shortcut_folder_add', 'name': list_name, 'isFolder': 'false'}, '[I]Add Content...[/I]', 'new', False)
		self.end_directory()

	def discover_contents(self):
		from caches.discover_cache import discover_cache
		action, media_type = self.params_get('action', ''), self.params_get('media_type')
		if not action:
			self.add({'mode': 'discover_choice', 'media_type': media_type, 'isFolder': 'false'}, '[I]Make New Discover List...[/I]', 'new')
			results = discover_cache.get_all(media_type)
			if media_type == 'movie': mode, action = 'build_movie_list', 'tmdb_movies_discover'
			else: mode, action = 'build_tvshow_list', 'tmdb_tv_discover'
			def _builder():
				for item in results:
					listitem = make_listitem()
					name = item['id']
					url_params = {'mode': mode, 'action': action, 'name': name, 'url': item['data']}
					url = build_url(url_params)
					if not self.is_home:
						cm = []
						cm.append(('[B]Remove from history[/B]', 'RunPlugin(%s)' % build_url({'mode': 'navigator.discover_contents', 'action':'delete_one', 'name': name})))
						cm.append(('[B]Clear All History[/B]', 'RunPlugin(%s)' % build_url({'mode': 'navigator.discover_contents', 'action':'delete_all', 'media_type': media_type})))
						listitem.addContextMenuItems(cm)
					listitem.setLabel(name)
					listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon})
					info_tag = listitem.getVideoInfoTag()
					# info_tag.setMediaType('video')
					info_tag.setPlot(' ')
					yield (url, listitem, True)
			handle = int(sys.argv[1])
			icon = get_icon('discover')
			add_items(handle, list(_builder()))
			set_content(handle, 'files')
			set_category(handle, 'Discover')
			end_directory(handle)
			set_view_mode('view.main')
		else:
			if action == 'delete_one': discover_cache.delete_one(self.params_get('name'))
			elif action == 'delete_all': discover_cache.delete_all(media_type)
			container_refresh()

	def exit_media_menu(self):
		params = get_property('fenlight.exit_params')
		if params: return container_refresh_input(params)

	def tips(self):
		tips_location = 'special://home/addons/plugin.video.fenlight/resources/text/tips'
		files = sorted(list_dirs(tips_location)[1])
		tips_location = tips_location + '/%s'
		tips_list = []
		tips_append = tips_list.append
		for item in files:
			tip = item.replace('.txt', '')[4:]
			if '!!HELP!!' in tip: tip, sort_order = tip.replace('!!HELP!!', '[COLOR crimson]HELP!!![/COLOR] '), 0
			elif '!!NEW!!' in tip: tip, sort_order = tip.replace('!!NEW!!', '[COLOR chartreuse]NEW!![/COLOR] '), 1
			elif '!!SPOTLIGHT!!' in tip: tip, sort_order = tip.replace('!!SPOTLIGHT!!', '[COLOR orange]SPOTLIGHT![/COLOR] '), 2
			else: sort_order = 3
			action = {'mode': 'show_text', 'heading': tip, 'file': tp(tips_location % item), 'font_size': 'large', 'isFolder': 'false'}
			tips_append((action, tip, sort_order))
		item_list = sorted(tips_list, key=lambda x: x[2])
		for c, i in enumerate(item_list, 1): self.add(i[0], '[B]%02d. [/B]%s' % (c, i[1]), 'information', False)
		self.end_directory()

	def because_you_watched(self):
		media_type = self.params_get('menu_type')
		mode, action = ('build_movie_list', 'tmdb_movies_recommendations') if media_type == 'movie' else ('build_tvshow_list', 'tmdb_tv_recommendations')
		recently_watched = get_recently_watched(media_type, short_list=0)
		for item in recently_watched:
			if media_type == 'movie': name, tmdb_id = item['title'], item['media_id']
			else: name, tmdb_id = '%s - %sx%s' % (item['title'], str(item['season']), str(item['episode'])), item['media_ids']['tmdb']
			self.add({'mode': mode, 'action': action, 'key_id': tmdb_id, 'name': 'Because You Watched %s' % name}, name, 'because_you_watched', False)
		self.end_directory()

	def build_main_list(self):
		if self.params_get('full_list', 'false') == 'true': browse_list = get_main_lists(self.list_name)[0]
		else: browse_list = currently_used_list(self.list_name)
		for pos, item in enumerate(browse_list):
			try:
				item_get = item.get
				isFolder = item_get('isFolder', 'true') == 'true'
				if not isFolder and self.is_home: continue
				listitem = make_listitem()
				iconImage = item_get('iconImage')
				icon = iconImage if iconImage.startswith('http') else get_icon(iconImage)
				if not self.is_home:
					cm = []
					cm.append(('[B]Move[/B]', run_plugin % build_url({'mode': mm_str % 'move', 'active_list': self.list_name, 'position': pos})))
					cm.append(('[B]Remove[/B]', run_plugin % build_url({'mode': mm_str % 'remove', 'active_list': self.list_name, 'position': pos})))
					cm.append(('[B]Add Content[/B]', run_plugin % build_url({'mode': mm_str % 'add', 'active_list': self.list_name, 'position': pos})))
					cm.append(('[B]Restore Menu[/B]', run_plugin % build_url({'mode': mm_str % 'restore', 'active_list': self.list_name, 'position': pos})))
					cm.append(('[B]Check for New Menu Items[/B]', run_plugin % build_url({'mode': mm_str % 'update', 'active_list': self.list_name, 'position': pos})))
					cm.append(('[B]Reload Menu[/B]', run_plugin % build_url({'mode': mm_str % 'reload', 'active_list': self.list_name, 'position': pos})))
					cm.append(('[B]Browse Removed items[/B]', run_plugin % build_url({'mode': mm_str % 'browse', 'active_list': self.list_name, 'position': pos})))
					listitem.addContextMenuItems(cm)
				listitem.setLabel(item_get('name', ''))
				listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon, 'landscape': icon})
				info_tag = listitem.getVideoInfoTag()
				# info_tag.setMediaType('video')
				info_tag.setPlot(' ')
				yield (build_url(item), listitem, isFolder)
			except: pass

	def build_random_lists(self):
		menu_type = self.params_get('menu_type')
		self.category_name = 'Random Movie Lists' if menu_type == 'movie' else 'Random TV Show Lists' if menu_type == 'tvshow' else 'Random Trakt Lists'
		for item in random_list_dict[menu_type](): self.add(item, item['name'], item['iconImage'])
		self.end_directory()

	def handle_random(self, menu_type, action):
		if menu_type == 'movie': from indexers.movies import Movies as function
		else: from indexers.tvshows import TVShows as function
		return function({'action': action, 'random': 'true'}).fetch_list()

	def add(self, url_params, list_name, iconImage='folder', original_image=False):
		isFolder = url_params.get('isFolder', 'true') == 'true'
		if original_image: icon = iconImage
		else: icon = get_icon(iconImage)
		url_params['iconImage'] = icon
		url = build_url(url_params)
		listitem = make_listitem()
		listitem.setLabel(list_name)
		listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon, 'landscape': icon})
		info_tag = listitem.getVideoInfoTag()
		# info_tag.setMediaType('video')
		info_tag.setPlot(' ')
		add_item(int(sys.argv[1]), url, listitem, isFolder)

	def end_directory(self):
		handle = int(sys.argv[1])
		set_content(handle, '')
		set_category(handle, self.category_name)
		end_directory(handle)
		set_view_mode('view.main', '')
