# -*- coding: utf-8 -*-
from caches.base_cache import connect_database
# from modules.kodi_utils import logger

INSERT_ONE = 'INSERT OR REPLACE INTO resolved VALUES (?, ?, ?, ?, ?, ?)'
DELETE_ONE = 'DELETE FROM resolved where id=?'
SELECT_ONE = 'SELECT id from resolved WHERE media_type=? AND tmdb_id=?'
SELECT_ALL = 'SELECT * from resolved'
DELETE_ALL = 'DELETE FROM resolved'

class ResolvedCache:
	def insert_one(self, media_type, tmdb_id, data):
		try:
			provider, name, _id = data['scrape_provider'], data['name'] , data.get('hash') or data.get('id')
			dbcon = connect_database('resolved_db')
			dbcon.execute(INSERT_ONE, (media_type, tmdb_id, provider, name, _id, repr(data)))
		except: pass

	def delete_one(self, _id):
		try:
			dbcon = connect_database('resolved_db')
			dbcon.execute(DELETE_ONE, (_id,))
			dbcon.execute('VACUUM')
		except: pass

	def get_one(self, media_type, tmdb_id):
		dbcon = connect_database('resolved_db')
		try: result = dbcon.execute(SELECT_ONE, (media_type, tmdb_id)).fetchone()[0]
		except: result = []
		return result

	def get_all(self):
		dbcon = connect_database('resolved_db')
		try: result = dbcon.execute(SELECT_ALL).fetchall()
		except: result = []
		return result

	def clear_cache(self):
		try:
			dbcon = connect_database('resolved_db')
			dbcon.execute(DELETE_ALL)
			dbcon.execute('VACUUM')
			return True
		except: return False

resolved_cache = ResolvedCache()
