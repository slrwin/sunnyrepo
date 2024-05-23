# -*- coding: utf-8 -*-
from indexers.movies import Movies
from indexers.tvshows import TVShows
from modules import meta_lists
from modules import kodi_utils
from modules.utils import manual_function_import, make_thread_list
# logger = kodi_utils.logger

external, home, end_directory, set_property, sys, random = kodi_utils.external, kodi_utils.home, kodi_utils.end_directory, kodi_utils.set_property, kodi_utils.sys, kodi_utils.random
add_items, set_content, set_category, set_view_mode = kodi_utils.add_items, kodi_utils.set_content, kodi_utils.set_category, kodi_utils.set_view_mode

random_valid_type_check = {'build_movie_list': 'movie', 'build_tvshow_list': 'tvshow', 'build_season_list': 'season', 'build_episode_list': 'episode',
'build_in_progress_episode': 'single_episode', 'build_recently_watched_episode': 'single_episode', 'build_next_episode': 'single_episode',
'build_my_calendar': 'single_episode', 'build_trakt_lists': 'trakt_list'}
random_episodes_check = {'build_in_progress_episode': 'episode.progress', 'build_recently_watched_episode': 'episode.recently_watched',
'build_next_episode': 'episode.next', 'build_my_calendar': 'episode.trakt'}
movie_main = ('tmdb_movies_popular', 'tmdb_movies_popular_today','tmdb_movies_blockbusters','tmdb_movies_in_theaters', 'tmdb_movies_upcoming', 'tmdb_movies_latest_releases',
'tmdb_movies_premieres', 'tmdb_movies_oscar_winners')
movie_trakt_main = ('trakt_movies_trending', 'trakt_movies_trending_recent', 'trakt_movies_most_watched', 'trakt_movies_most_favorited',
'trakt_movies_top10_boxoffice', 'trakt_recommendations')
movie_trakt_personal = ('trakt_collection_lists', 'trakt_watchlist_lists')
movie_meta_list_dict = {'tmdb_movies_languages': meta_lists.languages, 'tmdb_movies_providers': meta_lists.watch_providers_movies, 'tmdb_movies_year': meta_lists.years_movies,
'tmdb_movies_decade': meta_lists.decades_movies, 'tmdb_movies_certifications': meta_lists.movie_certifications, 'tmdb_movies_genres': meta_lists.movie_genres}
tvshow_main = ('tmdb_tv_popular', 'tmdb_tv_popular_today', 'tmdb_tv_premieres', 'tmdb_tv_airing_today','tmdb_tv_on_the_air','tmdb_tv_upcoming')
tvshow_trakt_main = ('trakt_tv_trending', 'trakt_tv_trending_recent', 'trakt_recommendations', 'trakt_tv_most_watched', 'trakt_tv_most_favorited')
tvshow_trakt_personal = ('trakt_collection_lists', 'trakt_watchlist_lists')
tvshow_meta_list_dict = {'tmdb_tv_languages': meta_lists.languages, 'tmdb_tv_networks': meta_lists.networks, 'tmdb_tv_providers': meta_lists.watch_providers_tvshows,
'tmdb_tv_year': meta_lists.years_tvshows, 'tmdb_tv_decade': meta_lists.decades_tvshows, 'tmdb_tv_genres': meta_lists.tvshow_genres,
'trakt_tv_certifications': meta_lists.tvshow_certifications}

