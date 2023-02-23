# -*- coding: utf-8 -*-
from modules.kodi_utils import translate_path, get_property, tmdb_default_api, fanarttv_default_api, get_setting, external_browse, current_skin, path_exists, \
								custom_xml_path, custom_skin_path, default_skin_path
# from modules.kodi_utils import logger

download_directories_dict = {'movie': 'movie_download_directory', 'episode': 'tvshow_download_directory', 'thumb_url': 'image_download_directory',
							'image_url': 'image_download_directory','image': 'image_download_directory', 'premium': 'premium_download_directory',
							None: 'premium_download_directory', 'None': False}
results_style_dict = {'true': 'contrast', 'false': 'non_contrast'}
results_window_numbers_dict = {'list': 2000, 'infolist': 2001, 'medialist': 2002, 'rows': 2003, 'shift': 2004, 'thumbs': 2005}
year_in_title_dict = {'movie': (1, 3), 'tvshow': (2, 3)}
default_action_dict = {0: 'play', 1: 'cancel'}
extras_open_action_dict = {'movie': (1, 3), 'tvshow': (2, 3)}
prescrape_scrapers_tuple = ('furk', 'easynews', 'rd_cloud', 'pm_cloud', 'ad_cloud')
sort_to_top_dict = {'folders': 'results.sort_folders_first', 'rd_cloud': 'results.sort_rdcloud_first',
					'pm_cloud': 'results.sort_pmcloud_first', 'ad_cloud': 'results.sort_adcloud_first'}
internal_scrapers_clouds_list = [('rd', 'provider.rd_cloud'), ('pm', 'provider.pm_cloud'), ('ad', 'provider.ad_cloud')]
single_ep_format_dict = {0: '%d-%m-%Y', 1: '%Y-%m-%d', 2: '%m-%d-%Y'}
default_art_provider_tuple = ('poster', 'poster2', 'fanart', 'fanart2', 'clearlogo', 'clearlogo2')
art_provider_dict = {True: ('poster2', 'poster', 'fanart2', 'fanart', 'clearlogo2', 'clearlogo'), False: ('poster', 'poster2', 'fanart', 'fanart2', 'clearlogo2', 'clearlogo')}
resolution_tuple = (
	{'poster': 'w185', 'fanart': 'w300', 'still': 'w185', 'profile': 'w185', 'clearlogo': 'original'},
	{'poster': 'w342', 'fanart': 'w780', 'still': 'w300', 'profile': 'w342', 'clearlogo': 'original'},
	{'poster': 'w780', 'fanart': 'w1280', 'still': 'original', 'profile': 'h632', 'clearlogo': 'original'},
	{'poster': 'original', 'fanart': 'original', 'still': 'original', 'profile': 'original', 'clearlogo': 'original'})

def skin_location(skin_xml):
	user_skin = current_skin()
	if '32860' in get_setting('custom_skins.enable'): return translate_path(default_skin_path)
	if path_exists(translate_path(custom_xml_path % (user_skin, skin_xml))): return translate_path(custom_skin_path + user_skin)
	return translate_path(default_skin_path)

def use_skin_fonts():
	return get_setting('use_skin_fonts')

def date_offset():
	return int(get_setting('datetime.offset', '0')) + 5

def results_format():
	return str(get_setting('results.format', 'List').lower())

def results_style():
	return results_style_dict[get_setting('results.use_contrast', 'true')]

def results_xml_window_number(window_format=None):
	if not window_format: window_format = results_format()
	return results_window_numbers_dict[window_format.split(' ')[0]]

def store_resolved_torrent_to_cloud(debrid_service, pack):
	setting_value = int(get_setting('store_resolved_torrent.%s' % debrid_service.lower(), '0'))
	return setting_value in (1, 2) if pack else setting_value == 1

def enabled_debrids_check(debrid_service):
	if not get_setting('%s.enabled' % debrid_service) == 'true': return False
	if get_setting('%s.token' % debrid_service) in (None, ''): return False
	return True

def monitor_playback():
	return get_setting('playback.monitor_success', 'true') == 'true'

def limit_resolve():
	return get_setting('playback.limit_resolve', 'false') == 'true'

def disable_content_lookup():
	return get_setting('playback.disable_content_lookup') == 'true'

def widget_load_empty():
	return get_setting('playback.widget_load_empty', 'true') == 'true'

def easynews_max_retries():
	return int(get_setting('playback.easynews_max_retries', '1'))

