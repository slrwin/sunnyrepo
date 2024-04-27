# -*- coding: utf-8 -*-
from caches.base_cache import connect_database
from modules.kodi_utils import get_property, set_property, clear_property
# from modules.kodi_utils import logger

GET_LIST = 'SELECT list_contents FROM navigator WHERE list_name = ? AND list_type = ?'
SET_LIST = 'INSERT OR REPLACE INTO navigator VALUES (?, ?, ?)'
DELETE_LIST = 'DELETE FROM navigator WHERE list_name=? and list_type=?'
GET_FOLDERS = 'SELECT list_name, list_contents FROM navigator WHERE list_type = ?'
GET_FOLDER_CONTENTS = 'SELECT list_contents FROM navigator WHERE list_name = ? AND list_type = ?'
prop_dict = {'default': 'fenlight_%s_default', 'edited': 'fenlight_%s_edited', 'shortcut_folder': 'fenlight_%s_shortcut_folder'}
timeout = 60

root_list = [
				{'name': 'Movies',
				'iconImage': 'movies',
				'mode': 'navigator.main',
				'action': 'MovieList'},
				{'name': 'TV Shows',
				'iconImage': 'tv',
				'mode': 'navigator.main',
				'action': 'TVShowList'},
				{'name': 'People',
				'iconImage': 'genre_family',
				'mode': 'navigator.people'},
				{'name': 'Search',
				'iconImage': 'search',
				'mode': 'navigator.search'},
				{'name': 'Discover',
				'iconImage': 'discover',
				'mode': 'navigator.discover'},
				{'name': 'Random Lists',
				'iconImage': 'random',
				'mode': 'navigator.random_lists'},
				{'name': 'My Lists',
				'iconImage': 'lists',
				'mode': 'navigator.my_content'},
				{'name': 'My Services',
				'iconImage': 'premium',
				'mode': 'navigator.premium'},
				{'name': 'Favorites',
				'iconImage': 'favorites',
				'mode': 'navigator.favorites'},
				{'name': 'Downloads',
				'iconImage': 'downloads',
				'mode': 'navigator.downloads'},
				{'name': 'Tools',
				'iconImage': 'settings2',
				'mode': 'navigator.tools'}
			]

