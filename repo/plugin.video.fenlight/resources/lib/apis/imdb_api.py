# -*- coding: utf-8 -*-
import re
import json
import requests
from caches.base_cache import connect_database
from caches.main_cache import cache_object
from caches.settings_cache import get_setting
from modules.dom_parser import parseDOM
from modules.kodi_utils import sleep
from modules.utils import remove_accents, replace_html_codes
from modules.kodi_utils import logger

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Firefox/102.0'}
base_url = 'https://www.imdb.com/%s'
more_like_this_url = 'title/%s'
reviews_url = 'title/%s/reviews/_ajax?paginationKey=%s'
trivia_url = 'title/%s/trivia'
blunders_url = 'title/%s/goofs'
parentsguide_url = 'title/%s/parentalguide'
images_url = 'title/%s/mediaindex?page=%s'
people_images_url = 'name/%s/mediaindex?page=%s'
people_trivia_url = 'name/%s/trivia'
people_search_url_backup = 'search/name/?name=%s'
people_search_url = 'https://sg.media-imdb.com/suggests/%s/%s.json'
timeout = 20.0

def imdb_more_like_this(imdb_id):
	url = base_url % more_like_this_url % imdb_id
	string = 'imdb_more_like_this_%s' % imdb_id
	params = {'url': url, 'action': 'imdb_more_like_this', 'imdb_id': imdb_id}
	return cache_object(get_imdb, string, params, False, 168)[0]

def imdb_people_id(actor_name):
	name = actor_name.lower()
	string = 'imdb_people_id_%s' % name
	url, url_backup = people_search_url % (name[0], name.replace(' ', '%20')), base_url % people_search_url_backup % name
	params = {'url': url, 'action': 'imdb_people_id', 'name': name, 'url_backup': url_backup}
	return cache_object(get_imdb, string, params, False, 8736)[0]

def imdb_reviews(imdb_id):
	url = base_url % reviews_url % (imdb_id, '')
	string = 'imdb_reviews_%s' % imdb_id
	params = {'url': url, 'action': 'imdb_reviews', 'imdb_id': imdb_id}
	return cache_object(get_imdb, string, params, False, 168)[0]

def imdb_parentsguide(imdb_id):
	url = base_url % parentsguide_url % imdb_id
	string = 'imdb_parentsguide_%s' % imdb_id
	params = {'url': url, 'action': 'imdb_parentsguide'}
	return cache_object(get_imdb, string, params, False, 168)[0]

def imdb_trivia(imdb_id):
	url = base_url % trivia_url % imdb_id
	string = 'imdb_trivia_%s' % imdb_id
	params = {'url': url, 'action': 'imdb_trivia'}
	return cache_object(get_imdb, string, params, False, 168)[0]

def imdb_blunders(imdb_id):
	url = base_url % blunders_url % imdb_id
	string = 'imdb_blunders_%s' % imdb_id
	params = {'url': url, 'action': 'imdb_blunders'}
	return cache_object(get_imdb, string, params, False, 168)[0]

def imdb_people_trivia(imdb_id):
	url = base_url % people_trivia_url % imdb_id
	string = 'imdb_people_trivia_%s' % imdb_id
	params = {'url': url, 'action': 'imdb_people_trivia'}
	return cache_object(get_imdb, string, params, False, 168)[0]

