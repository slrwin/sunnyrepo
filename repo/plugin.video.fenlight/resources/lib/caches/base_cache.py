# -*- coding: utf-8 -*-
import time
import sqlite3 as database
from modules import kodi_utils
# logger = kodi_utils.logger

kodi_refresh, sleep, userdata_path, path_join, translatePath = kodi_utils.kodi_refresh, kodi_utils.sleep, kodi_utils.userdata_path, kodi_utils.path_join, kodi_utils.translatePath
delete_file, get_property, set_property, clear_property = kodi_utils.delete_file, kodi_utils.get_property, kodi_utils.set_property, kodi_utils.clear_property
notification, confirm_dialog, ok_dialog, open_file = kodi_utils.notification, kodi_utils.confirm_dialog, kodi_utils.ok_dialog, kodi_utils.open_file
path_exists, list_dirs, progress_dialog, make_directory = kodi_utils.path_exists, kodi_utils.list_dirs, kodi_utils.progress_dialog, kodi_utils.make_directory
databases_path = path_join(userdata_path, 'databases/')
current_dbs = ('navigator.db', 'watched.db', 'favourites.db', 'traktcache.db', 'maincache.db', 'lists.db', 'discover.db', 'metacache.db', 'debridcache.db', 'external.db', 'settings.db')
database_path_raw = path_join(userdata_path, 'databases')
navigator_db = translatePath(path_join(database_path_raw, 'navigator.db'))
watched_db = translatePath(path_join(database_path_raw, 'watched.db'))
favorites_db = translatePath(path_join(database_path_raw, 'favourites.db'))
trakt_db = translatePath(path_join(database_path_raw, 'traktcache.db'))
maincache_db = translatePath(path_join(database_path_raw, 'maincache.db'))
lists_db = translatePath(path_join(database_path_raw, 'lists.db'))
discover_db = translatePath(path_join(database_path_raw, 'discover.db'))
metacache_db = translatePath(path_join(database_path_raw, 'metacache.db'))
debridcache_db = translatePath(path_join(database_path_raw, 'debridcache.db'))
external_db = translatePath(path_join(database_path_raw, 'external.db'))
settings_db = translatePath(path_join(database_path_raw, 'settings.db'))
database_timeout = 20
database_locations = {
'navigator_db': navigator_db, 'watched_db': watched_db, 'favorites_db': favorites_db, 'settings_db': settings_db, 'trakt_db': trakt_db, 'maincache_db': maincache_db,
'metacache_db': metacache_db, 'debridcache_db': debridcache_db, 'lists_db': lists_db, 'discover_db': discover_db, 'external_db': external_db
		}
integrity_check = {
'settings_db': ('settings',),
'navigator_db': ('navigator',),
'watched_db': ('watched_status', 'progress'),
'favorites_db': ('favourites',),
'trakt_db': ('trakt_data', 'watched_status', 'progress'),
'maincache_db': ('maincache',),
'metacache_db': ('metadata', 'season_metadata', 'function_cache'),
'lists_db': ('lists',),
'discover_db': ('discover',),
'debridcache_db': ('debrid_data',),
'external_db': ('results_data',)
		}

table_creators = {
'navigator_db': (
'CREATE TABLE IF NOT EXISTS navigator (list_name text, list_type text, list_contents text, unique (list_name, list_type))',),
'watched_db': (
'CREATE TABLE IF NOT EXISTS watched \
(db_type text not null, media_id text not null, season integer, episode integer, last_played text, title text, unique (db_type, media_id, season, episode))',
'CREATE TABLE IF NOT EXISTS progress \
(db_type text not null, media_id text not null, season integer, episode integer, resume_point text, curr_time text, \
last_played text, resume_id integer, title text, unique (db_type, media_id, season, episode))',
'CREATE TABLE IF NOT EXISTS watched_status (db_type text not null, media_id text not null, status text, unique (db_type, media_id))'),
'favorites_db': (
'CREATE TABLE IF NOT EXISTS favourites (db_type text not null, tmdb_id text not null, title text not null, unique (db_type, tmdb_id))',),
'settings_db': (
'CREATE TABLE IF NOT EXISTS settings (setting_id text not null unique, setting_type text, setting_default text, setting_value text)',),
'trakt_db': (
'CREATE TABLE IF NOT EXISTS trakt_data (id text unique, data text)',
'CREATE TABLE IF NOT EXISTS watched \
(db_type text not null, media_id text not null, season integer, episode integer, last_played text, title text, unique (db_type, media_id, season, episode))',
'CREATE TABLE IF NOT EXISTS progress \
(db_type text not null, media_id text not null, season integer, episode integer, resume_point text, curr_time text, \
last_played text, resume_id integer, title text, unique (db_type, media_id, season, episode))',
'CREATE TABLE IF NOT EXISTS watched_status (db_type text not null, media_id text not null, status text, unique (db_type, media_id))'),
'maincache_db': (
'CREATE TABLE IF NOT EXISTS maincache (id text unique, data text, expires integer)',),
'metacache_db': (
'CREATE TABLE IF NOT EXISTS metadata (db_type text not null, tmdb_id text not null, imdb_id text, tvdb_id text, meta text, expires integer, unique (db_type, tmdb_id))',
'CREATE TABLE IF NOT EXISTS season_metadata (tmdb_id text not null unique, meta text, expires integer)',
'CREATE TABLE IF NOT EXISTS function_cache (string_id text not null unique, data text, expires integer)'),
'debridcache_db': (
'CREATE TABLE IF NOT EXISTS debrid_data (hash text not null, debrid text not null, cached text, expires integer, unique (hash, debrid))',),
'lists_db': (
'CREATE TABLE IF NOT EXISTS lists (id text unique, data text, expires integer)',),
'external_db': (
'CREATE TABLE IF NOT EXISTS results_data (provider text not null, db_type text not null, tmdb_id text not null, title text, year integer, season text, episode text, results text, \
expires integer, unique (provider, db_type, tmdb_id, title, year, season, episode))',),
'discover_db': (
'CREATE TABLE IF NOT EXISTS discover (id text not null unique, db_type text not null, data text)',)
		}
