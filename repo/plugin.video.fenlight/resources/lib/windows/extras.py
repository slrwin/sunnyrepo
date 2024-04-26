# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from windows.base_window import BaseDialog, window_manager, window_player, ok_dialog
from apis import tmdb_api, imdb_api, omdb_api, trakt_api
from indexers import dialogs, people
from indexers.images import Images
from modules import kodi_utils, settings, watched_status
from modules.sources import Sources
from modules.utils import change_image_resolution, adjust_premiered_date, get_datetime
from modules.meta_lists import networks, movie_genres, tvshow_genres
from modules.metadata import movieset_meta, episodes_meta
from modules.episode_tools import EpisodeTools
# logger = kodi_utils.logger

Thread, get_icon, close_all_dialog = kodi_utils.Thread, kodi_utils.get_icon, kodi_utils.close_all_dialog
backup_cast_thumbnail = get_icon('genre_family')
addon_fanart, empty_poster = kodi_utils.default_addon_fanart, kodi_utils.empty_poster
extras_button_label_values, show_busy_dialog, hide_busy_dialog = kodi_utils.extras_button_label_values, kodi_utils.show_busy_dialog, kodi_utils.hide_busy_dialog
container_update, activate_window, clear_property = kodi_utils.container_update, kodi_utils.activate_window, kodi_utils.clear_property
extras_enable_scrollbars, omdb_api_key, date_offset = settings.extras_enable_scrollbars, settings.omdb_api_key, settings.date_offset
default_all_episodes, extras_enabled_menus, tmdb_api_key = settings.default_all_episodes, settings.extras_enabled_menus, settings.tmdb_api_key
enable_extra_ratings, nextep_method, watched_indicators = settings.extras_enable_extra_ratings, settings.nextep_method, settings.watched_indicators
options_menu_choice, extras_menu_choice, imdb_videos_choice = dialogs.options_menu_choice, dialogs.extras_menu_choice, dialogs.imdb_videos_choice
trakt_manager_choice, random_choice, playback_choice, favorites_choice = dialogs.trakt_manager_choice, dialogs.random_choice, dialogs.playback_choice, dialogs.favorites_choice
get_next_episodes, get_watched_status_movie, watched_info_movie = watched_status.get_next_episodes, watched_status.get_watched_status_movie, watched_status.watched_info_movie
watched_info_episode, get_database, get_next = watched_status.watched_info_episode, watched_status.get_database, watched_status.get_next
get_progress_status_movie, get_bookmarks_movie = watched_status.get_progress_status_movie, watched_status.get_bookmarks_movie
trailer_choice, media_extra_info, genres_choice, random_choice = dialogs.trailer_choice, dialogs.media_extra_info_choice, dialogs.genres_choice, dialogs.random_choice
keywords_choice = dialogs.keywords_choice
person_search, person_data_dialog = people.person_search, people.person_data_dialog
tmdb_movies_year, tmdb_tv_year, tmdb_movies_genres, tmdb_tv_genres = tmdb_api.tmdb_movies_year, tmdb_api.tmdb_tv_year, tmdb_api.tmdb_movies_genres, tmdb_api.tmdb_tv_genres
tmdb_movies_recommendations, tmdb_tv_recommendations, tmdb_company_id = tmdb_api.tmdb_movies_recommendations, tmdb_api.tmdb_tv_recommendations, tmdb_api.tmdb_company_id
tmdb_movies_companies, tmdb_tv_networks = tmdb_api.tmdb_movies_companies, tmdb_api.tmdb_tv_networks
imdb_reviews, imdb_trivia, imdb_blunders = imdb_api.imdb_reviews, imdb_api.imdb_trivia, imdb_api.imdb_blunders
imdb_parentsguide, imdb_videos = imdb_api.imdb_parentsguide, imdb_api.imdb_videos
fetch_ratings_info, trakt_comments = omdb_api.fetch_ratings_info, trakt_api.trakt_comments
tmdb_image_base, count_insert = 'https://image.tmdb.org/t/p/%s%s', 'x%s'
youtube_check = 'plugin.video.youtube'
setting_base, label_base, ratings_icon_base = 'fenlight.extras.%s.button', 'button%s.label', 'fenlight_flags/ratings/%s'
separator = '[B]  •  [/B]'
button_ids = (10, 11, 12, 13, 14, 15, 16, 17, 50)
plot_id, cast_id, recommended_id, reviews_id, comments_id, trivia_id, blunders_id, parentsguide_id = 2000, 2050, 2051, 2052, 2053, 2054, 2055, 2056
videos_id, year_id, genres_id, networks_id, collection_id, media_images_id = 2057, 2058, 2059, 2060, 2061, 2062
items_list_ids = (recommended_id, year_id, genres_id, networks_id, collection_id)
text_list_ids = (reviews_id, trivia_id, blunders_id, parentsguide_id, comments_id)
finished_tvshow = ('', 'Ended', 'Canceled')
parentsguide_icons = {'Sex & Nudity': get_icon('sex_nudity'), 'Violence & Gore': get_icon('genre_war'), 'Profanity': get_icon('bad_language'),
						'Alcohol, Drugs & Smoking': get_icon('drugs_alcohol'), 'Frightening & Intense Scenes': get_icon('genre_horror')}
