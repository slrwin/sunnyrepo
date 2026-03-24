# -*- coding: utf-8 -*-
import re
import json
import requests
from caches.base_cache import connect_database
from caches.main_cache import cache_object
from caches.settings_cache import get_setting
from modules.dom_parser import parseDOM
from modules.kodi_utils import sleep
from modules.utils import remove_accents, replace_html_codes, normalize
# from modules.kodi_utils import logger

GQL_URL  = 'https://graphql.imdb.com/'
GQL_HEADERS = {
	'Content-Type': 'application/json',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
	'Accept': 'application/json', 'Origin': 'https://www.imdb.com', 'Referer': 'https://www.imdb.com/',
	'x-imdb-client-name': 'imdb-web-next-localized', 'x-imdb-user-language': 'en-US', 'x-imdb-user-country': 'US'}

def _gql(query, variables=None):
	try:
		payload = {'query': query}
		if variables: payload['variables'] = variables
		r = requests.post(GQL_URL, json=payload, headers=GQL_HEADERS, timeout=20)
		if r.status_code == 200: return r.json()
	except: pass
	return None

def _clean(text):
	if not text: return ''
	text = text.replace('<br/><br/>', '\n').replace('<br/>', '\n').replace('<br>', '\n')
	text = re.sub(r'<a[^>]*>', '', text).replace('</a>', '')
	text = re.sub(r'<[^>]+>', '', text)
	text = replace_html_codes(text)
	text = remove_accents(text)
	return text.strip()

def imdb_more_like_this(imdb_id):
	string = 'imdb_more_like_this_%s' % imdb_id
	params = {'action': 'imdb_more_like_this', 'imdb_id': imdb_id}
	return cache_object(get_imdb, string, params, False, 168)[0]

def imdb_people_id(actor_name):
	name = actor_name.lower()
	string = 'imdb_people_id_%s' % name
	url, url_backup = 'https://sg.media-imdb.com/suggests/%s/%s.json' % (name[0], name.replace(' ', '%20')), 'https://www.imdb.com/search/name/?name=%s' % name
	params = {'url': url, 'action': 'imdb_people_id', 'name': name, 'url_backup': url_backup}
	return cache_object(get_imdb, string, params, False, 8736)[0]

def imdb_reviews(imdb_id):
	string = 'imdb_reviews_%s' % imdb_id
	params = {'action': 'imdb_reviews', 'imdb_id': imdb_id}
	return cache_object(get_imdb, string, params, False, 168)[0]

def imdb_parentsguide(imdb_id):
	string = 'imdb_parentsguide_%s' % imdb_id
	params = {'action': 'imdb_parentsguide', 'imdb_id': imdb_id}
	return cache_object(get_imdb, string, params, False, 168)[0]

def imdb_trivia(imdb_id):
	string = 'imdb_trivia_%s' % imdb_id
	params = {'action': 'imdb_trivia', 'imdb_id': imdb_id}
	return cache_object(get_imdb, string, params, False, 168)[0]

def imdb_blunders(imdb_id):
	string = 'imdb_blunders_%s' % imdb_id
	params = {'action': 'imdb_blunders', 'imdb_id': imdb_id}
	return cache_object(get_imdb, string, params, False, 168)[0]

def imdb_people_trivia(imdb_id):
	string = 'imdb_people_trivia_%s' % imdb_id
	params = {'action': 'imdb_people_trivia', 'imdb_id': imdb_id}
	return cache_object(get_imdb, string, params, False, 168)[0]

def imdb_year_check(imdb_id):
	url = 'https://v2.sg.media-imdb.com/suggestion/t/%s.json' % imdb_id
	string = 'imdb_year_check%s' % imdb_id
	params = {'url': url, 'imdb_id': imdb_id, 'action': 'imdb_year_check'}
	return cache_object(get_imdb, string, params, False, 720)[0]