media_prop = 'fenlight.%s'
BASE_GET = 'SELECT expires, data FROM %s WHERE id = ?'
BASE_SET = 'INSERT OR REPLACE INTO %s(id, data, expires) VALUES (?, ?, ?)'
BASE_DELETE = 'DELETE FROM %s WHERE id = ?'

def make_database(database_name):
	dbcon = database.connect(database_locations[database_name])
	for command in table_creators[database_name]: dbcon.execute(command)
	dbcon.close()

def make_databases():
	if not path_exists(databases_path): make_directory(databases_path)
	for database_name, database_location in database_locations.items():
		dbcon = database.connect(database_location)
		for command in table_creators[database_name]: dbcon.execute(command)

def connect_database(database_name):
	dbcon = database.connect(database_locations[database_name], timeout=database_timeout, isolation_level=None, check_same_thread=False)
	dbcon.execute('PRAGMA synchronous = OFF')
	dbcon.execute('PRAGMA journal_mode = OFF')
	return dbcon

def get_timestamp(offset=0):
	# Offset is in HOURS multiply by 3600 to get seconds
	return int(time.time()) + (offset*3600)

def remove_old_databases():
	try:
		files = list_dirs(databases_path)[1]
		for item in files:
			if not item in current_dbs:
				try: delete_file(databases_path + item)
				except: pass
	except: pass

def check_databases_integrity():
	def _process(database_name, tables):
		database_location = database_locations[database_name]
		try:
			dbcon = database.connect(database_location)
			for db_table in tables: dbcon.execute(command_base % db_table)
		except:
			database_errors.append(database_name)
			if path_exists(database_location):
				try: dbcon.close()
				except: pass
				delete_file(database_location)
	command_base = 'SELECT * FROM %s LIMIT 1'
	database_errors = []
	for database_name, tables in integrity_check.items(): _process(database_name, tables)
	make_databases()
	if database_errors: ok_dialog(text='[B]Following Databases Rebuilt:[/B][CR][CR]%s' % ', '.join(database_errors))
	else: notification('No Corrupt or Missing Databases', time=3000)

def clean_databases():
	from caches.external_cache import external_cache
	from caches.main_cache import main_cache
	from caches.meta_cache import meta_cache
	from caches.debrid_cache import debrid_cache
	success = []
	for item in (external_cache, main_cache, meta_cache, debrid_cache): success.append(item.clean_database())
	if all(success): line1 = 'Success'
	elif any(success): line1 = 'Success, with Errors'
	else: line1 = 'Failed'
	notification(line1, time=2000)