def get_imdb(params):
	imdb_list = []
	action = params.get('action')
	url = params.get('url')
	next_page = None
	if action == 'imdb_more_like_this':
		def _process():
			for item in items:
				try:
					_id = item.split('href="/title/')[1].split('/?ref_')[0]
					if _id.replace('tt','').isnumeric(): yield (_id)
				except: pass
		try:
			result = requests.get(url, timeout=timeout, headers=headers).text
			result = result.split('<span>Storyline</span>')[0].split('<span>More like this</span>')[1]
			items = str(result).split('poster-card__title--clickable" aria-label="')
		except: items = []
		imdb_list = list(_process())
		imdb_list = [i for n, i in enumerate(imdb_list) if i not in imdb_list[n + 1:]] # remove duplicates
	if action in ('imdb_trivia', 'imdb_blunders'):
		def _process():
			for count, item in enumerate(items, 1):
				try:
					content = re.sub(r'<a class="ipc-md-link ipc-md-link--entity" href="\S+">', '', item).replace('</a>', '')
					content = replace_html_codes(content)
					content = content.replace('<br/><br/>', '\n')
					content = '[B]%s %02d.[/B][CR][CR]%s' % (_str, count, content)
					yield content
				except: pass
		if action == 'imdb_trivia': _str = 'TRIVIA'
		else: _str =  'BLUNDERS'
		result = requests.get(url, timeout=timeout, headers=headers)
		result = remove_accents(result.text)
		result = result.replace('\n', ' ')
		items = parseDOM(result, 'div', attrs={'class': 'ipc-html-content-inner-div'})
		imdb_list = list(_process())
	elif action == 'imdb_people_trivia':
		def _process():
			for count, item in enumerate(items, 1):
				try:
					content = re.sub(r'<a href=".+?">', '', item).replace('</a>', '').replace('<p> ', '').replace('<br />', '').replace('  ', '')
					content = re.sub(r'<a class=".+?">', '', item).replace('</a>', '').replace('<p> ', '').replace('<br />', '').replace('  ', '')
					content = replace_html_codes(content)
					content = '[B]%s %02d.[/B][CR][CR]%s' % (trivia_str, count, content)
					yield content
				except: pass
		trivia_str = 'TRIVIA'
		result = requests.get(url, timeout=timeout, headers=headers)
		result = remove_accents(result.text)
		result = result.replace('\n', ' ')
		items = parseDOM(result, 'div', attrs={'class': 'ipc-html-content-inner-div'})
		imdb_list = list(_process())
	elif action == 'imdb_reviews':
		def _process():
			for count, listing in enumerate(all_reviews, 1):
				try:
					try: spoiler = listing['spoiler']
					except: spoiler = False
					try: listing = listing['content']
					except: continue
					try:
						content = parseDOM(listing, 'div', attrs={'class': 'text show-more__control'})[0]
						content = replace_html_codes(content)
					except: continue
					try: title = parseDOM(listing, 'a', attrs={'class': 'title'})[0]
					except: title = ''
					try: date = parseDOM(listing, 'span', attrs={'class': 'review-date'})[0]
					except: date = ''
					try:
						rating = parseDOM(listing, 'span', attrs={'class': 'rating-other-user-rating'})
						rating = parseDOM(rating, 'span')
						rating = rating[0] + rating[1]
					except: rating = ''
					review = '[B]%02d. [I]%s - %s - %s[/I][/B][CR][CR]%s' % (count, rating, date, title, content)
					if spoiler: review = '[B][COLOR red][%s][/COLOR][CR][/B]' % spoiler_str + review
					yield review
				except: pass
		spoiler_str = 'CONTAINS SPOILERS'
		imdb_id = params['imdb_id']
		paginationKey = ''
		non_spoiler_list = []
		spoiler_list = []
		count = 0
		result = requests.get(url, timeout=timeout)
		while count < 3:
			if count > 0:
				url = base_url % reviews_url % (imdb_id, paginationKey)
				result = requests.get(url, timeout=timeout)
			result = remove_accents(result.text)
			result = result.replace('\n', ' ')
			non_spoilers = parseDOM(result, 'div', attrs={'class': 'lister-item mode-detail imdb-user-review  collapsable'})
			spoilers = parseDOM(result, 'div', attrs={'class': 'lister-item mode-detail imdb-user-review  with-spoiler'})
			non_spoiler_list.extend([{'spoiler': False, 'content': i} for i in non_spoilers])
			spoiler_list.extend([{'spoiler': True, 'content': i} for i in spoilers])
			try: paginationKey = re.search(r'data-key="(.+?)"', result, re.DOTALL).group(1)
			except: break
			count += 1
		all_reviews = non_spoiler_list + spoiler_list
		imdb_list = list(_process())
	elif action == 'imdb_people_id':
		try:
			name = params['name']
			result = requests.get(url, timeout=timeout)
			results = json.loads(re.sub(r'imdb\$(.+?)\(', '', result.text)[:-1])['d']
			imdb_list = [i['id'] for i in results if i['id'].startswith('nm') and i['l'].lower() == name][0]
		except: imdb_list = []
		if not imdb_list:
			try:
				result = requests.get(params['url_backup'], timeout=timeout)
				result = remove_accents(result.text)
				result = result.replace('\n', ' ')
				result = parseDOM(result, 'div', attrs={'class': 'lister-item-image'})[0]
				imdb_list = re.search(r'href="/name/(.+?)"', result, re.DOTALL).group(1)
			except: pass
	elif action == 'imdb_parentsguide':
		spoiler_results = None
		spoiler_list, final_list = [], []
		spoiler_append, final_list_append, imdb_append = spoiler_list.append, final_list.append, imdb_list.append
		tester, count, result = '', 0, []
		while count <= 2:
			tester = requests.get(url, timeout=timeout, headers=headers)
			if not 'opengraphprotocol' in tester:
				result = tester
				result = remove_accents(result.text)
				result = result.replace('\n', ' ')
				break
			count += 1
			sleep(100)
		if not result:
			logger('Parentsguide', 'All opengraphprotocol results')
			return result, 0
		try:
			results = parseDOM(result, 'section', attrs={'id': r'advisory-(.+?)'})
			spoiler_results = parseDOM(result, 'section', attrs={'id': 'advisory-spoilers'})[0]
		except: pass
		if spoiler_results:
			results = [i for i in results if not i in spoiler_results]
			spoiler_results = spoiler_results.split('<h4 class="ipl-list-title">')[1:]
			for item in spoiler_results:
				item_dict = {}
				try:
					title = replace_html_codes(re.search(r'(.+?)</h4>', item, re.DOTALL).group(1))
					item_dict['title'] = title
				except: continue
				try:
					listings = parseDOM(item, 'li', attrs={'class': 'ipl-zebra-list__item'})
					item_dict['listings'] = []
				except: continue
				dict_listings_append = item_dict['listings'].append
				for item in listings:
					try:
						listing = replace_html_codes(re.search(r'(.+?)     <div class="', item, re.DOTALL).group(1))
						if not listing in item_dict['listings']: dict_listings_append(listing)
					except: pass
				if not item_dict in spoiler_list: spoiler_append(item_dict)
		for item in results:
			item_dict = {}
			try:
				title = replace_html_codes(parseDOM(item, 'h4', attrs={'class': 'ipl-list-title'})[0])
				item_dict['title'] = title
			except: continue
			try:
				ranking = replace_html_codes(parseDOM(item, 'span', attrs={'class': 'ipl-status-pill ipl-status-pill--(.+?)'})[0])
				item_dict['ranking'] = ranking
			except: item_dict['ranking'] = 'none'
			try:
				listings = parseDOM(item, 'li', attrs={'class': 'ipl-zebra-list__item'})
				item_dict['listings'] = []
			except: pass
			if listings:
				dict_listings_append = item_dict['listings'].append
				for item in listings:
					try:
						listing = replace_html_codes(re.search(r'(.+?)     <div class="', item, re.DOTALL).group(1))
						if not listing in item_dict['listings']: dict_listings_append(listing)
					except: pass
			elif item_dict['ranking'] == 'none': continue
			if item_dict: final_list_append(item_dict)
		if spoiler_list:
			for imdb in imdb_list:
				for spo in spoiler_list:
					if spo['title'] == imdb['title']:
						imdb['listings'].extend(spo['listings'])
		for item in final_list:
			new_dict = {}
			listings = list(set(item['listings']))
			item['listings'] = list(set(item['listings']))
			new_dict['title'] = item['title']
			new_dict['ranking'] = item['ranking']
			new_dict['content'] = '\n\n'.join(['%02d. %s' % (count, i) for count, i in enumerate(listings, 1)])
			new_dict['total_count'] = len(listings)
			imdb_append(new_dict)
	return (imdb_list, next_page)

def clear_imdb_cache(silent=False):
	from modules.kodi_utils import clear_property
	try:
		dbcon = connect_database('maincache_db')
		imdb_results = [str(i[0]) for i in dbcon.execute("SELECT id FROM maincache WHERE id LIKE ?", ('imdb_%',)).fetchall()]
		if not imdb_results: return True
		dbcon.execute("DELETE FROM maincache WHERE id LIKE ?", ('imdb_%',))
		for i in imdb_results: clear_property(i)
		return True
	except: return False

def refresh_imdb_meta_data(imdb_id):
	from modules.kodi_utils import clear_property
	try:
		imdb_results = []
		insert1, insert2 = '%%_%s' % imdb_id, '%%_%s_%%' % imdb_id
		dbcon = connect_database('maincache_db')
		for item in (insert1, insert2):
			imdb_results += [str(i[0]) for i in dbcon.execute("SELECT id FROM maincache WHERE id LIKE ?", (item,)).fetchall()]
		if not imdb_results: return True
		dbcon.execute("DELETE FROM maincache WHERE id LIKE ?", (insert1,))
		dbcon.execute("DELETE FROM maincache WHERE id LIKE ?", (insert2,))
		for i in imdb_results: clear_property(i)
	except: pass