movie_list = [
				{'name': 'Trending',
				'iconImage': 'trending',
				'mode': 'build_movie_list',
				'action': 'trakt_movies_trending',
				'random_support': 'true'},
				{'name': 'Trending Recent',
				'iconImage': 'trending_recent',
				'mode': 'build_movie_list',
				'action': 'trakt_movies_trending_recent',
				'random_support': 'true'},
				{'name': 'Popular',
				'iconImage': 'popular',
				'mode': 'build_movie_list',
				'action': 'tmdb_movies_popular',
				'random_support': 'true'},
				{'name': 'Popular Today',
				'iconImage': 'popular_today',
				'mode': 'build_movie_list',
				'action': 'tmdb_movies_popular_today',
				'random_support': 'true'},
				{'name': 'Premieres',
				'action': 'tmdb_movies_premieres',
				'iconImage': 'fresh',
				'mode': 'build_movie_list',
				'random_support': 'true'},
				{'name': 'Latest Releases',
				'iconImage': 'dvd',
				'mode': 'build_movie_list',
				'action': 'tmdb_movies_latest_releases',
				'random_support': 'true'},
				{'name': 'Most Watched',
				'iconImage': 'most_watched',
				'mode': 'build_movie_list',
				'action': 'trakt_movies_most_watched',
				'random_support': 'true'},
				{'name': 'Most Favorited',
				'iconImage': 'favorites',
				'mode': 'build_movie_list',
				'action': 'trakt_movies_most_favorited',
				'random_support': 'true'},
				{'name': 'Top 10 Box Office',
				'action': 'trakt_movies_top10_boxoffice',
				'iconImage': 'box_office',
				'mode': 'build_movie_list'},
				{'name': 'Blockbusters',
				'iconImage': 'most_voted',
				'mode': 'build_movie_list',
				'action': 'tmdb_movies_blockbusters',
				'random_support': 'true'},
				{'name': 'In Theaters',
				'iconImage': 'intheatres',
				'mode': 'build_movie_list',
				'action': 'tmdb_movies_in_theaters',
				'random_support': 'true'},
				{'name': 'Up Coming',
				'iconImage': 'lists',
				'mode': 'build_movie_list',
				'action': 'tmdb_movies_upcoming',
				'random_support': 'true'},
				{'name': 'Oscar Winners',
				'iconImage': 'oscar_winners',
				'mode': 'build_movie_list',
				'action': 'tmdb_movies_oscar_winners',
				'random_support': 'true'},
				{'name': 'Genres',
				'iconImage': 'genres',
				'mode': 'navigator.genres',
				'menu_type': 'movie',
				'random_support': 'true'},
				{'name': 'Providers',
				'iconImage': 'providers',
				'mode': 'navigator.providers',
				'menu_type': 'movie',
				'random_support': 'true'},
				{'name': 'Languages',
				'iconImage': 'languages',
				'mode': 'navigator.languages',
				'menu_type': 'movie',
				'random_support': 'true'},
				{'name': 'Years',
				'iconImage': 'calender',
				'mode': 'navigator.years',
				'menu_type': 'movie',
				'random_support': 'true'},
				{'name': 'Decades',
				'iconImage': 'calendar_decades',
				'mode': 'navigator.decades',
				'menu_type': 'movie',
				'random_support': 'true'},
				{'name': 'Certifications',
				'iconImage': 'certifications',
				'mode': 'navigator.certifications',
				'menu_type': 'movie',
				'random_support': 'true'},
				{'name': 'Because You Watched...',
				'iconImage': 'because_you_watched',
				'mode': 'navigator.because_you_watched',
				'menu_type': 'movie'},
				{'name': 'Watched',
				'iconImage': 'watched_1',
				'mode': 'build_movie_list',
				'action': 'watched_movies'},
				{'name': 'Recently Watched',
				'iconImage': 'watched_recent',
				'mode': 'build_movie_list',
				'action': 'recent_watched_movies'},
				{'name': 'In Progress',
				'iconImage': 'player',
				'mode': 'build_movie_list',
				'action': 'in_progress_movies'}
			]

