# -*- coding: utf-8 -*-
import os
from apis.tmdb_api import tmdb_people_info
from windows import open_window
from indexers.images import Images
from modules import kodi_utils
# logger = kodi_utils.logger

json, select_dialog, dialog, show_busy_dialog, hide_busy_dialog = kodi_utils.json, kodi_utils.select_dialog, kodi_utils.dialog, kodi_utils.show_busy_dialog, kodi_utils.hide_busy_dialog
notification, get_icon, unquote, kodi_refresh, ls = kodi_utils.notification, kodi_utils.get_icon, kodi_utils.unquote, kodi_utils.kodi_refresh, kodi_utils.local_string
tmdb_image_url = 'https://image.tmdb.org/t/p/h632/%s'
default_image = get_icon('genre_family')

def popular_people():
	Images().run({'mode': 'popular_people_image_results', 'page_no': 1})

def person_data_dialog(params):
	if 'query' in params: query = unquote(params['query'])
	else: query = None
	open_window(('windows.people', 'People'), 'people.xml', query=query, actor_name=params.get('actor_name'), actor_image=params.get('actor_image'),
				actor_id=params.get('actor_id'), is_widget=params.get('is_widget', 'false'))

def person_search(query=None, window_xml='select.xml'):
	show_busy_dialog()
	query = unquote(query)
	try: people = tmdb_people_info(query)
	except: pass
	hide_busy_dialog()
	if not people: return notification(ls(32760))
	if len(people) == 1:
		person = people[0]
		actor_id, actor_name = person['id'], person['name']
		try: image_id = person['profile_path']
		except: image_id = None
		if not image_id: actor_image = default_image
		else: actor_image = tmdb_image_url % image_id
	else:
		def _builder():
			for item in people:
				known_for_list = [i.get('title', 'NA') for i in item['known_for']]
				known_for_list = [i for i in known_for_list if not i == 'NA']
				image = tmdb_image_url % item['profile_path'] if item['profile_path'] else default_image
				yield {'line1': item['name'], 'line2': ', '.join(known_for_list) if known_for_list else '', 'icon': image}
		list_items = list(_builder())
		kwargs = {'items': json.dumps(list_items), 'heading': ls(32036), 'multi_line': 'true', 'window_xml': window_xml}
		person = select_dialog(people, **kwargs)
		if person == None: return None, None, None
		actor_id = int(person['id'])
		actor_name = person['name']
		actor_image = tmdb_image_url % person['profile_path'] if person['profile_path'] else default_image
	if not actor_name: return
	return person_data_dialog({'actor_name': actor_name, 'actor_image': actor_image, 'actor_id': actor_id})