class RandomLists():
	def __init__(self, params):
		self.handle = int(sys.argv[1])
		self.params = params
		self.params_get = params.get
		self.mode = self.params_get('mode').replace('random.', '')
		self.action = self.params_get('action')
		self.menu_type = self.params_get('menu_type', None) or ('movie' if 'movie' in self.mode else 'tvshow')
		self.base_list_name = self.params_get('name')
		self.params.update({'mode': self.mode, 'action': self.action, 'menu_type': self.menu_type, 'base_list_name': self.base_list_name})
		self.is_external, self.is_home = external(), home()
		self.folder_name = self.params_get('folder_name', None)
		if self.menu_type == 'movie': self.function, self.view_mode, self.content_type = Movies, 'view.movies', 'movies'
		else: self.function, self.view_mode, self.content_type = TVShows, 'view.tvshows', 'tvshows'
		self.category_name, self.list_items, self.random_results = '', [], []

	def set_property(self):
		if self.is_external: 
			if self.folder_name: set_property('fenlight.%s' % self.folder_name, self.category_name)
			else: set_property('fenlight.%s' % self.base_list_name, self.category_name)

	def get_function(self):
		return manual_function_import('apis.%s_api' % self.action.split('_')[0], self.action)

	def make_directory(self):
		add_items(self.handle, self.list_items)
		set_content(self.handle, self.content_type)
		set_category(self.handle, self.category_name)
		end_directory(self.handle, cacheToDisc=False if self.is_external else True)
		if not self.is_external: set_view_mode(self.view_mode, self.content_type, self.is_external)

	def run_random(self):
		if self.mode == 'build_trakt_lists': return self.random_trakt_lists()
		if self.action in movie_main: return self.random_main()
		if self.action in movie_trakt_main: return self.random_trakt_main()
		if self.action in movie_trakt_personal: return self.random_trakt_personal_lists()
		if self.action in tvshow_main: return self.random_main()
		if self.action in tvshow_trakt_main: return self.random_trakt_main()
		if self.action in tvshow_trakt_personal: return self.function(self.params).fetch_list()
		return self.random_special_main()

	def random_main(self):
		list_function = self.get_function()
		threads = list(make_thread_list(lambda x: self.random_results.extend(list_function(x)['results']), range(1, 6)))
		[i.join() for i in threads]
		

		random_list = random.sample(self.random_results, min(len(self.random_results), 20))
		

		self.params['list'] = [i['id'] for i in random_list]
		self.list_items = self.function(self.params).worker()
		self.category_name = self.params_get('category_name', None) or self.base_list_name or ''
		self.make_directory()

	def random_trakt_main(self):
		function_key, list_key = ('movies', 'movie') if self.menu_type == 'movie' else ('shows', 'show')
		list_function = self.get_function()
		threads = list(make_thread_list(lambda x: self.random_results.extend(list_function(x)), [function_key,] if self.action == 'trakt_recommendations' else range(1, 6)))
		[i.join() for i in threads]
		

		random_list = random.sample(self.random_results, min(len(self.random_results), 20))
		

		try: self.params['list'] = [i[list_key]['ids'] for i in random_list]
		except: self.params['list'] = [i['ids'] for i in random_list]
		self.params['id_type'] = 'trakt_dict'
		self.list_items = self.function(self.params).worker()
		self.category_name = self.params_get('category_name', None) or self.base_list_name or ''
		self.make_directory()

	def random_special_main(self):
		list_function = self.get_function()
		choice_list = movie_meta_list_dict if self.menu_type == 'movie' else tvshow_meta_list_dict
		info = random.choice(choice_list[self.action])
		list_name = self.action.split('_')[-1]
		if not list_name.endswith('s'): list_name += 's'
		if self.action == 'trakt_tv_certifications': threads = list(make_thread_list(lambda x: self.random_results.extend(list_function(info['id'], x)), range(1, 6)))			
		else: threads = list(make_thread_list(lambda x: self.random_results.extend(list_function(info['id'], x)['results']), range(1, 6)))
		[i.join() for i in threads]
		

		random_list = random.sample(self.random_results, min(len(self.random_results), 20))
			

		if self.action == 'trakt_tv_certifications': self.params.update({'id_type': 'trakt_dict', 'list': [i['show']['ids'] for i in random_list]})
		else: self.params['list'] = [i['id'] for i in random_list]
		self.list_items = self.function(self.params).worker()
		self.category_name = info['name']
		self.set_property()
		self.make_directory()

	def random_trakt_lists(self):
		from apis.trakt_api import trakt_get_lists
		from indexers.trakt_lists import build_trakt_list
		list_type = self.params.get('list_type')
		list_type_name = 'Trakt My Lists' if list_type == 'my_lists' else 'Trakt Liked Lists'
		self.random_results = trakt_get_lists(list_type)
		

		random_list = random.choice(self.random_results)
		

		if list_type == 'liked_lists': random_list = random_list['list']
		list_name = random_list['name']
		url_params = {'user': random_list['user']['ids']['slug'], 'slug': random_list['ids']['slug'], 'list_type': list_type, 'base_list_name':list_type_name,
					'list_name': list_name, 'random': 'true'}
		self.category_name = list_name
		self.set_property()
		self.list_items = build_trakt_list(url_params)
		self.make_directory()

	def random_trakt_personal_lists(self):
		self.category_name = self.base_list_name
		self.set_property()
		return self.function(self.params).fetch_list()

def random_shortcut_folders(folder_name, random_results):
	random_results = [i for i in random_results if i.get('mode').replace('random.', '') in random_valid_type_check]
	if not random_results: return end_directory(int(sys.argv[1]))
	

	if len(random_results) > 1: random_list = random.choice(random_results)
	else: random_list = random_results[0]
	

	random_list.update({'folder_name': folder_name, 'mode': random_list['mode'].replace('random.', '')})
	list_name = random_list.get('list_name', None) or random_list.get('name', None) or 'Random'
	if random_list.get('random')== 'true': return RandomLists(random_list).run_random()
	menu_type = random_valid_type_check[random_list['mode']]
	if external(): set_property('fenlight.%s' % folder_name, list_name)
	if menu_type == 'movie':
		return Movies(random_list).fetch_list()
	if menu_type == 'tvshow':
		return TVShows(random_list).fetch_list()
	if menu_type == 'season':
		from indexers.seasons import build_season_list
		return build_season_list(random_list)
	if menu_type == 'episode':
		from indexers.episodes import build_episode_list
		return build_episode_list(random_list)
	if menu_type == 'single_episode':
		from indexers.episodes import build_single_episode
		return build_single_episode(random_episodes_check[random_list['mode']], random_list)
	if menu_type == 'trakt_list':
		from indexers.trakt_lists import build_trakt_list
		return build_trakt_list(random_list)
	return end_directory(int(sys.argv[1]))