def display_sleep_time():
	return 100

def show_specials():
	return get_setting('show_specials', 'false') == 'true'

def show_unaired_watchlist():
	return get_setting('show_unaired_watchlist', 'false') == 'true'

def include_year_in_title(media_type):
	return int(get_setting('include_year_in_title', '0')) in year_in_title_dict[media_type]
	
def movies_directory():
	return translate_path(get_setting('movies_directory'))
	
def tv_show_directory():
	return translate_path(get_setting('tv_shows_directory'))

def download_directory(media_type):
	return translate_path(get_setting(download_directories_dict[media_type]))

def source_folders_directory(media_type, source):
	setting = '%s.movies_directory' % source if media_type == 'movie' else '%s.tv_shows_directory' % source
	if get_setting(setting) not in ('', 'None', None): return translate_path( get_setting(setting))
	else: return False

def suppress_episode_plot():
	return get_setting('suppress_episode_plot', 'false') == 'true'

def paginate(is_widget=None):
	if not get_setting('paginate.lists', 'false') == 'true': return False
	if paginate_widget_only():
		is_widget = is_widget or external_browse()
		return True if is_widget else False
	return True

def paginate_widget_only():
	return get_setting('paginate.widget_only', 'false') == 'true'

def page_limit():
	return int(get_setting('paginate.limit', '20'))

def page_reference():
	return int(get_setting('paginate.reference', '0'))

def ignore_articles():
	return get_setting('ignore_articles', 'false') == 'true'

def use_year_in_search():
	return get_setting('meta_use_year_in_search') == 'true'

def default_all_episodes():
	return int(get_setting('default_all_episodes'))

def quality_filter(setting):
	return get_setting(setting).split(', ')

def audio_filters():
	setting = get_setting('filter_audio')
	if setting in ('', None): return []
	return setting.split(', ')

def include_prerelease_results():
	return get_setting('include_prerelease_results', 'true') == 'true'

def auto_play(media_type):
	return get_setting('auto_play_%s' % media_type, 'false') == 'true'

def autoplay_next_episode():
	if auto_play('episode') and get_setting('autoplay_next_episode', 'false') == 'true': return True
	else: return False

def autoscrape_next_episode():
	if not auto_play('episode') and get_setting('autoscrape_next_episode', 'false') == 'true': return True
	else: return False

def auto_nextep_settings():
	scraper_time = int(get_setting('results.timeout', '60')) + 20
	window_percentage = 100 - int(get_setting('autoplay_next_window_percentage', '95'))
	alert_method = int(get_setting('autoplay_alert_method', '0'))
	default_action = default_action_dict[int(get_setting('autoplay_default_action', '1'))] if alert_method == 0 else 'cancel'
	return {'scraper_time': scraper_time, 'window_percentage': window_percentage, 'alert_method': alert_method, 'default_action': default_action}

def progress_flags_direction():
	return int(get_setting('results.progress_flags_direction', '0'))

def filter_status(filter_type):
	return int(get_setting('filter_%s' % filter_type, '0'))

def ignore_results_filter():
	return int(get_setting('results.ignore_filter', '0'))

def display_uncached_torrents():
	return get_setting('torrent.display.uncached', 'false') == 'true'

def trakt_sync_interval():
	setting = get_setting('trakt.sync_interval', '25')
	interval = int(setting) * 60
	return setting, interval

def trakt_sync_refresh_widgets():
	return get_setting('trakt.sync_refresh_widgets', 'true') == 'true'

def calendar_sort_order():
	return int(get_setting('trakt.calendar_sort_order', '0'))

def lists_sort_order(setting):
	return int(get_setting('sort.%s' % setting, '0'))

def auto_start_fen():
	return get_setting('auto_start_fen', 'false') == 'true'

def furk_active():
	if get_setting('provider.furk', 'false') == 'true':
		if not get_setting('furk_api_key'):
			furk_status = False if '' in (get_setting('furk_login'), get_setting('furk_password')) else True
		else: furk_status = True
	else: furk_status = False
	return furk_status

def easynews_active():
	if get_setting('provider.easynews', 'false') == 'true':
		easynews_status = False if '' in (get_setting('easynews_user'), get_setting('easynews_password')) else True
	else: easynews_status = False
	return easynews_status

def watched_indicators():
	if get_setting('trakt.user') == '': return 0
	return int(get_setting('watched_indicators','0'))