def get_imdb(params):
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
				'Accept-Language':'en-us,en;q=0.5'}
	imdb_list = []
	action = params.get('action')
	imdb_id = params.get('imdb_id', '')
	next_page = None
	if action == 'imdb_more_like_this':
		def _process():
			for edge in edges:
				try:
					_id = edge['node']['id']
					if _id.startswith('tt'): yield (_id)
				except: pass
		try:
			result = _gql('query($id:ID!){title(id:$id){moreLikeThisTitles(first:12){edges{node{id}}}}}', {'id': imdb_id})
			edges = result['data']['title']['moreLikeThisTitles']['edges']
		except: edges = []
		imdb_list = list(_process())
		imdb_list = [i for n, i in enumerate(imdb_list) if i not in imdb_list[n + 1:]]
	elif action in ('imdb_trivia', 'imdb_blunders'):
		def _process():
			for count, edge in enumerate(edges, 1):
				try:
					content = _clean(edge['node']['text']['plaidHtml'])
					content = '[B]%s %02d.[/B][CR][CR]%s' % (_str, count, content)
					yield content
				except: pass
		if action == 'imdb_trivia': _str, field = 'TRIVIA', 'trivia'
		else: _str, field = 'BLUNDERS', 'goofs'
		try:
			result = _gql('query($id:ID!){title(id:$id){%s(first:50){edges{node{text{plaidHtml}}}}}}' % field, {'id': imdb_id})
			edges = result['data']['title'][field]['edges']
		except: edges = []
		imdb_list = list(_process())
	elif action == 'imdb_people_trivia':
		def _process():
			for count, edge in enumerate(edges, 1):
				try:
					content = _clean(edge['node']['text']['plaidHtml'])
					content = '[B]%s %02d.[/B][CR][CR]%s' % (trivia_str, count, content)
					yield content
				except: pass
		trivia_str = 'TRIVIA'
		try:
			result = _gql('query($id:ID!){name(id:$id){trivia(first:50){edges{node{text{plaidHtml}}}}}}', {'id': imdb_id})
			edges = result['data']['name']['trivia']['edges']
		except: edges = []
		imdb_list = list(_process())
	elif action == 'imdb_reviews':
		def _process():
			count = 1
			for edge in edges:
				try:
					node = edge['node']
					try:
						text_obj = node.get('text') or {}
						orig_obj = text_obj.get('originalText') or {}
						if isinstance(orig_obj, dict):
							content = _clean(orig_obj.get('plaidHtml', ''))
						else:
							content = _clean(str(orig_obj))
					except: continue
					if not content: continue
					try: spoiler = node.get('spoiler', False)
					except: spoiler = False
					try:
						rating = node.get('authorRating')
						rating = str(rating) if rating is not None else '-'
					except: rating = '-'
					try:
						summary = node.get('summary') or {}
						if isinstance(summary, dict):
							title = _clean(summary.get('originalText', '')) or '-----'
						else:
							title = '-----'
					except: title = '-----'
					try: date = node.get('submissionDate', '-----')
					except: date = '-----'
					try: review = '[B]%02d. [I]%s/10 - %s - %s[/I][/B][CR][CR]%s' % (count, rating, date, title, content)
					except: continue
					if spoiler: review = '[B][COLOR red][%s][/COLOR][CR][/B]' % spoiler_str + review
					count += 1
					yield review
				except: pass
		spoiler_str = 'CONTAINS SPOILERS'
		edges = []
		for gql_field in ('featuredReviews', 'reviews'):
			try:
				query = 'query($id:ID!){title(id:$id){%s(first:50){edges{node{authorRating submissionDate spoiler summary{originalText}text{originalText{plaidHtml}}}}}}}' % gql_field
				result = _gql(query, {'id': imdb_id})
				edges = result['data']['title'][gql_field]['edges']
				if edges: break
			except: continue
		imdb_list = list(_process())
	elif action == 'imdb_people_id':
		try:
			name = params['name']
			result = requests.get(params['url'], timeout=20)
			results = json.loads(re.sub(r'imdb\$(.+?)\(', '', result.text)[:-1])['d']
			imdb_list = [i['id'] for i in results if i['id'].startswith('nm') and i['l'].lower() == name][0]
		except: imdb_list = []
		if not imdb_list:
			try:
				result = requests.get(params['url_backup'], timeout=20, headers=headers)
				result = remove_accents(result.text)
				result = result.replace('\n', ' ')
				result = parseDOM(result, 'div', attrs={'class': 'lister-item-image'})[0]
				imdb_list = re.search(r'href="/name/(.+?)"', result, re.DOTALL).group(1)
			except: pass
	elif action == 'imdb_year_check':
		try:
			result = requests.get(params['url'], timeout=5).json()
			imdb_list = [str(i['y']) for i in result['d'] if i['id'] == imdb_id][0]
		except: pass
	elif action == 'imdb_parentsguide':
		imdb_list = []
		imdb_append = imdb_list.append
		try:
			result = _gql('query($id:ID!){title(id:$id){parentsGuide{categories{category{id text}severity{text}guideItems(first:50){edges{node{isSpoiler text{plaidHtml}}}}}}}}',
						{'id': imdb_id})
			categories = result['data']['title']['parentsGuide']['categories']
		except: categories = []
		for cat in categories:
			item_dict = {}
			try: item_dict['title'] = cat['category']['text']
			except: continue
			try: item_dict['ranking'] = cat['severity']['text']
			except: item_dict['ranking'] = 'none'
			try:
				listings = []
				for edge in cat.get('guideItems', {}).get('edges', []):
					text = _clean(edge.get('node', {}).get('text', {}).get('plaidHtml', ''))
					if text: listings.append(text)
			except: listings = []
			if listings:
				item_dict['content'] = '\n\n'.join(['%02d. %s' % (count, i) for count, i in enumerate(listings, 1)])
			elif item_dict['ranking'] == 'none': continue
			item_dict['total_count'] = len(listings)
			if item_dict: imdb_append(item_dict)
	return (imdb_list, next_page)

def clear_imdb_cache(silent=False):
	try:
		dbcon = connect_database('maincache_db')
		results = dbcon.execute("SELECT id FROM maincache WHERE id LIKE ?", ('imdb_%',)).fetchall()
		dbcon.execute("DELETE FROM maincache WHERE id LIKE ?", ('imdb_%',))
		return True
	except: return False

def refresh_imdb_meta_data(imdb_id):
	try:
		insert1, insert2 = '%%%s' % imdb_id, '%%%s_%%' % imdb_id
		dbcon = connect_database('maincache_db')
		dbcon.execute("DELETE FROM maincache WHERE id LIKE ?", (insert1,))
		dbcon.execute("DELETE FROM maincache WHERE id LIKE ?", (insert2,))
		return True
	except: return False