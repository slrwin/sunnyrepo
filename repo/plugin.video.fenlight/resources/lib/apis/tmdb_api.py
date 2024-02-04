# -*- coding: utf-8 -*-
import datetime
from caches.main_cache import cache_object
from caches.lists_cache import lists_cache_object
from caches.meta_cache import cache_function
from modules.meta_lists import oscar_winners
from modules.kodi_utils import make_session, tmdb_dict_removals, remove_keys, tmdb_default_api as tmdb_api_key
# from modules.kodi_utils import logger

EXPIRY_4_HOURS, EXPIRY_2_DAYS, EXPIRY_1_WEEK = 4, 48, 168
base_url = 'https://api.themoviedb.org/3'
movies_append = 'external_ids,videos,credits,release_dates,alternative_titles,translations,images'
tvshows_append = 'external_ids,videos,credits,content_ratings,alternative_titles,translations,images'
timeout = 20.0
session = make_session(base_url)

def tmdb_movies_oscar_winners(page_no):
	return oscar_winners[page_no-1]

def tmdb_network_details(network_id):
	string = 'tmdb_network_details_%s' % network_id
	url = '%s/network/%s?api_key=%s' % (base_url, network_id, tmdb_api_key)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_keywords_by_query(query, page_no):
	string = 'tmdb_keywords_by_query_%s_%s' % (query, page_no)
	url = '%s/search/keyword?api_key=%s&query=%s&page=%s' % (base_url, tmdb_api_key, query, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_movie_keywords(tmdb_id):
	string = 'tmdb_movie_keywords_%s' % tmdb_id
	url = '%s/movie/%s/keywords?api_key=%s' % (base_url, tmdb_id, tmdb_api_key)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_tv_keywords(tmdb_id):
	string = 'tmdb_tv_keywords_%s' % tmdb_id
	url = '%s/tv/%s/keywords?api_key=%s' % (base_url, tmdb_id, tmdb_api_key)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_movie_keyword_results(tmdb_id, page_no):
	string = 'tmdb_movie_keyword_results_%s_%s' % (tmdb_id, page_no)
	url = '%s/discover/movie?api_key=%s&language=en-US&with_keywords=%s&page=%s' % (base_url, tmdb_api_key, tmdb_id, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_keyword_results(tmdb_id, page_no):
	string = 'tmdb_tv_keyword_results_%s_%s' % (tmdb_id, page_no)
	url = '%s/discover/tv?api_key=%s&language=en-US&with_keywords=%s&page=%s' % (base_url, tmdb_api_key, tmdb_id, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movie_keyword_results_direct(query, page_no):
	try:
		results = tmdb_movie_keyword_results(tmdb_keywords_by_query(query, page_no)['results'][0]['id'], page_no)
		results['total_pages'] = 1
		return results
	except: return None

def tmdb_tv_keyword_results_direct(query, page_no):
	try:
		results = tmdb_tv_keyword_results(tmdb_keywords_by_query(query, page_no)['results'][0]['id'], page_no)
		results['total_pages'] = 1
		return results
	except: return None

def tmdb_company_id(query):
	string = 'tmdb_company_id_%s' % query
	url = '%s/search/company?api_key=%s&query=%s' % (base_url, tmdb_api_key, query)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_media_images(media_type, tmdb_id):
	if media_type == 'movies': media_type = 'movie'
	url = '%s/%s/%s/images?api_key=%s' % (base_url, media_type, tmdb_id, tmdb_api_key)
	return get_tmdb(url).json()

def tmdb_media_videos(media_type, tmdb_id):
	if media_type == 'movies': media_type = 'movie'
	if media_type in ('tvshow', 'tvshows'): media_type = 'tv'
	string = 'tmdb_media_videos_%s_%s' % (media_type, tmdb_id)
	url = '%s/%s/%s/videos?api_key=%s' % (base_url, media_type, tmdb_id, tmdb_api_key)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_movies_discover(query, page_no):
	string = url = query % page_no
	return cache_object(get_tmdb, string, url)

def tmdb_movies_popular(page_no):
	string = 'tmdb_movies_popular_%s' % page_no
	url = '%s/movie/popular?api_key=%s&language=en-US&region=US&with_original_language=en&page=%s' % (base_url, tmdb_api_key, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_popular_today(page_no):
	string = 'tmdb_movies_popular_today_%s' % page_no
	url = '%s/trending/movie/day?api_key=%s&language=en-US&region=US&with_original_language=en&page=%s' % (base_url, tmdb_api_key, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_blockbusters(page_no):
	string = 'tmdb_movies_blockbusters_%s' % page_no
	url = '%s/discover/movie?api_key=%s&language=en-US&region=US&with_original_language=en&sort_by=revenue.desc&page=%s' % (base_url, tmdb_api_key, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_in_theaters(page_no):
	string = 'tmdb_movies_in_theaters_%s' % page_no
	url = '%s/movie/now_playing?api_key=%s&language=en-US&region=US&with_original_language=en&page=%s' % (base_url, tmdb_api_key, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_upcoming(page_no):
	current_date, future_date = get_dates(31, reverse=False)
	string = 'tmdb_movies_upcoming_%s' % page_no
	url = '%s/discover/movie?api_key=%s&language=en-US&region=US&with_original_language=en&release_date.gte=%s&release_date.lte=%s&with_release_type=3|2|1&page=%s' \
							% (base_url, tmdb_api_key, current_date, future_date, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_latest_releases(page_no):
	current_date, previous_date = get_dates(31, reverse=True)
	string = 'tmdb_movies_latest_releases_%s' % page_no
	url = '%s/discover/movie?api_key=%s&language=en-US&region=US&with_original_language=en&release_date.gte=%s&release_date.lte=%s&with_release_type=4|5|6&page=%s' \
							% (base_url, tmdb_api_key, previous_date, current_date, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_premieres(page_no):
	current_date, previous_date = get_dates(31, reverse=True)
	string = 'tmdb_movies_premieres_%s' % page_no
	url = '%s/discover/movie?api_key=%s&language=en-US&region=US&with_original_language=en&release_date.gte=%s&release_date.lte=%s&with_release_type=1|3|2&page=%s' \
							% (base_url, tmdb_api_key, previous_date, current_date, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_genres(genre_id, page_no):
	string = 'tmdb_movies_genres_%s_%s' % (genre_id, page_no)
	url = '%s/discover/movie?api_key=%s&with_genres=%s&language=en-US&region=US&with_original_language=en&release_date.lte=%s&page=%s' \
			% (base_url, tmdb_api_key, genre_id, get_current_date(), page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_languages(language, page_no):
	string = 'tmdb_movies_languages_%s_%s' % (language, page_no)
	url = '%s/discover/movie?api_key=%s&language=en-US&with_original_language=%s&release_date.lte=%s&page=%s' \
			% (base_url, tmdb_api_key, language, get_current_date(), page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_certifications(certification, page_no):
	string = 'tmdb_movies_certifications_%s_%s' % (certification, page_no)
	url = '%s/discover/movie?api_key=%s&language=en-US&region=US&with_original_language=en&certification_country=US&certification=%s&sort_by=%s&release_date.lte=%s&page=%s' \
							% (base_url, tmdb_api_key, certification, 'popularity.desc', get_current_date(), page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_year(year, page_no):
	string = 'tmdb_movies_year_%s_%s' % (year, page_no)
	url = '%s/discover/movie?api_key=%s&language=en-US&region=US&with_original_language=en&certification_country=US&primary_release_year=%s&page=%s' \
							% (base_url, tmdb_api_key, year, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_decade(decade, page_no):
	string = 'tmdb_movies_decade_%s_%s' % (decade, page_no)
	start = '%s-01-01' % decade
	end = get_dates(2)[0] if decade == '2020' else '%s-12-31' % str(int(decade) + 9)
	url = '%s/discover/movie?api_key=%s&language=en-US&region=US&with_original_language=en&primary_release_date.gte=%s' \
			'&primary_release_date.lte=%s&page=%s' % (base_url, tmdb_api_key, start, end, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_providers(provider, page_no):
	string = 'tmdb_movies_providers_%s_%s' % (provider, page_no)
	url = '%s/discover/movie?api_key=%s&watch_region=US&with_watch_providers=%s&vote_count.gte=100&page=%s' % (base_url, tmdb_api_key, provider, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_recommendations(tmdb_id, page_no):
	string = 'tmdb_movies_recommendations_%s_%s' % (tmdb_id, page_no)
	url = '%s/movie/%s/recommendations?api_key=%s&language=en-US&region=US&with_original_language=en&page=%s' % (base_url, tmdb_id, tmdb_api_key, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_search(query, page_no):
	string = 'tmdb_movies_search_%s_%s' % (query, page_no)
	url = '%s/search/movie?api_key=%s&language=en-US&include_adult=true&query=%s&page=%s' % (base_url, tmdb_api_key, query, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_companies(company_id, page_no):
	string = 'tmdb_movies_companies_%s_%s' % (company_id, page_no)
	url = '%s/discover/movie?api_key=%s&language=en-US&region=US&with_original_language=en&with_companies=%s&page=%s' \
							% (base_url, tmdb_api_key, company_id, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_movies_reviews(tmdb_id, page_no):
	url = '%s/movie/%s/reviews?api_key=%s&page=%s' % (base_url, tmdb_id, tmdb_api_key, page_no)
	return get_tmdb(url).json()

def tmdb_tv_discover(query, page_no):
	string = url = query % page_no
	return cache_object(get_tmdb, string, url)

def tmdb_tv_popular(page_no):
	string = 'tmdb_tv_popular_%s' % page_no
	url = '%s/discover/tv?api_key=%s&language=en-US&region=US&with_original_language=en&sort_by=popularity.desc&page=%s' \
							% (base_url, tmdb_api_key, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_popular_today(page_no):
	string = 'tmdb_tv_popular_today_%s' % page_no
	url = '%s/trending/tv/day?api_key=%s&language=en-US&region=US&with_original_language=en&page=%s' % (base_url, tmdb_api_key, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_premieres(page_no):
	current_date, previous_date = get_dates(31, reverse=True)
	string = 'tmdb_tv_premieres_%s' % page_no
	url = '%s/discover/tv?api_key=%s&language=en-US&region=US&with_original_language=en&first_air_date.gte=%s&first_air_date.lte=%s&page=%s' \
							% (base_url, tmdb_api_key, previous_date, current_date, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_airing_today(page_no):
	string = 'tmdb_tv_airing_today_%s' % page_no
	url = '%s/tv/airing_today?api_key=%s&language=en-US&region=US&with_original_language=en&page=%s' % (base_url, tmdb_api_key, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_on_the_air(page_no):
	string = 'tmdb_tv_on_the_air_%s' % page_no
	url = '%s/tv/on_the_air?api_key=%s&language=en-US&region=US&with_original_language=en&page=%s' % (base_url, tmdb_api_key, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_upcoming(page_no):
	current_date, future_date = get_dates(31, reverse=False)
	string = 'tmdb_tv_upcoming_%s' % page_no
	url = '%s/discover/tv?api_key=%s&language=en-US&region=US&with_original_language=en&first_air_date.gte=%s&first_air_date.lte=%s&page=%s' \
							% (base_url, tmdb_api_key, current_date, future_date, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_genres(genre_id, page_no):
	string = 'tmdb_tv_genres_%s_%s' % (genre_id, page_no)
	url = '%s/discover/tv?api_key=%s&with_genres=%s&language=en-US&region=US&with_original_language=en&include_null_first_air_dates=false&release_date.lte=%s&page=%s' \
							% (base_url, tmdb_api_key, genre_id, get_current_date(), page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_languages(language, page_no):
	string = 'tmdb_tv_languages_%s_%s' % (language, page_no)
	url = '%s/discover/tv?api_key=%s&language=en-US&include_null_first_air_dates=false&with_original_language=%s&release_date.lte=%s&page=%s' \
							% (base_url, tmdb_api_key, language, get_current_date(), page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_networks(network_id, page_no):
	string = 'tmdb_tv_networks_%s_%s' % (network_id, page_no)
	url = '%s/discover/tv?api_key=%s&language=en-US&region=US&with_original_language=en&include_null_first_air_dates=false&with_networks=%s&release_date.lte=%s&page=%s' \
							% (base_url, tmdb_api_key, network_id, get_current_date(), page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_providers(provider, page_no):
	string = 'tmdb_tv_providers_%s_%s' % (provider, page_no)
	url = '%s/discover/tv/?api_key=%s&watch_region=US&with_watch_providers=%s&vote_count.gte=100&page=%s' % (base_url, tmdb_api_key, provider, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_year(year, page_no):
	string = 'tmdb_tv_year_%s_%s' % (year, page_no)
	url = '%s/discover/tv?api_key=%s&language=en-US&region=US&with_original_language=en&include_null_first_air_dates=false&first_air_date_year=%s&page=%s' \
							% (base_url, tmdb_api_key, year, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_decade(decade, page_no):
	string = 'tmdb_tv_decade_%s_%s' % (decade, page_no)
	start = '%s-01-01' % decade
	end = get_dates(2)[0] if decade == '2020' else '%s-12-31' % str(int(decade) + 9)
	url = '%s/discover/tv?api_key=%s&language=en-US&region=US&with_original_language=en&include_null_first_air_dates=false&first_air_date.gte=%s' \
			'&first_air_date.lte=%s&page=%s' % (base_url, tmdb_api_key, start, end, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_recommendations(tmdb_id, page_no):
	string = 'tmdb_tv_recommendations_%s_%s' % (tmdb_id, page_no)
	url = '%s/tv/%s/recommendations?api_key=%s&language=en-US&region=US&with_original_language=en&page=%s' % (base_url, tmdb_id, tmdb_api_key, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_search(query, page_no):
	string = 'tmdb_tv_search_%s_%s' % (query, page_no)
	url = '%s/search/tv?api_key=%s&language=en-US&include_adult=true&query=%s&page=%s' % (base_url, tmdb_api_key, query, page_no)
	return lists_cache_object(get_data, string, url, json=False, expiration=EXPIRY_2_DAYS)

def tmdb_tv_reviews(tmdb_id, page_no):
	url = '%s/tv/%s/reviews?api_key=%s&page=%s' % (base_url, tmdb_id, tmdb_api_key, page_no)
	return get_tmdb(url).json()

def tmdb_popular_people(page_no):
	string = 'tmdb_people_popular_%s' % page_no
	url = '%s/person/popular?api_key=%s&language=en&page=%s' % (base_url, tmdb_api_key, page_no)
	return cache_object(get_tmdb, string, url)

def tmdb_trending_people_day(page_no):
	string = 'tmdb_people_trending_day_%s' % page_no
	url = '%s/trending/person/day?api_key=%s&page=%s' % (base_url, tmdb_api_key, page_no)
	return cache_object(get_tmdb, string, url)

def tmdb_trending_people_week(page_no):
	string = 'tmdb_people_trending_week_%s' % page_no
	url = '%s/trending/person/week?api_key=%s&page=%s' % (base_url, tmdb_api_key, page_no)
	return cache_object(get_tmdb, string, url)

def tmdb_people_full_info(actor_id):
	string = 'tmdb_people_full_info_%s' % actor_id
	url = '%s/person/%s?api_key=%s&language=en&append_to_response=external_ids,combined_credits,images,tagged_images' % (base_url, actor_id, tmdb_api_key)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_1_WEEK)

def tmdb_people_info(query, page_no=1):
	string = 'tmdb_people_info_%s_%s' % (query, page_no)
	url = '%s/search/person?api_key=%s&language=en&include_adult=true&query=%s&page=%s' % (base_url, tmdb_api_key, query, page_no)
	return cache_object(get_tmdb, string, url, expiration=EXPIRY_4_HOURS)

def movie_details(tmdb_id):
	try:
		url = '%s/movie/%s?api_key=%s&language=en&append_to_response=%s' % (base_url, tmdb_id, tmdb_api_key, movies_append)
		return get_tmdb(url).json()
	except: return None

def tvshow_details(tmdb_id):
	try:
		url = '%s/tv/%s?api_key=%s&language=en&append_to_response=%s' % (base_url, tmdb_id, tmdb_api_key, tvshows_append)
		return get_tmdb(url).json()
	except: return None

def movie_set_details(collection_id):
	try:
		url = '%s/collection/%s?api_key=%s&language=en' % (base_url, collection_id, tmdb_api_key)
		return get_tmdb(url).json()
	except: return None

def season_episodes_details(tmdb_id, season_no):
	try:
		url = '%s/tv/%s/season/%s?api_key=%s&language=en&append_to_response=credits' % (base_url, tmdb_id, season_no, tmdb_api_key)
		return get_tmdb(url).json()
	except: return None

def movie_external_id(external_source, external_id):
	try:
		string = 'movie_external_id_%s_%s' % (external_source, external_id)
		url = '%s/find/%s?api_key=%s&external_source=%s' % (base_url, external_id, tmdb_api_key, external_source)
		result = cache_function(get_tmdb, string, url)
		result = result['movie_results']
		if result: return result[0]
		else: return None
	except: return None

def tvshow_external_id(external_source, external_id):
	try:
		string = 'tvshow_external_id_%s_%s' % (external_source, external_id)
		url = '%s/find/%s?api_key=%s&external_source=%s' % (base_url, external_id, tmdb_api_key, external_source)
		result = cache_function(get_tmdb, string, url)
		result = result['tv_results']
		if result: return result[0]
		else: return None
	except: return None

def get_dates(days, reverse=True):
	current_date = get_current_date(return_str=False)
	if reverse: new_date = (current_date - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
	else: new_date = (current_date + datetime.timedelta(days=days)).strftime('%Y-%m-%d')
	return str(current_date), new_date

def get_current_date(return_str=True):
	if return_str: return str(datetime.date.today())
	else: return datetime.date.today()

def get_reviews_data(media_type, tmdb_id):
	def builder(media_type, tmdb_id):
		reviews_list, all_data = [], []
		template = '[B]%02d. %s%s[/B][CR][CR]%s'
		media_type = 'movie' if media_type in ('movie', 'movies') else 'tv'
		function = tmdb_movies_reviews if media_type  == 'movie' else tmdb_tv_reviews
		next_page, total_pages = 1, 1
		while next_page <= total_pages:
			data = function(tmdb_id, next_page)
			all_data += data['results']
			total_pages = data['total_pages']
			next_page = data['page'] + 1
		if all_data:
			for count, item in enumerate(all_data, 1):
				try:
					user = item['author'].upper()
					rating = item['author_details'].get('rating')
					if rating: rating = ' - %s/10' % str(rating).split('.')[0]
					else: rating = ''
					content = template % (count, user, rating, item['content'])
					reviews_list.append(content)
				except: pass
		return reviews_list
	string, url = 'tmdb_%s_reviews_%s' % (media_type ,tmdb_id), [media_type, tmdb_id]
	return cache_object(builder, string, url, json=False, expiration=EXPIRY_1_WEEK)

def get_data(url):
	data = get_tmdb(url).json()
	data['results'] = [remove_keys(i, tmdb_dict_removals) for i in data['results']]
	return data

def get_tmdb(url):
	try: response = session.get(url, timeout=timeout)
	except: response = None
	return response