tvshow_list = [
				{'name': 'Trending',
				'action': 'trakt_tv_trending',
				'iconImage': 'trending',
				'mode': 'build_tvshow_list',
				'random_support': 'true'},
				{'name': 'Trending Recent',
				'iconImage': 'trending_recent',
				'mode': 'build_tvshow_list',
				'action': 'trakt_tv_trending_recent',
				'random_support': 'true'},
				{'name': 'Popular',
				'action': 'tmdb_tv_popular',
				'iconImage': 'popular',
				'mode': 'build_tvshow_list',
				'random_support': 'true'},
				{'name': 'Popular Today',
				'action': 'tmdb_tv_popular_today',
				'iconImage': 'popular_today',
				'mode': 'build_tvshow_list',
				'random_support': 'true'},
				{'name': 'Premieres',
				'action': 'tmdb_tv_premieres',
				'iconImage': 'fresh',
				'mode': 'build_tvshow_list',
				'random_support': 'true'},
				{'name': 'Most Watched',
				'iconImage': 'most_watched',
				'mode': 'build_tvshow_list',
				'action': 'trakt_tv_most_watched',
				'random_support': 'true'},
				{'name': 'Most Favorited',
				'iconImage': 'favorites',
				'mode': 'build_tvshow_list',
				'action': 'trakt_tv_most_favorited',
				'random_support': 'true'},
				{'name': 'Airing Today',
				'action': 'tmdb_tv_airing_today',
				'iconImage': 'live',
				'mode': 'build_tvshow_list',
				'random_support': 'true'},
				{'name': 'On the Air',
				'action': 'tmdb_tv_on_the_air',
				'iconImage': 'ontheair',
				'mode': 'build_tvshow_list',
				'random_support': 'true'},
				{'name': 'Up Coming',
				'iconImage': 'lists',
				'mode': 'build_tvshow_list',
				'action': 'tmdb_tv_upcoming',
				'random_support': 'true'},
				{'name': 'Genres',
				'iconImage': 'genres',
				'mode': 'navigator.genres',
				'menu_type': 'tvshow',
				'random_support': 'true'},
				{'name': 'Providers',
				'iconImage': 'providers',
				'mode': 'navigator.providers',
				'menu_type': 'tvshow',
				'random_support': 'true'},
				{'name': 'Networks',
				'iconImage': 'networks',
				'mode': 'navigator.networks',
				'menu_type': 'tvshow',
				'random_support': 'true'},
				{'name': 'Languages',
				'iconImage': 'languages',
				'mode': 'navigator.languages',
				'menu_type': 'tvshow',
				'random_support': 'true'},
				{'name': 'Years',
				'iconImage': 'calender',
				'mode': 'navigator.years',
				'menu_type': 'tvshow',
				'random_support': 'true'},
				{'name': 'Decades',
				'iconImage': 'calendar_decades',
				'mode': 'navigator.decades',
				'menu_type': 'tvshow',
				'random_support': 'true'},
				{'name': 'Certifications',
				'iconImage': 'certifications',
				'mode': 'navigator.certifications',
				'menu_type': 'tvshow',
				'random_support': 'true'},
				{'name': 'Because You Watched...',
				'iconImage': 'because_you_watched',
				'mode': 'navigator.because_you_watched',
				'menu_type': 'tvshow'},
				{'name': 'Watched',
				'iconImage': 'watched_1',
				'mode': 'build_tvshow_list',
				'action': 'watched_tvshows'},
				{'name': 'In Progress',
				'action': 'in_progress_tvshows',
				'iconImage': 'in_progress_tvshow',
				'mode': 'build_tvshow_list'},
				{'name': 'Recently Watched Episodes',
				'iconImage': 'watched_recent',
				'mode': 'build_recently_watched_episode'},
				{'name': 'In Progress Episodes',
				'iconImage': 'player',
				'mode': 'build_in_progress_episode'},
				{'name': 'Next Episodes',
				'iconImage': 'next_episodes',
				'mode': 'build_next_episode'}
			]

default_menu_items = ('RootList', 'MovieList', 'TVShowList')
main_menus = {'RootList': root_list, 'MovieList': movie_list, 'TVShowList': tvshow_list}
main_menu_items = {'RootList': {'name': 'Root', 'iconImage': 'fenlight', 'mode': 'navigator.main', 'action': 'RootList'}, 'MovieList': root_list[0], 'TVShowList': root_list[1]}

