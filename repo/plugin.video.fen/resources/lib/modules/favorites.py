# -*- coding: utf-8 -*-
from caches.favorites import favorites
from modules.settings import ignore_articles, paginate, page_limit
from modules.utils import sort_for_article, paginate_list
# from modules.kodi_utils import logger

def get_favorites(media_type, page_no):
	data = favorites.get_favorites(media_type)
	data = sort_for_article(data, 'title', ignore_articles())
	original_list = [{'media_id': i['tmdb_id'], 'title': i['title']} for i in data]
	if paginate(): final_list, all_pages, total_pages = paginate_list(original_list, page_no, page_limit())
	else: final_list, all_pages, total_pages = original_list, [], 1
	return final_list, all_pages, total_pages


