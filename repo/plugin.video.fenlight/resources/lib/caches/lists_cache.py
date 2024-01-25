# -*- coding: utf-8 -*-
from caches.base_cache import BaseCache
# from modules.kodi_utils import logger

GET_ALL = 'SELECT id FROM lists'
DELETE_ALL = 'DELETE FROM lists'

class ListsCache(BaseCache):
	def __init__(self):
		BaseCache.__init__(self, 'lists_db', 'lists')

	def delete_all_lists(self):
		try:
			dbcon = self.manual_connect('lists_db')
			for i in dbcon.execute(GET_ALL): self.delete_memory_cache(str(i[0]))
			dbcon.execute(DELETE_ALL)
			dbcon.execute('VACUUM')
		except: return

lists_cache = ListsCache()

def lists_cache_object(function, string, args, json=True, expiration=24):
	cache = lists_cache.get(string)
	if cache is not None: return cache
	if isinstance(args, list): args = tuple(args)
	else: args = (args,)
	if json: result = function(*args).json()
	else: result = function(*args)
	lists_cache.set(string, result, expiration=expiration)
	return result