meta_ratings_values = (('metascore', 1), ('tomatometer', 2), ('tomatousermeter', 3), ('imdb', 4), ('tmdb', 5))
ratings_null = ('', '%')
missing_image_check = ('', None, empty_poster, addon_fanart)
_images = Images().run

class Extras(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, *args)
		self.control_id = None
		self.set_starting_constants(kwargs)
		self.set_properties()
		self.tasks = (self.set_artwork, self.set_infoline1, self.set_infoline2, self.make_ratings, self.make_cast, self.make_recommended, self.make_reviews,
					self.make_comments, self.make_trivia, self.make_blunders, self.make_parentsguide, self.make_videos, self.make_year, self.make_genres,
					self.make_network, self.make_collection, self.make_media_images)

	def onInit(self):
		self.set_home_property('window_loaded', 'true')
		for i in self.tasks: Thread(target=i).start()
		self.set_default_focus()
		if self.starting_position:
			try:
				window_id, focus = self.starting_position
				self.sleep(750)
				self.setFocusId(window_id)
				self.select_item(window_id, focus)
			except: self.set_default_focus()

	def set_default_focus(self):
		try: self.setFocusId(10)
		except: self.close()

	def run(self):
		self.doModal()
		self.clearProperties()
		if self.selected: self.execute_code(self.selected)

	def onClick(self, controlID):
		self.control_id = None
		if controlID in button_ids: return exec('self.%s()' % self.button_action_dict[controlID])
		else: self.control_id = controlID

	def onAction(self, action):
		if action in self.closing_actions: return window_manager(self)
		if action == self.info_action:
			focus_id = self.getFocusId()
			if not focus_id in items_list_ids: return
			show_busy_dialog()
			from modules.metadata import movie_meta, tvshow_meta
			chosen_listitem = self.get_listitem(focus_id)
			function = movie_meta if self.media_type == 'movie' else tvshow_meta
			meta = function('tmdb_id', chosen_listitem.getProperty('tmdb_id'), self.tmdb_api_key, get_datetime())
			hide_busy_dialog()
			self.show_extrainfo(self.media_type, meta, meta.get('poster', empty_poster))
		elif action in self.context_actions:
			focus_id = self.getFocusId()
			if focus_id == cast_id:
				person_name = self.get_listitem(focus_id).getProperty(self.item_action_dict[focus_id])
				return person_search(person_name)
			else: return
		if not self.control_id: return
		if action in self.selection_actions:
			try: chosen_var = self.get_listitem(self.control_id).getProperty(self.item_action_dict[self.control_id])
			except: return
			if not chosen_var: return
			position = self.get_position(self.control_id)
			if self.control_id in items_list_ids:
				self.set_current_params()
				self.new_params = {'mode': 'extras_menu_choice', 'tmdb_id': chosen_var, 'media_type': self.media_type, 'is_external': self.is_external, 'stacked': 'true'}
				return window_manager(self)
			elif self.control_id == cast_id:
				self.set_current_params()
				self.new_params = {'mode': 'person_data_dialog', 'key_id': chosen_var, 'reference_tmdb_id': self.tmdb_id, 'is_external': self.is_external, 'stacked': 'true'}
				return window_manager(self)
			elif self.control_id == videos_id:
				chosen = imdb_videos_choice({'videos': self.get_attribute(self, chosen_var)[position]['videos'], 'poster': self.poster})
				if not chosen: return
				self.set_current_params()
				self.window_player_url = chosen
				return window_player(self)
			elif self.control_id == media_images_id:
				return self.select_item(self.control_id, _images({'mode': 'imageviewer','all_images': self.get_attribute(self, chosen_var), 'current_index': position}))
			elif self.control_id in text_list_ids:
				if self.control_id == parentsguide_id: return self.show_text_media(text=chosen_var)
				else: return self.select_item(self.control_id, self.show_text_media(text=self.get_attribute(self, chosen_var), current_index=position))
			else: return

	def make_ratings(self, win_prop=4000):
		data = self.get_extra_ratings()
		if not data: return
		active_extra_ratings = False
		if self.rating: data['tmdb']['rating'] = self.rating
		for prop, _id in meta_ratings_values:
			rating, icon = data[prop]['rating'], data[prop]['icon']
			if rating in ratings_null: continue
			if prop == 'tmdb' and not active_extra_ratings: continue
			self.setProperty('%s_rating' % prop, 'true'), self.set_label(win_prop + _id, rating), self.set_image(win_prop + 100 + _id, ratings_icon_base % icon)
			active_extra_ratings = True
		if win_prop == 4000 and self.getProperty('tmdb_rating') == 'true': self.set_infoline1(remove_rating=True)

	def make_plot_and_tagline(self):
		self.plot = self.meta_get('tvshow_plot', '') or self.meta_get('plot', '') or ''
		if not self.plot: return
		self.tagline = self.meta_get('tagline') or ''
		if self.tagline: self.plot = '[I]%s[/I][CR][CR]%s' % (self.tagline, self.plot)
		if plot_id in self.enabled_lists: self.setProperty('plot_enabled', 'true')

	def make_cast(self):
		if not cast_id in self.enabled_lists: return
		def builder():
			for item in self.meta_get('cast'):
				try:
					listitem = self.make_listitem()
					thumbnail = item['thumbnail'] or backup_cast_thumbnail
					listitem.setProperty('name', item['name'])
					listitem.setProperty('role', item['role'])
					listitem.setProperty('thumbnail', thumbnail)
					yield listitem
				except: pass
		try:
			item_list = list(builder())
			self.setProperty('cast.number', count_insert % len(item_list))
			self.item_action_dict[cast_id] = 'name'
			self.add_items(cast_id, item_list)
		except: pass

	def make_recommended(self):
		if not recommended_id in self.enabled_lists: return
		try:
			function = tmdb_movies_recommendations if self.media_type == 'movie' else tmdb_tv_recommendations
			data = function(self.tmdb_id, 1)['results']
			item_list = list(self.make_tmdb_listitems(data))
			self.setProperty('recommended.number', count_insert % len(item_list))
			self.item_action_dict[recommended_id] = 'tmdb_id'
			self.add_items(recommended_id, item_list)
		except: pass

	def make_reviews(self):
		if not reviews_id in self.enabled_lists: return
		def builder():
			for item in self.all_reviews:
				try:
					listitem = self.make_listitem()
					listitem.setProperty('text', item)
					listitem.setProperty('content_list', 'all_reviews')
					yield listitem
				except: pass
		try:
			self.all_reviews = imdb_reviews(self.imdb_id)
			item_list = list(builder())
			self.setProperty('imdb_reviews.number', count_insert % len(item_list))
			self.item_action_dict[reviews_id] = 'content_list'
			self.add_items(reviews_id, item_list)
		except: pass

	def make_comments(self):
		if not comments_id in self.enabled_lists: return
		def builder():
			for item in self.all_comments:
				try:
					listitem = self.make_listitem()
					listitem.setProperty('text', item)
					listitem.setProperty('content_list', 'all_comments')
					yield listitem
				except: pass
		try:
			self.all_comments = trakt_comments(self.media_type, self.imdb_id)
			item_list = list(builder())
			self.setProperty('trakt_comments.number', count_insert % len(item_list))
			self.item_action_dict[comments_id] = 'content_list'
			self.add_items(comments_id, item_list)
		except: pass

	def make_trivia(self):
		if not trivia_id in self.enabled_lists: return
		def builder():
			for item in self.all_trivia:
				try:
					listitem = self.make_listitem()
					listitem.setProperty('text', item)
					listitem.setProperty('content_list', 'all_trivia')
					yield listitem
				except: pass
		try:
			self.all_trivia = imdb_trivia(self.imdb_id)
			item_list = list(builder())
			self.setProperty('imdb_trivia.number', count_insert % len(item_list))
			self.item_action_dict[trivia_id] = 'content_list'
			self.add_items(trivia_id, item_list)
		except: pass

	def make_blunders(self):
		if not blunders_id in self.enabled_lists: return
		def builder():
			for item in self.all_blunders:
				try:
					listitem = self.make_listitem()
					listitem.setProperty('text', item)
					listitem.setProperty('content_list', 'all_blunders')
					yield listitem
				except: pass
		try:
			self.all_blunders = imdb_blunders(self.imdb_id)
			item_list = list(builder())
			self.setProperty('imdb_blunders.number', count_insert % len(item_list))
			self.item_action_dict[blunders_id] = 'content_list'
			self.add_items(blunders_id, item_list)
		except: pass

	def make_parentsguide(self):
		if not parentsguide_id in self.enabled_lists: return
		def builder():
			for item in data:
				try:
					listitem = self.make_listitem()
					name = item['title']
					ranking = item['ranking'].upper()
					if ranking == 'NONE': ranking - 'NO RANK'
					if item['content']: ranking += ' (x%02d)' % item['total_count']
					icon = parentsguide_icons[name]
					listitem.setProperty('name', name)
					listitem.setProperty('ranking', ranking)
					listitem.setProperty('thumbnail', icon)
					listitem.setProperty('content', item['content'])
					yield listitem
				except: pass
		try:
			data = imdb_parentsguide(self.imdb_id)
			item_list = list(builder())
			self.setProperty('imdb_parentsguide.number', count_insert % len(item_list))
			self.item_action_dict[parentsguide_id] = 'content'
			self.add_items(parentsguide_id, item_list)
		except: pass

	def make_videos(self):
		if not videos_id in self.enabled_lists: return
		def builder():
			for item in self.all_videos:
				try:
					listitem = self.make_listitem()
					listitem.setProperty('name', item['title'])
					listitem.setProperty('thumbnail', item['poster'])
					listitem.setProperty('content_list', 'all_videos')
					yield listitem
				except: pass
		try:
			self.all_videos = imdb_videos(self.imdb_id)
			item_list = list(builder())
			self.setProperty('imdb_videos.number', count_insert % len(item_list))
			self.item_action_dict[videos_id] = 'content_list'
			self.add_items(videos_id, item_list)
		except: pass

	def make_year(self):
		if not year_id in self.enabled_lists: return
		try:
			function = tmdb_movies_year if self.media_type == 'movie' else tmdb_tv_year
			data = self.remove_current_tmdb_mediaitem(function(self.year, 1)['results'])
			item_list = list(self.make_tmdb_listitems(data))
			self.setProperty('more_from_year.number', count_insert % len(item_list))
			self.item_action_dict[year_id] = 'tmdb_id'
			self.add_items(year_id, item_list)
		except: pass

	def make_genres(self):
		if not genres_id in self.enabled_lists: return
		try:
			function, genre_list = (tmdb_movies_genres, movie_genres) if self.media_type == 'movie' else (tmdb_tv_genres, tvshow_genres)
			genre_list = ','.join([i['id'] for i in genre_list if i['name'] in self.genre])
			data = self.remove_current_tmdb_mediaitem(function(genre_list, 1)['results'])
			item_list = list(self.make_tmdb_listitems(data))
			self.setProperty('more_from_genres.number', count_insert % len(item_list))
			self.item_action_dict[genres_id] = 'tmdb_id'
			self.add_items(genres_id, item_list)
		except: pass

	def make_network(self):
		if not networks_id in self.enabled_lists: return
		try:
			network = self.meta_get('studio')[0]
			network_id = [i['id'] for i in tmdb_company_id(network)['results'] if i['name'] == network][0] \
						if self.media_type == 'movie' else [item['id'] for item in networks if item['name'] == network][0]
			function = tmdb_movies_companies if self.media_type == 'movie' else tmdb_tv_networks
			data = self.remove_current_tmdb_mediaitem(function(network_id, 1)['results'])
			item_list = list(self.make_tmdb_listitems(data))
			self.setProperty('more_from_networks.number', count_insert % len(item_list))
			self.item_action_dict[networks_id] = 'tmdb_id'
			self.add_items(networks_id, item_list)
		except: pass

	def make_collection(self):
		if self.media_type != 'movie': return
		if not collection_id in self.enabled_lists: return
		try: coll_id = self.extra_info_get('collection_id')
		except: return
		if not coll_id: return
		try:
			data = movieset_meta(coll_id, self.tmdb_api_key)
			item_list = list(self.make_tmdb_listitems(sorted(data['parts'], key=lambda k: k['release_date'] or '2050')))
			self.setProperty('more_from_collection.name', data['title'])
			self.setProperty('more_from_collection.overview', data['plot'] or data['title'])
			self.setProperty('more_from_collection.poster', data['poster'] or empty_poster)
			self.setProperty('more_from_collection.number', count_insert % len(item_list))
			self.item_action_dict[collection_id] = 'tmdb_id'
			self.add_items(collection_id, item_list)
		except: pass

	def make_media_images(self):
		if not media_images_id in self.enabled_lists: return
		def builder():
			for item in all_images:
				try:
					listitem = self.make_listitem()
					listitem.setProperty('name', item[1])
					listitem.setProperty('thumbnail', item[0])
					listitem.setProperty('content_list', 'all_media_images')
					yield listitem
				except: pass
		try:
			all_images = [(self.get_attribute(self, i), '%s %s' % (self.title, i.capitalize())) for i in ('poster', 'fanart', 'landscape', 'clearlogo')]
			all_images = [i for i in all_images if not i[0] in missing_image_check]
			if not all_images: return
			self.all_media_images = [(change_image_resolution(i[0], 'original'), i[1]) for i in all_images]
			item_list = list(builder())
			self.setProperty('media_images.number', count_insert % len(item_list))
			self.item_action_dict[media_images_id] = 'content_list'
			self.add_items(media_images_id, item_list)
		except: pass

	def get_extra_ratings(self):
		if not self.display_extra_ratings: return None
		data = self.meta_get('extra_ratings', None) or fetch_ratings_info(self.meta, self.omdb_api)
		return data

	def get_release_year(self, release_data):
		try:
			if release_data in ('', None): release_data = 'N/A'
			else: release_data = release_data.split('-')[0]
		except: pass
		return release_data

	def get_progress(self, percent_watched):
		return '%s%% Watched' % percent_watched

	def get_finish(self, percent_watched):
		finish_str = 'No Finish Time'
		if self.duration_data:
			label = 'Finish Rewatching' if percent_watched == '100' else 'Finish Watching'
			kodi_clock = self.get_infolabel('System.Time')
			if any(i in kodi_clock for i in ('AM', 'PM')): _format = '%I:%M %p'
			else: _format = '%H:%M'
			if percent_watched in ('0', '100'): remaining_time = self.duration_data
			else: remaining_time = ((100 - int(percent_watched))/100) * self.duration_data
			current_time = datetime.now()
			finish_time = current_time + timedelta(minutes=remaining_time)
			finished = finish_time.strftime(_format)
			finish_str = '%s: %s' % (label, finished)
		return finish_str

	def get_duration(self):
		time_str = ''
		if self.duration_data:
			hour, minute = divmod(self.duration_data, 60)
			if hour: time_str += '%dh' % hour
			if minute: time_str += '%s%sm' % (' ' if hour else '', '%d' % minute if minute < 10 else '%02d' % minute)
		return time_str

	def get_last_aired(self):
		if self.extra_info_get('last_episode_to_air', False):
			last_ep = self.extra_info_get('last_episode_to_air')
			last_aired = 'S%.2dE%.2d' % (last_ep['season_number'], last_ep['episode_number'])
		else: return ''
		return 'Last Aired: %s' % last_aired

	def get_next_aired(self):
		if self.status in finished_tvshow: return ''
		if self.extra_info_get('next_episode_to_air', False):
			next_ep = self.extra_info_get('next_episode_to_air')
			next_aired = 'S%.2dE%.2d' % (next_ep['season_number'], next_ep['episode_number'])
		else: return ''
		return 'Next Aired: %s' % next_aired

	def get_next_episode(self):
		self.nextep_season, self.nextep_episode = None, None
		value, curr_season_data, episode_date = '', [], None
		try:
			nextep_content = nextep_method()
			ep_list = get_next_episodes(nextep_content)
			ep_data = next((i for i in ep_list if i['media_ids']['tmdb'] == self.tmdb_id), None)
			orig_season, orig_episode = ep_data.get('season'), ep_data.get('episode')
			season_data = self.meta_get('season_data')
			watched_info = watched_info_episode(self.tmdb_id, get_database(watched_indicators()))
			nextep_season, nextep_episode = get_next(orig_season, orig_episode, watched_info, season_data, nextep_content)
			if not nextep_season: return
			episodes_data = episodes_meta(nextep_season, self.meta)
			item = next((i for i in episodes_data if i['episode'] == orig_episode), None)
			item_get = item.get
			episode_date, premiered = adjust_premiered_date(item_get('premiered'), date_offset())
			if episode_date and get_datetime() >= episode_date:
				self.nextep_season, self.nextep_episode = nextep_season, nextep_episode
				value = 'Next Episode: S%.2dE%.2d' % (self.nextep_season, self.nextep_episode)
		except: pass
		return value

	def make_tvshow_browse_params(self):
		total_seasons = self.meta_get('total_seasons')
		all_episodes = default_all_episodes()
		show_all_episodes = True if all_episodes in (1, 2) else False
		if show_all_episodes:
			if all_episodes == 1 and total_seasons > 1: url_params = {'mode': 'build_season_list', 'tmdb_id': self.tmdb_id}
			else: url_params = {'mode': 'build_episode_list', 'tmdb_id': self.tmdb_id, 'season': 'all'}
		else: url_params = {'mode': 'build_season_list', 'tmdb_id': self.tmdb_id}
		return url_params

	def remove_current_tmdb_mediaitem(self, data):
		return [i for i in data if int(i['id']) != self.tmdb_id]

	def make_tmdb_listitems(self, data):
		name_key = 'title' if self.media_type == 'movie' else 'name'
		release_key = 'release_date' if self.media_type == 'movie' else 'first_air_date'
		for item in data:
			try:
				listitem = self.make_listitem()
				poster_path = item['poster_path']
				if poster_path: thumbnail = tmdb_image_base % ('w300', poster_path)
				else: thumbnail = empty_poster
				year = self.get_release_year(item[release_key])
				listitem.setProperty('name', item[name_key])
				listitem.setProperty('release_date', year)
				listitem.setProperty('vote_average', '%.1f' % item['vote_average'])
				listitem.setProperty('thumbnail', thumbnail)
				listitem.setProperty('tmdb_id', str(item['id']))
				yield listitem
			except: pass

	def set_artwork(self):
		self.set_image(202, self.fanart)
		if self.clearlogo: self.set_image(201, self.clearlogo)
		else: self.setProperty('clearlogo', 'false')
		self.set_image(200, self.poster)

	def show_text_media(self, text, poster=None, current_index=None):
		return self.open_window(('windows.extras', 'ShowTextMedia'), 'textviewer_media.xml', text=text, poster=poster or self.poster, current_index=current_index)

	def tvshow_browse(self):
		self.close_all()
		url_params = self.make_tvshow_browse_params()
		self.selected = self.folder_runner(url_params)
		self.close()

	def movies_play(self):
		url_params = {'mode': 'playback.media', 'media_type': 'movie', 'tmdb_id': self.tmdb_id}
		Sources().playback_prep(url_params)

	def show_plot(self):
		return self.show_text_media(text=self.plot)

	def show_trailers(self):
		if not self.youtube_installed_check(): return self.notification('Youtube Plugin needed for playback')
		chosen = trailer_choice({'media_type': self.media_type, 'poster': self.poster, 'tmdb_id': self.tmdb_id,
								'trailer_url': self.meta_get('trailer'), 'all_trailers': self.meta_get('all_trailers', [])})
		if not chosen: return ok_dialog()
		elif chosen == 'canceled': return
		self.set_current_params(set_starting_position=False)
		self.window_player_url = chosen
		return window_player(self)

	def show_images(self):
		return _images({'mode': 'imdb_image_results', 'imdb_id': self.imdb_id, 'media_title': self.rootname, 'page_no': 1, 'rolling_count_list': [0]})

	def show_media_images(self):
		all_images = [(self.get_attribute(self, i), '%s %s' % (self.title, i)) for i in ('poster', 'fanart', 'landscape', 'clearlogo')]
		all_images = [i for i in all_images if not i[0] in missing_image_check]
		if not all_images: return self.notification('No Media Images to Display')
		all_images = [(i[0], change_image_resolution(i[0], 'original'), i[1]) for i in all_images]
		return _images({'mode': 'tmdb_media_image_results', 'all_images': all_images})

	def show_extrainfo(self, media_type=None, meta=None, poster=None):
		text = media_extra_info({'media_type': media_type or self.media_type, 'meta': meta or self.meta})
		return self.show_text_media(text=text, poster=poster)

	def show_genres(self):
		if not self.genre: return
		genre_id = genres_choice({'genres_list': movie_genres if self.media_type == 'movie' else tvshow_genres, 'genres': self.genre, 'poster': self.poster})
		if not genre_id: return
		self.close_all()
		mode, action = ('build_movie_list', 'tmdb_movies_genres') if self.media_type == 'movie' else ('build_tvshow_list', 'tmdb_tv_genres')
		self.selected = self.folder_runner({'mode': mode, 'action': action, 'key_id': genre_id})
		self.close()

	def show_keywords(self):
		keyword_id = keywords_choice({'media_type': self.media_type, 'tmdb_id': self.tmdb_id, 'poster': self.poster})
		if not keyword_id: return
		self.close_all()
		mode, action = ('build_movie_list', 'tmdb_movie_keyword_results') if self.media_type == 'movie' else ('build_tvshow_list', 'tmdb_tv_keyword_results')
		self.selected = self.folder_runner({'mode': mode, 'action': action, 'key_id': keyword_id})
		self.close()

	def play_nextep(self):
		if self.nextep_season == None: return ok_dialog(text='No Episodes Available')
		url_params = {'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': self.tmdb_id, 'season': self.nextep_season,
					'episode': self.nextep_episode}
		Sources().playback_prep(url_params)

	def play_random_episode(self):
		function = random_choice({'meta': self.meta, 'poster': self.poster, 'return_choice': 'true'})
		if not function: return
		exec('EpisodeTools(self.meta).%s()' % function)
		self.close()

	def show_director(self):
		try: director = self.meta_get('director', None)[0]
		except: return self.notification('No Director Information Available')
		if not director: return
		self.set_current_params(set_starting_position=False)
		self.new_params = {'mode': 'person_data_dialog', 'key_id': director, 'is_external': self.is_external, 'stacked': 'true'}
		window_manager(self)

	def show_options(self):
		params = {'content': self.options_media_type, 'tmdb_id': str(self.tmdb_id), 'poster': self.poster, 'is_external': self.is_external, 'from_extras': 'true'}
		return options_menu_choice(params, self.meta)

	def show_recommended(self):
		mode, action = ('build_movie_list', 'tmdb_movies_recommendations') if self.media_type == 'movie' else ('build_tvshow_list', 'tmdb_tv_recommendations')
		self.selected = self.folder_runner({'mode': mode, 'action': action, 'key_id': self.tmdb_id, 'name': 'Recommended based on %s' % self.title})
		self.close()

	def show_trakt_manager(self):
		return trakt_manager_choice({'tmdb_id': self.tmdb_id, 'imdb_id': self.imdb_id, 'tvdb_id': self.meta_get('tvdb_id', 'None'),
									'media_type': self.media_type, 'icon': self.poster})

	def show_favorites_manager(self):
		return favorites_choice({'media_type': self.media_type, 'tmdb_id': str(self.tmdb_id), 'title': self.title, 'refresh': 'false'})

	def playback_choice(self):
		params = {'media_type': self.media_type, 'poster': self.poster, 'meta': self.meta, 'season': None, 'episode': None}
		playback_choice(params)

	def close_all(self):
		clear_property('fenlight.window_stack')
		close_all_dialog()

	def assign_buttons(self):
		setting_id_base = setting_base % self.media_type
		for item in button_ids[:-1]:
			button_action = self.get_setting(setting_id_base + str(item))
			self.setProperty(label_base % item, extras_button_label_values[self.media_type][button_action])
			self.button_action_dict[item] = button_action
		self.button_action_dict[50] = 'show_plot'

	def set_current_params(self, set_starting_position=True):
		self.current_params = {'mode': 'extras_menu_choice', 'tmdb_id': self.tmdb_id, 'media_type': self.media_type, 'is_external': self.is_external}
		if set_starting_position: self.current_params['starting_position'] = [self.control_id, self.get_position(self.control_id)]

	def set_starting_constants(self, kwargs):
		self.meta = kwargs['meta']
		self.meta_get = self.meta.get
		self.media_type, self.options_media_type = self.meta_get('mediatype'), kwargs['options_media_type']
		self.starting_position = kwargs.get('starting_position', None)
		self.is_external = kwargs['is_external'].lower()
		self.item_action_dict, self.button_action_dict = {}, {}
		self.selected = None
		self.current_params, self.new_params = {}, {}
		self.extra_info = self.meta_get('extra_info')
		self.extra_info_get = self.extra_info.get
		self.tmdb_id, self.imdb_id = self.meta_get('tmdb_id'), self.meta_get('imdb_id')
		self.folder_runner = activate_window if self.is_external == 'true' else container_update
		self.enabled_lists, self.enable_scrollbars = extras_enabled_menus(), extras_enable_scrollbars()
		self.tmdb_api_key, self.omdb_api = tmdb_api_key(), omdb_api_key()
		self.display_extra_ratings = self.imdb_id and self.omdb_api not in ('empty_setting', '') and enable_extra_ratings()
		self.title, self.year, self.rootname = self.meta_get('title'), str(self.meta_get('year')), self.meta_get('rootname')
		self.poster = self.meta_get('poster') or empty_poster
		self.fanart = self.meta_get('fanart') or addon_fanart
		self.clearlogo = self.meta_get('clearlogo') or ''
		self.landscape = self.meta_get('landscape') or ''
		self.rating = str(round(self.meta_get('rating'), 1)) if self.meta_get('rating') not in (0, 0.0, None) else None
		self.mpaa, self.genre, self.network = self.meta_get('mpaa'), self.meta_get('genre'), self.meta_get('studio') or ''
		self.status, self.duration_data = self.extra_info_get('status', '').replace(' Series', ''), int(float(self.meta_get('duration'))/60)
		self.status_infoline_value = self.make_status_infoline()
		self.make_plot_and_tagline()

	def set_properties(self):
		self.assign_buttons()
		self.setProperty('media_type', self.media_type), self.setProperty('title', self.title), self.setProperty('year', self.year), self.setProperty('plot', self.plot)
		self.setProperty('genre', ', '.join(self.genre)), self.setProperty('network', ', '.join(self.network)), self.setProperty('enable_scrollbars', self.enable_scrollbars)

	def make_status_infoline(self):
		status_str = self.status
		if self.media_type == 'tvshow' and self.status == 'Returning':
			try: next_aired_date = self.extra_info_get('next_episode_to_air')['air_date']
			except: next_aired_date = None
			if next_aired_date: status_str = '%s %s' % (self.status, adjust_premiered_date(next_aired_date, date_offset())[0].strftime('%d %B %Y'))
		return status_str

	def set_infoline1(self, remove_rating=False):
		self.set_label(2001, separator.join([i for i in (self.year, None if remove_rating else self.rating, self.mpaa, self.get_duration(), self.status_infoline_value) if i]))

	def set_infoline2(self):
		if self.media_type == 'movie':
			percent_watched = get_progress_status_movie(get_bookmarks_movie(), self.tmdb_id)
			if not percent_watched:
				try: percent_watched = '100' if get_watched_status_movie(watched_info_movie(), str(self.tmdb_id)) == 1 else '0'
				except: percent_watched = '0'
				if not percent_watched: percent_watched = 0
			line2 = separator.join([self.get_progress(percent_watched), self.get_finish(percent_watched)])
		else: line2 = separator.join([i for i in (self.get_next_episode(), self.get_last_aired(), self.get_next_aired()) if i])
		self.set_label(3001, line2)

	def youtube_installed_check(self):
		if not self.addon_installed(youtube_check): return False
		if not self.addon_enabled(youtube_check): return False
		return True

