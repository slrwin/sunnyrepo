# -*- coding: utf-8 -*-
from xbmc import getInfoLabel
from urllib.parse import parse_qsl
# from modules.kodi_utils import logger

def external():
	return 'fen' not in getInfoLabel('Container.PluginName')

def routing(sys):
	params = dict(parse_qsl(sys.argv[2][1:], keep_blank_values=True))
	_get = params.get
	mode = _get('mode', 'navigator.main')
	if 'navigator.' in mode:
		from indexers.navigator import Navigator
		return exec('Navigator(params).%s()' % mode.split('.')[1])
	elif 'menu_editor.' in mode:
		from modules.menu_editor import MenuEditor
		return exec('MenuEditor(params).%s()' % mode.split('.')[1])
	elif 'discover.' in mode:
		from indexers.discover import Discover
		return exec('Discover(params).%s()' % mode.split('.')[1])
	elif 'furk.' in mode:
		if mode == 'furk.browse_packs':
			from modules.sources import Sources
			return Sources().furkPacks(_get('file_name'), _get('file_id'))
		elif mode == 'furk.add_to_files':
			from indexers.furk import add_to_files
			return add_to_files(_get('item_id'))
		elif mode == 'furk.remove_from_files':
			from indexers.furk import remove_from_files
			return remove_from_files(_get('item_id'))
		elif mode == 'furk.myfiles_protect_unprotect':
			from indexers.furk import myfiles_protect_unprotect
			return myfiles_protect_unprotect(_get('action'), _get('name'), _get('item_id'))
		else:
			from indexers import furk
			return exec('furk.%s(params)' % mode.split('.')[1])
	elif 'easynews.' in mode:
		from indexers import easynews
		return exec('easynews.%s(params)' % mode.split('.')[1])
	elif 'playback.' in mode:
		if mode == 'playback.media':
			from modules.sources import Sources
			return Sources().playback_prep(params)
		elif mode == 'playback.video':
			from modules.player import FenPlayer
			return FenPlayer().run(_get('url', None), _get('obj', None))
	elif 'choice' in mode:
		from indexers import dialogs
		return exec('dialogs.%s(params)' % mode)
	elif 'trakt.' in mode:
		if '.list' in mode:
			from indexers import trakt_lists
			return exec('trakt_lists.%s(params)' % mode.split('.')[2])
		else:
			from apis import trakt_api
			return exec('trakt_api.%s(params)' % mode.split('.')[1])
	elif 'build' in mode:
		if mode == 'build_movie_list':
			from indexers.movies import Movies
			return Movies(params).fetch_list()
		elif mode == 'build_tvshow_list':
			from indexers.tvshows import TVShows
			return TVShows(params).fetch_list()
		elif mode == 'build_season_list':
			from indexers.seasons import build_season_list
			return build_season_list(params)
		elif mode == 'build_episode_list':
			from indexers.episodes import build_episode_list
			return build_episode_list(params)
		elif mode == 'build_in_progress_episode':
			from indexers.episodes import build_single_episode
			return build_single_episode('episode.progress')
		elif mode == 'build_recently_watched_episode':
			from indexers.episodes import build_single_episode
			return build_single_episode('episode.recently_watched')
		elif mode == 'build_next_episode':
			from indexers.episodes import build_single_episode
			return build_single_episode('episode.next')
		elif mode == 'build_my_calendar':
			from indexers.episodes import build_single_episode
			return build_single_episode('episode.trakt', params)
		elif mode == 'build_next_episode_manager':
			from modules.episode_tools import build_next_episode_manager
			return build_next_episode_manager()
		elif mode == 'imdb_build_user_lists':
			from indexers.imdb import imdb_build_user_lists
			return imdb_build_user_lists(_get('media_type'))
		elif mode == 'build_popular_people':
			from indexers.people import popular_people
			return popular_people()
		elif mode == 'imdb_build_keyword_results':
			from indexers.imdb import imdb_build_keyword_results
			return imdb_build_keyword_results(_get('media_type'), _get('query'))
	elif 'watched_status.' in mode:
		if mode == 'watched_status.mark_episode':
			from modules.watched_status import mark_episode
			return mark_episode(params)
		elif mode == 'watched_status.mark_season':
			from modules.watched_status import mark_season
			return mark_season(params)
		elif mode == 'watched_status.mark_tvshow':
			from modules.watched_status import mark_tvshow
			return mark_tvshow(params)
		elif mode == 'watched_status.mark_movie':
			from modules.watched_status import mark_movie
			return mark_movie(params)
		elif mode == 'watched_status.erase_bookmark':
			from modules.watched_status import erase_bookmark
			return erase_bookmark(_get('media_type'), _get('tmdb_id'), _get('season', ''), _get('episode', ''), _get('refresh', 'false'))
	elif 'history.' in mode:
		if mode == 'history.search':
			from indexers.history import search_history
			return search_history(params)
		elif mode == 'history.clear_search':
			from modules.history import clear_search_history
			return clear_search_history()
		elif mode == 'history.remove':
			from modules.history import remove_from_search_history
			return remove_from_search_history(params)
		elif mode == 'history.clear_all':
			from modules.history import clear_all_history
			return clear_all_history(_get('setting_id'), _get('refresh', 'false'))
	elif 'real_debrid' in mode:
		if mode == 'real_debrid.rd_torrent_cloud':
			from indexers.real_debrid import rd_torrent_cloud
			return rd_torrent_cloud()
		if mode == 'real_debrid.rd_downloads':
			from indexers.real_debrid import rd_downloads
			return rd_downloads()
		elif mode == 'real_debrid.browse_rd_cloud':
			from indexers.real_debrid import browse_rd_cloud
			return browse_rd_cloud(_get('id'))
		elif mode == 'real_debrid.resolve_rd':
			from indexers.real_debrid import resolve_rd
			return resolve_rd(params)
		elif mode == 'real_debrid.rd_account_info':
			from indexers.real_debrid import rd_account_info
			return rd_account_info()
		elif mode == 'real_debrid.authenticate':
			from apis.real_debrid_api import RealDebridAPI
			return RealDebridAPI().auth()
		elif mode == 'real_debrid.revoke_authentication':
			from apis.real_debrid_api import RealDebridAPI
			return RealDebridAPI().revoke()
	elif 'premiumize' in mode:
		if mode == 'premiumize.pm_torrent_cloud':
			from indexers.premiumize import pm_torrent_cloud
			return pm_torrent_cloud(_get('id', None), _get('folder_name', None))
		elif mode == 'premiumize.pm_transfers':
			from indexers.premiumize import pm_transfers
			return pm_transfers()
		elif mode == 'premiumize.pm_account_info':
			from indexers.premiumize import pm_account_info
			return pm_account_info()
		elif mode == 'premiumize.authenticate':
			from apis.premiumize_api import PremiumizeAPI
			return PremiumizeAPI().auth()
		elif mode == 'premiumize.revoke_authentication':
			from apis.premiumize_api import PremiumizeAPI
			return PremiumizeAPI().revoke()
	elif 'alldebrid' in mode:
		if mode == 'alldebrid.ad_torrent_cloud':
			from indexers.alldebrid import ad_torrent_cloud
			return ad_torrent_cloud(_get('id', None))
		elif mode == 'alldebrid.browse_ad_cloud':
			from indexers.alldebrid import browse_ad_cloud
			return browse_ad_cloud(_get('folder'))
		elif mode == 'alldebrid.resolve_ad':
			from indexers.alldebrid import resolve_ad
			return resolve_ad(params)
		elif mode == 'alldebrid.ad_account_info':
			from indexers.alldebrid import ad_account_info
			return ad_account_info()
		elif mode == 'alldebrid.authenticate':
			from apis.alldebrid_api import AllDebridAPI
			return AllDebridAPI().auth()
		elif mode == 'alldebrid.revoke_authentication':
			from apis.alldebrid_api import AllDebridAPI
			return AllDebridAPI().revoke()
	elif '_settings' in mode:
		if mode == 'open_settings':
			from modules.kodi_utils import open_settings
			return open_settings(_get('query', '0.0'), _get('addon', 'plugin.video.fen'))
		elif mode == 'clean_settings':
			from modules.kodi_utils import clean_settings
			return clean_settings()
		elif mode == 'clear_settings_window_properties':
			from modules.kodi_utils import clear_settings_window_properties
			return clear_settings_window_properties()
	elif '_cache' in mode:
		import caches
		if mode == 'clear_cache':
			return caches.clear_cache(_get('cache'))
		elif mode == 'clear_all_cache':
			return caches.clear_all_cache()
		elif mode == 'clean_databases_cache':
			return caches.clean_databases()
		elif mode == 'check_corrupt_databases_cache':
			return caches.check_corrupt_databases()
	elif '_image' in mode:
		from indexers.images import Images
		return Images().run(params)
	elif '_text' in mode:
		if mode == 'show_text':
			from modules.kodi_utils import show_text
			return show_text(_get('heading'), _get('text', None), _get('file', None), _get('font_size', 'small'), _get('kodi_log', 'false') == 'true')
		elif mode == 'show_text_media':
			from modules.kodi_utils import show_text_media
			return show_text(_get('heading'), _get('text', None), _get('file', None), _get('meta'), {})
	elif '_view' in mode:
		from modules import kodi_utils
		if mode == 'choose_view':
			return kodi_utils.choose_view(_get('view_type'), _get('content', ''))
		elif mode == 'set_view':
			return kodi_utils.set_view(_get('view_type'))
	##EXTRA modes##
	elif mode == 'kodi_refresh':
		from modules.kodi_utils import kodi_refresh
		return kodi_refresh()
	elif mode == 'get_search_term':
		from modules.history import get_search_term
		return get_search_term(params)
	elif mode == 'person_data_dialog':
		from indexers.people import person_data_dialog
		return person_data_dialog(params)
	elif mode == 'downloader':
		from modules.downloader import runner
		return runner(params)
	elif mode == 'download_manager':
		from modules.downloader import download_manager
		return download_manager(params)
	elif mode == 'manual_add_magnet_to_cloud':
		from modules.debrid import manual_add_magnet_to_cloud
		return manual_add_magnet_to_cloud(params)
	elif mode == 'debrid.browse_packs':
		from modules.sources import Sources
		return Sources().debridPacks(_get('provider'), _get('name'), _get('magnet_url'), _get('info_hash'))
	elif mode == 'upload_logfile':
		from modules.kodi_utils import upload_logfile
		return upload_logfile()
	elif mode == 'toggle_language_invoker':
		from modules.kodi_utils import toggle_language_invoker
		return toggle_language_invoker()