class NavigatorCache:
	def get_main_lists(self, list_name):
		default_contents = self.get_memory_cache(list_name, 'default')
		if not default_contents:
			default_contents = self.get_list(list_name, 'default')
			if default_contents == None:
				self.rebuild_database()
				return self.get_main_lists(list_name)
			try: edited_contents = self.get_list(list_name, 'edited')
			except: edited_contents = None
		else: edited_contents = self.get_memory_cache(list_name, 'edited')
		return default_contents, edited_contents

	def get_list(self, list_name, list_type):
		contents = None
		try:
			dbcon = connect_database('navigator_db')
			contents = eval(dbcon.execute(GET_LIST, (list_name, list_type)).fetchone()[0])
		except: pass
		return contents

	def set_list(self, list_name, list_type, list_contents):
		dbcon = connect_database('navigator_db')
		dbcon.execute(SET_LIST, (list_name, list_type, repr(list_contents)))
		self.set_memory_cache(list_name, list_type, list_contents)

	def delete_list(self, list_name, list_type):
		dbcon = connect_database('navigator_db')
		dbcon.execute(DELETE_LIST, (list_name, list_type))
		self.delete_memory_cache(list_name, list_type)
		dbcon.execute('VACUUM')
	
	def get_memory_cache(self, list_name, list_type):
		try: return eval(get_property(self._get_list_prop(list_type) % list_name))
		except: return None
	
	def set_memory_cache(self, list_name, list_type, list_contents):
		set_property(self._get_list_prop(list_type) % list_name, repr(list_contents))

	def delete_memory_cache(self, list_name, list_type):
		clear_property(self._get_list_prop(list_type) % list_name)

	def get_shortcut_folders(self):
		try:
			dbcon = connect_database('navigator_db')
			folders = dbcon.execute(GET_FOLDERS, ('shortcut_folder',)).fetchall()
			folders = sorted([(str(i[0]), eval(i[1])) for i in folders], key=lambda s: s[0].lower())
		except: folders = []
		return folders

	def get_shortcut_folder_contents(self, list_name):
		try:
			dbcon = connect_database('navigator_db')
			contents = eval(dbcon.execute(GET_FOLDER_CONTENTS, (list_name, 'shortcut_folder')).fetchone()[0])
		except: contents = []
		return contents

	def currently_used_list(self, list_name):
		default_contents, edited_contents = self.get_main_lists(list_name)
		list_items = edited_contents or default_contents
		return list_items

	def rebuild_database(self):
		dbcon = connect_database('navigator_db')
		dbcon = connect_database('navigator_db')
		for list_name in default_menu_items: self.set_list(list_name, 'default', main_menus[list_name])

	def _get_list_prop(self, list_type):
		return prop_dict[list_type]
	
	def random_movie_lists(self):
		return [dict(i, **{'random': 'true', 'name': 'Random %s' % i['name']}) for i in movie_list if 'random_support' in i]
	
	def random_tvshow_lists(self):
		return [dict(i, **{'random': 'true', 'name': 'Random %s' % i['name']}) for i in tvshow_list if 'random_support' in i]

	def random_trakt_lists(self):
		return [
			{'mode': 'build_movie_list', 'action': 'trakt_collection_lists', 'new_page': 'random', 'name': 'Trakt Movie Collection', 'iconImage': 'movies', 'random': 'true'},
			{'mode': 'build_tvshow_list', 'action': 'trakt_collection_lists', 'new_page': 'random', 'name': 'Trakt TV Show Collection', 'iconImage': 'tv', 'random': 'true'},
			{'mode': 'build_movie_list', 'action': 'trakt_watchlist_lists', 'new_page': 'random', 'name': 'Trakt Movie Watchlist', 'iconImage': 'movies', 'random': 'true'},
			{'mode': 'build_tvshow_list', 'action': 'trakt_watchlist_lists', 'new_page': 'random', 'name': 'Trakt TV Show Watchlist', 'iconImage': 'tv', 'random': 'true'},
			{'mode': 'build_movie_list', 'action': 'trakt_recommendations', 'new_page': 'movies', 'name': 'Recommended Movies', 'iconImage': 'movies', 'random': 'true'},
			{'mode': 'build_tvshow_list', 'action': 'trakt_recommendations', 'new_page': 'shows', 'name': 'Recommended TV Shows', 'iconImage': 'tv', 'random': 'true'},
			{'mode': 'trakt.get_trakt_random_lists', 'list_type': 'my_lists', 'name': 'Trakt My Lists', 'iconImage': 'lists', 'random': 'true'},
			{'mode': 'trakt.get_trakt_random_lists', 'list_type': 'liked_lists', 'name': 'Trakt Liked Lists', 'iconImage': 'lists', 'random': 'true'}
				]

navigator_cache = NavigatorCache()