class ShowTextMedia(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, *args)
		self.text = kwargs.get('text')
		self.position = kwargs.get('current_index', None)
		self.text_is_list = isinstance(self.text, list)
		self.len_text = len(self.text) if self.text_is_list else None
		self.window_id = 2061
		self.setProperty('poster', kwargs.get('poster'))

	def run(self):
		self.doModal()
		return self.position

	def onInit(self):
		self.update_text()
		self.setFocusId(self.window_id)	

	def onAction(self, action):
		if action in self.closing_actions: return self.close()
		if self.text_is_list:
			if action == self.left_action: return self.update_text('previous')
			if action == self.right_action: return self.update_text('next')

	def update_text(self, direction=None):
		if direction == 'previous': self.position = self.position - 1 if self.position > 0 else self.len_text - 1
		elif direction == 'next': self.position = 0 if self.position == self.len_text - 1 else self.position + 1
		self.set_text(2001, self.text[self.position] if self.text_is_list else self.text)
		if self.text_is_list:
			if self.position == 0: self.setProperty('previous_display', 'false')
			else: self.setProperty('previous_display', 'true')
			if self.position == self.len_text - 1: self.setProperty('next_display', 'false')
			else: self.setProperty('next_display', 'true')
		else: self.setProperty('previous_display', 'false'), self.setProperty('next_display', 'false')
