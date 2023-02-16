# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
from windows import BaseDialog
from apis import tmdb_api, imdb_api
from indexers import dialogs, people
from indexers.images import Images
from modules import kodi_utils, watched_status, settings
from modules.sources import Sources
from modules.downloader import runner
from modules.utils import change_image_resolution, adjust_premiered_date, get_datetime
from modules.meta_lists import networks
from modules.metadata import movieset_meta, episodes_meta
from modules.episode_tools import EpisodeTools
logger = kodi_utils.logger

json, Thread, get_icon, close_all_dialog, ok_dialog = kodi_utils.json, kodi_utils.Thread, kodi_utils.get_icon, kodi_utils.close_all_dialog, kodi_utils.ok_dialog
addon_icon, ls, get_icon, backup_cast_thumbnail = kodi_utils.addon_icon, kodi_utils.local_string, kodi_utils.get_icon, get_icon('genre_family')
fetch_kodi_imagecache, addon_fanart, empty_poster = kodi_utils.fetch_kodi_imagecache, kodi_utils.addon_fanart, kodi_utils.empty_poster
extras_button_label_values = kodi_utils.extras_button_label_values
default_all_episodes, metadata_user_info, extras_enabled_menus = settings.default_all_episodes, settings.metadata_user_info, settings.extras_enabled_menus
extras_enable_scrollbars, extras_enable_animation, get_resolution = settings.extras_enable_scrollbars, settings.extras_enable_animation, settings.get_resolution
watched_indicators, get_art_provider = settings.watched_indicators, settings.get_art_provider
options_menu_choice, extras_menu_choice, imdb_videos_choice = dialogs.options_menu_choice, dialogs.extras_menu_choice, dialogs.imdb_videos_choice
get_progress_percent, get_bookmarks, get_watched_info_movie = watched_status.get_progress_percent, watched_status.get_bookmarks, watched_status.get_watched_info_movie
trakt_manager_choice, random_choice, playback_choice, favorites_choice = dialogs.trakt_manager_choice, dialogs.random_choice, dialogs.playback_choice, dialogs.favorites_choice
get_watched_status_movie, get_watched_info_tv, get_next_episodes = watched_status.get_watched_status_movie, watched_status.get_watched_info_tv, watched_status.get_next_episodes
trailer_choice, imdb_keywords_choice, media_extra_info, genres_choice = dialogs.trailer_choice, dialogs.imdb_keywords_choice, dialogs.media_extra_info_choice, dialogs.genres_choice
person_search, person_data_dialog = people.person_search, people.person_data_dialog
tmdb_movies_year, tmdb_tv_year, tmdb_movies_genres, tmdb_tv_genres = tmdb_api.tmdb_movies_year, tmdb_api.tmdb_tv_year, tmdb_api.tmdb_movies_genres, tmdb_api.tmdb_tv_genres
tmdb_movies_recommendations, tmdb_tv_recommendations, tmdb_company_id = tmdb_api.tmdb_movies_recommendations, tmdb_api.tmdb_tv_recommendations, tmdb_api.tmdb_company_id
tmdb_movies_networks, tmdb_tv_networks = tmdb_api.tmdb_movies_networks, tmdb_api.tmdb_tv_networks
imdb_reviews, imdb_trivia, imdb_blunders = imdb_api.imdb_reviews, imdb_api.imdb_trivia, imdb_api.imdb_blunders
imdb_parentsguide, imdb_videos = imdb_api.imdb_parentsguide, imdb_api.imdb_videos
tmdb_image_base, count_insert = 'https://image.tmdb.org/t/p/%s%s', '%02d'
setting_base, label_base = 'extras.%s.button', 'button%s.label'
button_ids = (10, 11, 12, 13, 14, 15, 16, 17, 50)
cast_id, recommended_id, reviews_id, trivia_id, blunders_id, parentsguide_id = 2050, 2051, 2052, 2053, 2054, 2055
videos_id, posters_id, fanarts_id, year_id, genres_id, networks_id, collection_id = 2056, 2057, 2058, 2059, 2060, 2061, 2062
tmdb_list_ids = (recommended_id, year_id, genres_id, networks_id, collection_id)
imdb_list_ids = (reviews_id, trivia_id, blunders_id, parentsguide_id)
art_ids = (posters_id, fanarts_id)
finished_tvshow = ('', 'Ended', 'Canceled')
parentsguide_levels = {'mild': ls(32996), 'moderate': ls(32997), 'severe': ls(32998), 'none': ls(33070)}
parentsguide_inputs = {'Sex & Nudity': (ls(32990), get_icon('sex_nudity')), 'Violence & Gore': (ls(32991), get_icon('genre_war')),
						'Profanity': (ls(32992),get_icon('bad_language')), 'Alcohol, Drugs & Smoking': (ls(32993), get_icon('drugs_alcohol')),
						'Frightening & Intense Scenes': (ls(32994), get_icon('genre_horror'))}