def max_threads():
	if not get_setting('limit_concurrent_threads', 'false') == 'true': return 60
	return int(get_setting('max_threads', '60'))

def widget_hide_next_page():
	return get_setting('widget_hide_next_page', 'false') == 'true'

def widget_hide_watched():
	return get_setting('widget_hide_watched', 'false') == 'true'

def extras_open_action(media_type):
	return int(get_setting('extras.open_action', '0')) in extras_open_action_dict[media_type]

def extras_enable_scrollbars():
	return get_setting('extras.enable_scrollbars', 'true')

def extras_enable_animation():
	return get_setting('extras.enable_animation', 'false')

def extras_exclude_non_acting():
	return get_setting('extras.exclude_non_acting_roles', 'true') == 'true'

def extras_enabled_menus():
	setting = get_setting('extras.enabled_menus')
	if setting in ('', None, 'noop', []): return []
	return [int(i) for i in setting.split(',')]

def check_prescrape_sources(scraper):
	if scraper in prescrape_scrapers_tuple: return get_setting('check.%s' % scraper) == 'true'
	if get_setting('check.%s' % scraper) == 'true' and get_setting('auto_play') != 'true': return True
	else: return False

def filter_by_name(scraper):
	if get_property('fs_filterless_search') == 'true': return False
	return get_setting('%s.title_filter' % scraper, 'false') == 'true'

def easynews_language_filter():
	enabled = get_setting('easynews.filter_lang') == 'true'
	if enabled: filters = get_setting('easynews.lang_filters').split(', ')
	else: filters = []
	return enabled, filters

def results_sort_order():
	sort_direction = -1 if get_setting('results.size_sort_direction') == '0' else 1
	return (
			lambda k: (k['quality_rank'], k['provider_rank'], sort_direction*k['size']), #Quality, Provider, Size
			lambda k: (k['quality_rank'], sort_direction*k['size'], k['provider_rank']), #Quality, Size, Provider
			lambda k: (k['provider_rank'], k['quality_rank'], sort_direction*k['size']), #Provider, Quality, Size
			lambda k: (k['provider_rank'], sort_direction*k['size'], k['quality_rank']), #Provider, Size, Quality
			lambda k: (sort_direction*k['size'], k['quality_rank'], k['provider_rank']), #Size, Quality, Provider
			lambda k: (sort_direction*k['size'], k['provider_rank'], k['quality_rank'])  #Size, Provider, Quality
			)[int(get_setting('results.sort_order', '1'))]

def active_internal_scrapers():
	settings = ['provider.external', 'provider.furk', 'provider.easynews', 'provider.folders']
	settings_append = settings.append
	for item in internal_scrapers_clouds_list:
		if enabled_debrids_check(item[0]): settings_append(item[1])
	active = [i.split('.')[1] for i in settings if get_setting(i) == 'true']
	return active

def provider_sort_ranks():
	fu_priority = int(get_setting('fu.priority', '6'))
	en_priority = int(get_setting('en.priority', '7'))
	rd_priority = int(get_setting('rd.priority', '8'))
	ad_priority = int(get_setting('ad.priority', '9'))
	pm_priority = int(get_setting('pm.priority', '10'))
	return {'furk': fu_priority, 'easynews': en_priority, 'real-debrid': rd_priority, 'premiumize.me': pm_priority, 'alldebrid': ad_priority,
			'rd_cloud': rd_priority, 'pm_cloud': pm_priority, 'ad_cloud': ad_priority, 'folders': 0}

def sort_to_top(provider):
	return get_setting(sort_to_top_dict[provider]) == 'true'

def auto_resume(media_type):
	auto_resume = get_setting('auto_resume_%s' % media_type)
	if auto_resume == '1': return True
	if auto_resume == '2' and auto_play(media_type): return True
	else: return False

def use_season_title():
	return get_setting('use_season_title', 'true') == 'true'

def show_unaired():
	return get_setting('show_unaired', 'true') == 'true'

def single_ep_format():
	return single_ep_format_dict[int(get_setting('single_ep_format', '1'))]

def single_ep_display_title():
	return int(get_setting('single_ep_display', '0'))

def nextep_display_settings():
	include_airdate = get_setting('nextep.include_airdate') == 'true'
	return {'unaired_color': 'red', 'unwatched_color': 'darkgoldenrod', 'include_airdate': include_airdate}