def clear_cache(cache_type, silent=False):
	def _confirm(): return silent or confirm_dialog()
	success = True
	if cache_type == 'meta':
		from caches.trakt_cache import clear_trakt_movie_sets
		from caches.meta_cache import delete_meta_cache
		clear_trakt_movie_sets()
		success = delete_meta_cache(silent=silent)
	elif cache_type == 'internal_scrapers':
		if not _confirm(): return
		from apis import easynews_api
		easynews_api.clear_media_results_database()
		for item in ('pm_cloud', 'rd_cloud', 'ad_cloud', 'folders'): clear_cache(item, silent=True)
	elif cache_type == 'external_scrapers':
		from caches.external_cache import external_cache
		from caches.debrid_cache import debrid_cache
		data = external_cache.delete_cache(silent=silent)
		clear_debrid_result = debrid_cache.clear_cache()
		success = (data, clear_debrid_result) == ('success', 'success')
	elif cache_type == 'trakt':
		from caches.trakt_cache import clear_all_trakt_cache_data
		success = clear_all_trakt_cache_data(silent=silent)
	elif cache_type == 'imdb':
		if not _confirm(): return
		from apis.imdb_api import clear_imdb_cache
		success = clear_imdb_cache()
	elif cache_type == 'pm_cloud':
		if not _confirm(): return
		from apis.premiumize_api import PremiumizeAPI
		success = PremiumizeAPI().clear_cache()
	elif cache_type == 'rd_cloud':
		if not _confirm(): return
		from apis.real_debrid_api import RealDebridAPI
		success = RealDebridAPI().clear_cache()
	elif cache_type == 'ad_cloud':
		if not _confirm(): return
		from apis.alldebrid_api import AllDebridAPI
		success = AllDebridAPI().clear_cache()
	elif cache_type == 'folders':
		from caches.main_cache import main_cache
		main_cache.delete_all_folderscrapers()
	elif cache_type == 'list':
		if not _confirm(): return
		from caches.lists_cache import lists_cache
		lists_cache.delete_all_lists()
	else:# main
		if not _confirm(): return
		from caches.main_cache import main_cache
		main_cache.delete_all()
	if not silent and success: notification('Success')

def clear_all_cache():
	if not confirm_dialog(): return
	progressDialog = progress_dialog()
	line = 'Clearing....[CR]%s'
	caches = (('meta', 'Meta Cache'), ('internal_scrapers', 'Internal Scrapers Cache'), ('external_scrapers', 'External Scrapers Cache'),
			('trakt', 'Trakt Cache'), ('imdb', 'IMDb Cache'), ('list', 'List Data Cache', ), ('main', 'Main Cache', ),
			('pm_cloud', 'Premiumize Cloud'), ('rd_cloud', 'Real Debrid Cloud'), ('ad_cloud', 'All Debrid Cloud'))
	for count, cache_type in enumerate(caches, 1):
		try:
			progressDialog.update(line % (cache_type[1]), int(float(count) / float(len(caches)) * 100))
			clear_cache(cache_type[0], silent=True)
			sleep(1000)
		except: pass
	progressDialog.close()
	sleep(100)
	ok_dialog(text='Success')

def refresh_cached_data(meta):
	from caches.meta_cache import meta_cache
	media_type, tmdb_id, imdb_id = meta['mediatype'], meta['tmdb_id'], meta['imdb_id']
	try: meta_cache.delete(media_type, 'tmdb_id', tmdb_id, meta)
	except: return notification('Error')
	from apis.imdb_api import refresh_imdb_meta_data
	refresh_imdb_meta_data(imdb_id)
	notification('Success')
	kodi_refresh()

class BaseCache(object):
	def __init__(self, dbfile, table):
		self.table = table
		self.dbfile = dbfile

	def get(self, string):
		result = None
		try:
			current_time = get_timestamp()
			result = self.get_memory_cache(string, current_time)
			if result is None:
				dbcon = connect_database(self.dbfile)
				cache_data = dbcon.execute(BASE_GET % self.table, (string,)).fetchone()
				if cache_data:
					if cache_data[0] > current_time:
						result = eval(cache_data[1])
						self.set_memory_cache(result, string, cache_data[0])
					else: self.delete(string)
		except: pass
		return result

	def set(self, string, data, expiration=720):
		try:
			dbcon = connect_database(self.dbfile)
			expires = get_timestamp(expiration)
			dbcon.execute(BASE_SET % self.table, (string, repr(data), int(expires)))
			self.set_memory_cache(data, string, int(expires))
		except: return None

	def get_memory_cache(self, string, current_time):
		result = None
		try:
			cachedata = get_property(media_prop % string)
			if cachedata:
				cachedata = eval(cachedata)
				if cachedata[0] > current_time: result = cachedata[1]
		except: pass
		return result

	def set_memory_cache(self, data, string, expires):
		try:
			cachedata = (expires, data)
			cachedata_repr = repr(cachedata)
			set_property(media_prop % string, cachedata_repr)
		except: pass

	def delete(self, string):
		try:
			dbcon = connect_database(self.dbfile)
			dbcon.execute(BASE_DELETE % self.table, (string,))
			self.delete_memory_cache(string)
		except: pass

	def delete_memory_cache(self, string):
		clear_property(media_prop % string)

	def manual_connect(self, dbfile):
		return connect_database(dbfile)
