# -*- coding: utf-8 -*-
from caches.base_cache import connect_database
# from modules.kodi_utils import logger

INSERT_ONE = 'INSERT OR REPLACE INTO resolved VALUES (?, ?, ?, ?, ?)'
DELETE_ONE = 'DELETE FROM resolved where id=?'
SELECT_ONE = 'SELECT data from resolved WHERE media_type=? AND tmdb_id=? AND season=? AND episode=?'
DELETE_TYPE = 'DELETE FROM resolved WHERE media_type=?'

class ResolvedCache:
	def insert_one(self, media_type, tmdb_id, season, episode, data):
		dbcon = connect_database('resolved_db')
		dbcon.execute(INSERT_ONE, (media_type, tmdb_id, season, episode, repr(data)))

	def delete_one(self, _id):
		dbcon = connect_database('resolved_db')
		dbcon.execute(DELETE_ONE, (_id,))
		dbcon.execute('VACUUM')

	def get_one(self, media_type, tmdb_id, season, episode):
		dbcon = connect_database('resolved_db')
		try: result = dbcon.execute(SELECT_ONE, (media_type, tmdb_id, season, episode)).fetchone()[0]
		except:
			result = None
			if media_type == 'episode':
				try: result = dbcon.execute(SELECT_ONE, (media_type, tmdb_id, season, '')).fetchone()[0]
				except: pass
				if not result:
					try: result = dbcon.execute(SELECT_ONE, (media_type, tmdb_id, '', '')).fetchone()[0]
					except: return result
			else: return result
		return eval(result)

	def clear_cache(self, media_type):
		dbcon = connect_database('resolved_db')
		dbcon.execute(DELETE_TYPE, (media_type,))
		dbcon.execute('VACUUM')

resolved_cache = ResolvedCache()