_images = Images()

class Extras(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.control_id = None
		self.set_starting_constants(kwargs)
		self.set_properties()
		self.tasks = (self.set_poster, self.make_cast, self.make_recommended, self.make_reviews, self.make_trivia, self.make_blunders, self.make_parentsguide,
					self.make_videos, self.make_year, self.make_genres, self.make_network, self.make_posters, self.make_fanart, self.make_collection)

	def onInit(self):
		for i in self.tasks: Thread(target=i).start()
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
		if action in self.closing_actions: return self.close()
		if action == self.info_action: self.close()
		if action in self.context_actions:
			focus_id = self.getFocusId()
			if focus_id in (posters_id, fanarts_id):
				chosen_listitem = self.get_listitem(focus_id)
				image = chosen_listitem.getProperty('thumbnail')
				params = {'action': 'image', 'name': '%s %s' % (self.rootname, chosen_listitem.getProperty('name')), 'thumb_url': image, 'media_type': 'image',
						'image_url': change_image_resolution(image, 'original' if 'image.tmdb' in image else '/fanart/'), 'image': addon_icon}
				return runner(params)
			elif focus_id == cast_id:
				person_name = self.get_listitem(focus_id).getProperty(self.item_action_dict[focus_id])
				return person_search(person_name, window_xml='media_select.xml')
			else: return
		if not self.control_id: return
		if action in self.selection_actions:
			try: chosen_var = self.get_listitem(self.control_id).getProperty(self.item_action_dict[self.control_id])
			except: return
			if self.control_id in tmdb_list_ids:
				params = {'tmdb_id': chosen_var, 'media_type': self.media_type, 'is_widget': self.is_widget}
				return extras_menu_choice(params)
			elif self.control_id == cast_id:
				return person_data_dialog({'query': chosen_var, 'reference_tmdb_id': self.tmdb_id, 'is_widget': self.is_widget})
			elif self.control_id == videos_id:
				chosen = imdb_videos_choice(self.get_attribute(self, chosen_var)[self.get_position(self.control_id)]['videos'], self.poster)
				if not chosen: return
				self.open_window(('windows.videoplayer', 'VideoPlayer'), 'videoplayer.xml', meta=self.meta, video=chosen)
			elif self.control_id in imdb_list_ids:
				if self.control_id == parentsguide_id:
					if not chosen_var: return
					self.show_text_media(chosen_var)
				else:
					end_index = self.show_text_media_list(chosen_var)
					self.getControl(self.control_id).selectItem(end_index)
			elif self.control_id in art_ids:
				end_index = _images.run({'mode': 'slideshow_image', 'all_images': self.get_attribute(self, chosen_var), 'current_index': self.get_position(self.control_id)})
				self.getControl(self.control_id).selectItem(end_index)
			else: return

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
					name = parentsguide_inputs[item['title']][0]
					ranking = parentsguide_levels[item['ranking'].lower()].upper()
					if item['content']: ranking += ' (x%02d)' % item['total_count']
					icon = parentsguide_inputs[item['title']][1]
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

	def make_posters(self):
		self.make_artwork('poster')

	def make_fanart(self):
		self.make_artwork('fanart')

	def make_artwork(self, image_type):
		if image_type == 'poster' and not posters_id in self.enabled_lists: return
		elif not fanarts_id in self.enabled_lists: return
		def builder():
			for count, item in enumerate(data, 1):
				try:
					listitem = self.make_listitem()
					thumbnail = change_image_resolution(item[0], 'w300' if 'image.tmdb' in item[0] else '/preview/')
					listitem.setProperty('name', '%02d. %s' % (count, item[1]))
					listitem.setProperty('thumbnail', thumbnail)
					listitem.setProperty('all_images', art_list_id)
					yield listitem
				except: pass
		try:
			dbtype = 'movie' if self.media_type == 'movie' else 'tv'
			all_images = self.meta_get('images')[image_type]
			if not self.meta_user_info['extra_fanart_enabled']: all_images = [i for i in all_images if 'image.tmdb' in i]
			data = [(change_image_resolution(i, 'original' if 'image.tmdb' in i else '/fanart/'), self.title) for i in all_images]
			if image_type == 'poster': _id, art_list_id, self.tmdb_posters, used_image, default_image = posters_id, 'tmdb_posters', data, self.poster, empty_poster
			else: _id, art_list_id, self.tmdb_fanarts, used_image, default_image = fanarts_id, 'tmdb_fanarts', data, self.fanart, addon_fanart
			item_list = list(builder())
			self.setProperty('tmdb_artwork.%s.number' % image_type, count_insert % len(item_list))
			self.item_action_dict[_id] = 'all_images'
			self.add_items(_id, item_list)
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
			function = tmdb_movies_genres if self.media_type == 'movie' else tmdb_tv_genres
			genre_dict = genres_choice(self.media_type, self.genre, '', return_genres=True)
			genre_list = ','.join([i['value'][0] for i in genre_dict])
			data = self.remove_current_tmdb_mediaitem(function(genre_list, 1)['results'])
			item_list = list(self.make_tmdb_listitems(data))
			self.setProperty('more_from_genres.number', count_insert % len(item_list))
			self.item_action_dict[genres_id] = 'tmdb_id'
			self.add_items(genres_id, item_list)
		except: pass

	def make_network(self):
		if not networks_id in self.enabled_lists: return
		try:
			network = self.meta_get('studio')
			network_id = [i['id'] for i in tmdb_company_id(network)['results'] if i['name'] == network][0] \
						if self.media_type == 'movie' else [item['id'] for item in networks if 'name' in item and item['name'] == network][0]
			function = tmdb_movies_networks if self.media_type == 'movie' else tmdb_tv_networks
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
			data = movieset_meta(coll_id, self.meta_user_info)
			item_list = list(self.make_tmdb_listitems(sorted(data['parts'], key=lambda k: k['release_date'] or '2050')))
			self.setProperty('more_from_collection.name', data['title'])
			self.setProperty('more_from_collection.overview', data['plot'] or data['title'])
			self.setProperty('more_from_collection.poster', data['poster'] or empty_poster)
			self.setProperty('more_from_collection.number', count_insert % len(item_list))
			self.item_action_dict[collection_id] = 'tmdb_id'
			self.add_items(collection_id, item_list)
		except: pass

	def get_release_year(self, release_data):
		try:
			if release_data in ('', None): release_data = 'N/A'
			else: release_data = release_data.split('-')[0]
		except: pass
		return release_data

	def get_finish(self):
		label = ls(32791) if self.percent_watched == '100' else ls(33062)
		if self.listitem_check() and self.percent_watched in ('0', '100'): finished = self.get_infolabel('ListItem.EndTime')
		else:
			kodi_clock = self.get_infolabel('System.Time')
			if any(i in kodi_clock for i in ('AM', 'PM')): _format = '%I:%M %p'
			else: _format = '%H:%M'
			if self.percent_watched == '100': remaining_time = self.duration_data
			else: remaining_time = ((100 - int(self.percent_watched))/100) * self.duration_data
			current_time = datetime.now()
			finish_time = current_time + timedelta(minutes=remaining_time)
			finished = finish_time.strftime(_format)
		return '%s: %s' % (label, finished)

	def get_duration(self):
		return ls(33058) % self.duration_data

	def get_progress(self):
		self.percent_watched = get_progress_percent(get_bookmarks(self.watched_indicators, 'movie'), self.tmdb_id)
		if not self.percent_watched:
			try:
				watched_info = get_watched_info_movie(self.watched_indicators)
				self.percent_watched = '100' if get_watched_status_movie(watched_info, str(self.tmdb_id))[0] == 1 else '0'
			except: self.percent_watched = '0'
		progress_status = '%s%% %s' % (self.percent_watched, ls(32475))
		return progress_status

	def get_last_aired(self):
		if self.extra_info_get('last_episode_to_air', False):
			last_ep = self.extra_info_get('last_episode_to_air')
			last_aired = 'S%.2dE%.2d' % (last_ep['season_number'], last_ep['episode_number'])
		else: return ''
		return '%s: %s' % (ls(32634), last_aired)

	def get_next_aired(self):
		if self.extra_info_get('next_episode_to_air', False):
			next_ep = self.extra_info_get('next_episode_to_air')
			next_aired = 'S%.2dE%.2d' % (next_ep['season_number'], next_ep['episode_number'])
		else: return ''
		return '%s: %s' % (ls(32635), next_aired)

	def get_next_episode(self):
		return_value, curr_season_data, episode_date = '', [], None
		current_date, watched_info = get_datetime(), get_watched_info_tv(self.watched_indicators)
		try:
			ep_list = get_next_episodes(watched_info)
			info = [i for i in ep_list if i['media_ids']['tmdb'] == self.tmdb_id][0]
			current_season = info['season']
			current_episode = info['episode']
			season_data = self.meta_get('season_data')
			curr_season_data = [i for i in season_data if i['season_number'] == current_season][0]
		except: self.nextep_season, self.nextep_episode = 1, 1
		if curr_season_data:
			try:
				adjust_hours = settings.date_offset()
				if current_episode >= curr_season_data['episode_count']: current_season, current_episode, new_season = current_season + 1, 1, True
				else: current_episode, new_season = current_episode + 1, False
				episodes_data = episodes_meta(current_season, self.meta, self.meta_user_info)				
				item = [i for i in episodes_data if i['episode'] == current_episode][0]
				item_get = item.get
				nextep_season, nextep_episode = item_get('season'), item_get('episode')
				episode_date, premiered = adjust_premiered_date(item_get('premiered'), adjust_hours)
			except: pass
		if episode_date and current_date >= episode_date:
			self.nextep_season, self.nextep_episode = nextep_season, nextep_episode
			next_episode_str = 'S%.2dE%.2d' % (self.nextep_season, self.nextep_episode)
			return_value = '%s: %s' % (ls(33041), next_episode_str)
			self.setProperty('next_episode', return_value)
		return return_value

	def make_tvshow_browse_params(self):
		total_seasons = self.meta_get('total_seasons')
		all_episodes = default_all_episodes()
		show_all_episodes = True if all_episodes in (1, 2) else False
		if show_all_episodes:
			if all_episodes == 1 and total_seasons > 1: url_params = {'mode': 'build_season_list', 'tmdb_id': self.tmdb_id}
			else: url_params = {'mode': 'build_episode_list', 'tmdb_id': self.tmdb_id, 'season': 'all'}
		else: url_params = {'mode': 'build_season_list', 'tmdb_id': self.tmdb_id}
		return url_params

	def original_poster(self):
		poster = self.meta_get('custom_poster') or self.meta_get(self.poster_main) or self.meta_get(self.poster_backup) or empty_poster
		self.current_poster = poster
		if 'image.tmdb' in self.current_poster:
			try: poster = change_image_resolution(self.current_poster, 'original')
			except: pass
		elif not self.check_poster_cached(self.current_poster): self.current_poster = self.meta_get(self.poster_backup) or ''
		return poster

	def original_fanart(self):
		fanart = self.meta_get('custom_fanart') or self.meta_get(self.fanart_main) or self.meta_get(self.fanart_backup) or addon_fanart
		return fanart

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

	def listitem_check(self):
		return self.get_infolabel('ListItem.Title') == self.meta_get('title')

	def add_items(self, _id, items):
		self.getControl(_id).addItems(items)

	def set_poster(self):
		if self.current_poster:
			self.getControl(200).setImage(self.current_poster)
			self.getControl(201).setImage(self.poster)
			total_time = 0
			while not self.check_poster_cached(self.poster) and not total_time > 200:
				total_time += 1
				self.sleep(50)
			self.getControl(200).setImage(self.poster)
		else: self.setProperty('active_poster', 'false')

	def check_poster_cached(self, poster):
		try:
			if poster == empty_poster: return True
			if fetch_kodi_imagecache(poster): return True
			return False
		except: return True

	def show_text_media(self, text=''):
		if not text: text = self.plot
		return self.open_window(('windows.extras', 'ShowTextMedia'), 'textviewer_media.xml', text=text, poster=self.poster)

	def show_text_media_list(self, chosen_var):
		return self.open_window(('windows.extras', 'ShowTextMedia'), 'textviewer_media_list.xml',
								items=self.get_attribute(self, chosen_var), current_index=self.get_position(self.control_id), poster=self.poster)

	def tvshow_browse(self):
		close_all_dialog()
		url_params = self.make_tvshow_browse_params()
		self.selected = self.folder_runner % self.build_url(url_params)
		self.close()

	def movies_play(self):
		url_params = {'mode': 'playback.media', 'media_type': 'movie', 'tmdb_id': self.tmdb_id}
		Sources().playback_prep(url_params)

	def show_trailers(self):
		chosen = trailer_choice(self.media_type, self.poster, self.tmdb_id, self.meta_get('trailer'), self.meta_get('all_trailers'))
		if not chosen: return ok_dialog()
		elif chosen == 'canceled': return
		self.open_window(('windows.videoplayer', 'VideoPlayer'), 'videoplayer.xml', video=chosen)

	def show_keywords(self):
		base_media = 'movies' if self.media_type == 'movie' else 'tv'
		keyword_params = imdb_keywords_choice(base_media, self.imdb_id, self.poster)
		if not keyword_params: return
		close_all_dialog()
		self.selected = self.folder_runner % self.build_url(keyword_params)
		self.close()

	def show_images(self):
		return _images.run({'mode': 'imdb_image_results', 'imdb_id': self.imdb_id, 'media_title': self.rootname, 'page_no': 1, 'rolling_count_list': [0]})

	def show_extrainfo(self):
		text = media_extra_info({'media_type': self.media_type, 'meta': self.meta})
		return self.show_text_media(text)

	def show_genres(self):
		if not self.genre: return
		base_media = 'movies' if self.media_type == 'movie' else 'tv'
		genre_params = genres_choice(base_media, self.genre, self.poster)
		if not genre_params: return
		close_all_dialog()
		self.selected = self.folder_runner % self.build_url(genre_params)
		self.close()

	def play_nextep(self):
		if self.nextep_season == None: return ok_dialog(text=33116)
		url_params = {'mode': 'playback.media', 'media_type': 'episode', 'tmdb_id': self.tmdb_id, 'season': self.nextep_season, 'episode': self.nextep_episode}
		Sources().playback_prep(url_params)

	def show_director(self):
		director = self.meta_get('director', None)
		if not director: return
		return person_data_dialog({'query': director, 'is_widget': self.is_widget})

	def show_options(self):
		params = {'content': self.options_media_type, 'tmdb_id': str(self.tmdb_id), 'poster': self.poster, 'is_widget': self.is_widget,
					'window_xml': 'media_select.xml', 'from_extras': 'true'}
		return options_menu_choice(params, self.meta)

	def show_recommended(self):
		mode, action = ('build_movie_list', 'tmdb_movies_recommendations') if self.media_type == 'movie' else ('build_tvshow_list', 'tmdb_tv_recommendations')
		self.selected = self.folder_runner % self.build_url({'mode': mode, 'action': action, 'tmdb_id': self.tmdb_id})
		self.close()

	def show_trakt_manager(self):
		return trakt_manager_choice({'tmdb_id': self.tmdb_id, 'imdb_id': self.imdb_id, 'tvdb_id': self.meta_get('tvdb_id', 'None'),
									'media_type': self.media_type, 'window_xml': 'media_select.xml', 'icon': self.poster})

	def show_favorites_manager(self):
		return favorites_choice({'media_type': self.media_type, 'tmdb_id': str(self.tmdb_id), 'title': self.title, 'refresh': 'false'})

	def play_random_episode(self):
		function = random_choice({'meta': self.meta, 'poster': self.poster, 'return_choice': 'true', 'window_xml': 'media_select.xml'})
		if not function: return
		exec('EpisodeTools(self.meta).%s()' % function)
		self.close()

	def playback_choice(self):
		playback_choice(self.media_type, self.poster, self.meta, None, None, 'media_select.xml')

	def assign_buttons(self):
		setting_id_base = setting_base % self.media_type
		for item in button_ids[:-1]:
			button_action = self.get_setting(setting_id_base + str(item))
			self.setProperty(label_base % item, ls(extras_button_label_values[self.media_type][button_action]))
			self.button_action_dict[item] = button_action
		self.button_action_dict[50] = 'show_text_media'

	def set_starting_constants(self, kwargs):
		self.item_action_dict = {}
		self.button_action_dict = {}
		self.selected = None
		self.meta = kwargs['meta']
		self.meta_get = self.meta.get
		self.media_type = self.meta_get('mediatype')#movie, tvshow
		self.options_media_type = kwargs['options_media_type']
		self.tmdb_id = self.meta_get('tmdb_id')
		self.imdb_id = self.meta_get('imdb_id')
		self.extra_info = self.meta_get('extra_info')
		self.extra_info_get = self.extra_info.get
		self.is_widget = kwargs['is_widget'].lower()
		if self.is_widget == 'true': self.folder_runner = 'ActivateWindow(Videos,%s,return)'
		else: self.folder_runner = 'Container.Update(%s)'
		self.meta_user_info = metadata_user_info()
		self.enabled_lists = extras_enabled_menus()
		self.enable_scrollbars = extras_enable_scrollbars()
		self.enable_animation = extras_enable_animation()
		self.poster_resolution = get_resolution()['poster']
		self.watched_indicators = watched_indicators()
		self.poster_main, self.poster_backup, self.fanart_main, self.fanart_backup, self.clearlogo_main, self.clearlogo_backup = get_art_provider()
		self.title = self.meta_get('title')
		self.year = str(self.meta_get('year'))
		self.rootname = self.meta_get('rootname')
		self.poster = self.original_poster()
		self.fanart = self.original_fanart()
		self.clearlogo = self.meta_get('custom_clearlogo') or self.meta_get(self.clearlogo_main) or self.meta_get(self.clearlogo_backup) or ''
		self.plot = self.meta_get('tvshow_plot', '') or self.meta_get('plot', '')
		self.rating = str(round(self.meta_get('rating'), 1))
		self.mpaa = self.meta_get('mpaa')
		self.status = self.extra_info_get('status', '').replace('Series', '')
		self.genre = self.meta_get('genre')
		self.network = self.meta_get('studio') or 'N/A'
		if not self.network: self.network = ''
		self.duration_data = int(float(self.meta_get('duration'))/60)
		self.duration = self.get_duration()
		if self.media_type == 'movie':
			self.progress = self.get_progress()
			self.finish_watching = self.get_finish()
			self.last_aired_episode, self.next_aired_episode = '', ''
		else:
			self.nextep_season, self.nextep_episode = None, None
			self.progress, self.finish_watching = '', ''
			self.last_aired_episode = self.get_last_aired()
			if self.status in finished_tvshow: self.next_aired_episode = ''
			else: self.next_aired_episode = self.get_next_aired()
			Thread(target=self.get_next_episode).start()

	def set_properties(self):
		self.assign_buttons()
		self.setProperty('media_type', self.media_type)
		self.setProperty('fanart', self.fanart)
		self.setProperty('clearlogo', self.clearlogo)
		self.setProperty('title', self.title)
		self.setProperty('plot', self.plot)
		self.setProperty('year', self.year)
		self.setProperty('rating', self.rating)
		self.setProperty('mpaa', self.mpaa)
		self.setProperty('status', self.status)
		self.setProperty('genre', self.genre)
		self.setProperty('network', self.network)
		self.setProperty('duration', self.duration)
		self.setProperty('progress', self.progress)
		self.setProperty('finish_watching', self.finish_watching)
		self.setProperty('last_aired_episode', self.last_aired_episode)
		self.setProperty('next_aired_episode', self.next_aired_episode)
		self.setProperty('enable_scrollbars', self.enable_scrollbars)
		self.setProperty('enable_animation', self.enable_animation)

class ShowTextMedia(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.poster = kwargs.get('poster')
		self.text = kwargs.get('text', None)
		self.items = kwargs.get('items', None)
		self.position = kwargs.get('current_index', None)
		if self.items: self.make_menu()
		self.window_id = 2060
		self.set_properties()

	def onInit(self):
		if self.items:
			self.win = self.getControl(self.window_id)
			self.win.addItems(self.item_list)
			self.win.selectItem(self.position)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		if self.items: return self.position

	def onAction(self, action):
		if action in self.closing_actions:
			if self.items: self.position = self.get_position(self.window_id)
			self.close()

	def make_menu(self):
		def builder():
			for item in self.items:
				listitem = self.make_listitem()
				listitem.setProperty('text', item)
				yield listitem
		self.item_list = list(builder())

	def set_properties(self):
		if not self.items: self.setProperty('text', self.text)
		self.setProperty('poster', self.poster)

class ExtrasChooser(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = 5001
		self.kwargs = kwargs
		self.preselect = self.kwargs['preselect']
		self.items = json.loads(self.kwargs['items'])
		self.chosen_indexes = []
		self.append = self.chosen_indexes.append
		self.selected = None
		self.make_menu()

	def onInit(self):
		self.win = self.getControl(self.window_id)
		self.win.addItems(self.item_list)
		if self.preselect:
			for index in self.preselect:
				self.item_list[index].setProperty('check_status', 'checked')
				self.append(index)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		return self.selected

	def onClick(self, controlID):
		if controlID == 10:
			self.selected = sorted(self.chosen_indexes)
			self.close()
		elif controlID == 11:
			self.close()

	def onAction(self, action):
		if action in self.selection_actions:
			position = self.get_position(self.window_id)
			chosen_listitem = self.get_listitem(self.window_id)
			if chosen_listitem.getProperty('check_status') == 'checked':
				chosen_listitem.setProperty('check_status', '')
				self.chosen_indexes.remove(position)
			else:
				chosen_listitem.setProperty('check_status', 'checked')
				self.append(position)
		elif action in self.closing_actions:
			return self.close()

	def make_menu(self):
		def builder():
			for item in self.items:
				listitem = self.make_listitem()
				listitem.setProperty('name', item['name'])
				listitem.setProperty('image', item['image'])
				listitem.setProperty('item', json.dumps(item))
				yield listitem
		self.item_list = list(builder())
