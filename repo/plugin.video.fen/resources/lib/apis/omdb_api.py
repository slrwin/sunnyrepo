# -*- coding: utf-8 -*-
from caches.main_cache import cache_object
from modules.kodi_utils import make_session
from modules.settings import omdb_api_key
# from modules.kodi_utils import logger


# Looks like this code will have to use the XML result from OMDb instead of the easier JSON result as not all values are returned with the JSON result.
EXPIRY_1_WEEK = 168
url = 'http://www.omdbapi.com/?apikey=%s&i=%s'
cache_string = 'omdb_%s_%s'
session = make_session('http://www.omdbapi.com/')

class OMDbAPI:
	def fetch_info(self, imdb_id, media_type):
		if not imdb_id: return {}
		self.api_key = omdb_api_key()
		if not self.api_key: return {}
		string = cache_string % (media_type, imdb_id)
		return cache_object(self.process_result, string, imdb_id, json=False, expiration=EXPIRY_1_WEEK)

	def process_result(self, imdb_id):
		data = {}
		try:
			try: result = session.get(url % (self.api_key, imdb_id)).json()
			except: return {}
			if not result.get('Response', 'False') == 'True': return {}
			try: rotten_tomatoes_rating = [i.get('Value').replace('N/A', '') for i in result.get('Ratings', []) if i.get('Source', '') == 'Rotten Tomatoes'][0]
			except: rotten_tomatoes_rating = ''
			metascore_rating = result.get('Metascore', '').replace('N/A', '')
			imdb_rating = result.get('imdbRating', '').replace('N/A', '')
			imdb_votes = result.get('imdbVotes', '').replace('N/A', '')
			awards = result.get('Awards', '').replace('N/A', '')
			data = {'rotten_tomatoes_rating': rotten_tomatoes_rating, 'metascore_rating': metascore_rating, 'imdb_rating': imdb_rating, 'imdb_votes': imdb_votes, 'awards': awards}
		except: pass
		return data