def nextep_content_settings():
	sort_type = int(get_setting('nextep.sort_type', '0'))
	sort_order = int(get_setting('nextep.sort_order', '0'))
	sort_direction = sort_order == 0
	sort_key = 'fen.last_played' if sort_type == 0 else 'fen.first_aired' if sort_type == 1 else 'fen.name'
	include_unaired = get_setting('nextep.include_unaired') == 'true'
	include_unwatched = int(get_setting('nextep.include_unwatched', '0'))
	sort_airing_today_to_top = get_setting('nextep.sort_airing_today_to_top', 'false') == 'true'
	return {'sort_key': sort_key, 'sort_direction': sort_direction, 'sort_type': sort_type, 'sort_order':sort_order,
			'include_unaired': include_unaired, 'include_unwatched': include_unwatched, 'sort_airing_today_to_top': sort_airing_today_to_top}

def scraping_settings():
	highlight_type = int(get_setting('highlight.type', '0'))
	if highlight_type == 3: return {'highlight_type': highlight_type}
	hoster_highlight, torrent_highlight, furk_highlight, easynews_highlight, debrid_cloud_highlight, folders_highlight = '', '', '', '', '', ''
	rd_highlight, pm_highlight, ad_highlight, highlight_4K, highlight_1080P, highlight_720P, highlight_SD = '', '', '', '', '', '', ''
	if highlight_type in (0, 1):
		furk_highlight = get_setting('provider.furk_colour', 'crimson')
		easynews_highlight = get_setting('provider.easynews_colour', 'limegreen')
		debrid_cloud_highlight = get_setting('provider.debrid_cloud_colour', 'darkviolet')
		folders_highlight = get_setting('provider.folders_colour', 'darkgoldenrod')
		if highlight_type == 0:
			hoster_highlight = get_setting('hoster.identify', 'dodgerblue')
			torrent_highlight = get_setting('torrent.identify', 'fuchsia')
		else:
			rd_highlight = get_setting('provider.rd_colour', 'seagreen')
			pm_highlight = get_setting('provider.pm_colour', 'orangered')
			ad_highlight = get_setting('provider.ad_colour', 'goldenrod')
	elif highlight_type == 2:
		highlight_4K = get_setting('scraper_4k_highlight', 'fuchsia')
		highlight_1080P = get_setting('scraper_1080p_highlight', 'lawngreen')
		highlight_720P = get_setting('scraper_720p_highlight', 'gold')
		highlight_SD = get_setting('scraper_SD_highlight', 'dodgerblue')
	return {'highlight_type': highlight_type, 'hoster_highlight': hoster_highlight, 'torrent_highlight': torrent_highlight,'real-debrid': rd_highlight, 'premiumize': pm_highlight,
			'alldebrid': ad_highlight, 'rd_cloud': debrid_cloud_highlight, 'pm_cloud': debrid_cloud_highlight, 'ad_cloud': debrid_cloud_highlight, 'furk': furk_highlight,
			'easynews': easynews_highlight, 'folders': folders_highlight, '4k': highlight_4K, '1080p': highlight_1080P, '720p': highlight_720P, 'sd': highlight_SD}

def get_fanart_data():
	return get_setting('get_fanart_data') == 'true'

def fanarttv_client_key():
	return get_setting('fanart_client_key', fanarttv_default_api)

def tmdb_api_key():
	return get_setting('tmdb_api', tmdb_default_api)

def omdb_api_key():
	return get_setting('omdb_api', '')

def fanarttv_default():
	return get_setting('fanarttv.default', 'false') == 'true'

def get_resolution():
	return resolution_tuple[int(get_setting('image_resolutions', '2'))]

def get_language():
	return get_setting('meta_language', 'en')

def get_art_provider():
	if not get_fanart_data(): return default_art_provider_tuple
	return art_provider_dict[fanarttv_default()]

def metadata_user_info():
	tmdb_api = tmdb_api_key()
	extra_fanart_enabled = get_fanart_data()
	image_resolution = get_resolution()
	meta_language = get_language()
	hide_watched = widget_hide_watched()
	if extra_fanart_enabled: fanart_client_key = fanarttv_client_key()
	else: fanart_client_key = ''
	return {'extra_fanart_enabled': extra_fanart_enabled, 'image_resolution': image_resolution , 'language': meta_language,
			'fanart_client_key': fanart_client_key, 'tmdb_api': tmdb_api, 'widget_hide_watched': hide_watched}
