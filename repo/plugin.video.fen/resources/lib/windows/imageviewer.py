# -*- coding: utf-8 -*-
from apis.tmdb_api import tmdb_popular_people
from windows import BaseDialog
from indexers.people import person_data_dialog
from modules.settings import download_directory
from modules.kodi_utils import json, addon_fanart, item_next, local_string as ls
# from modules.kodi_utils import logger

nextpage_str = ls(32799)

class ThumbImageViewer(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = 2000
		self.current_page = 1
		self.selected = None
		self.list_items = kwargs.get('list_items')
		self.next_page_params = kwargs.get('next_page_params')
		self.ImagesInstance = kwargs.get('ImagesInstance')

	def onInit(self):
		self.make_page()

	def run(self):
		self.doModal()
		self.clearProperties()

	def onAction(self, action):
		if action in self.closing_actions:
			if self.current_page == 1: return self.close()
			return self.previous_page()
		try:
			position = self.get_position(self.window_id)
			chosen_listitem = self.get_listitem(self.window_id)
		except: return
		if action in self.selection_actions:
			if chosen_listitem.getProperty('next_page_item') == 'true': self.new_page()
			else:
				thumb_params = chosen_listitem.getProperty('action')
				thumb_params = json.loads(thumb_params)
				if thumb_params['mode'] == 'slideshow_image':
					thumb_params['current_index'] = position
					ending_position = self.ImagesInstance.run(thumb_params)
					self.win.selectItem(ending_position)
				elif thumb_params['mode'] == 'person_data_dialog':
					person_data_dialog({'query': thumb_params['actor_name']})
		elif action in self.context_actions:
			choice = self.open_window(('windows.imageviewer', 'ThumbContextMenu'), 'contextmenu.xml', list_item=chosen_listitem)
			if choice:
				if 'delete_image' in choice: self.reset_after_delete(choice, position)
				else: self.execute_code(choice)

	def make_page(self):
		try:
			self.set_properties()
			if self.next_page_params.get('page_no', 'final_page') != 'final_page': self.make_next_page()
			self.win = self.getControl(self.window_id)
			self.win.addItems(self.list_items)
			self.setFocusId(self.window_id)
		except: pass

	def new_page(self):
		try:
			self.current_page += 1
			self.next_page_params['in_progress'] = 'true'
			self.list_items, self.next_page_params = self.ImagesInstance.run(self.next_page_params)
			self.win.reset()
			self.make_page()
		except: self.close()

	def previous_page(self):
		try:
			self.current_page -= 1
			self.next_page_params['page_no'] = self.current_page
			self.next_page_params['in_progress'] = 'true'
			self.list_items, self.next_page_params = self.ImagesInstance.run(self.next_page_params)
			self.win.reset()
			self.make_page()
		except: self.close()

	def make_next_page(self):
		try:
			listitem = self.make_listitem()
			listitem.setProperty('name', nextpage_str % str(self.current_page + 1))
			listitem.setProperty('thumb', item_next)
			listitem.setProperty('next_page_item', 'true')
			self.list_items.append(listitem)
		except: pass

	def reset_after_delete(self, choice, position):
		self.set_home_property('delete_image_finished', 'false')
		self.execute_code(choice)
		while not self.get_home_property('delete_image_finished') == 'true': self.sleep(10)
		self.win.reset()
		self.list_items = self.ImagesInstance.browser_image(download_directory('image'), return_items=True)
		self.make_page()
		self.win.selectItem(position)

	def set_properties(self):
		self.setProperty('page_no', str(self.current_page))
		self.setProperty('fanart', addon_fanart)

class ThumbContextMenu(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = 2020
		self.list_item = kwargs['list_item']
		self.item_list = []
		self.selected = None
		self.make_context_menu()

	def onInit(self):
		win = self.getControl(self.window_id)
		win.addItems(self.item_list)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		return self.selected

	def onAction(self, action):
		if action in self.selection_actions:
			chosen_listitem = self.get_listitem(self.window_id)
			self.selected = chosen_listitem.getProperty('action')
			return self.close()
		if action in self.context_actions:
			return self.close()
		if action in self.closing_actions:
			return self.close()

	def make_context_menu(self):
		enable_delete = self.list_item.getProperty('delete') == 'true'
		path = self.list_item.getProperty('path')
		thumb = self.list_item.getProperty('thumb')
		if enable_delete:
			delete_file_params = {'mode': 'delete_image', 'image_url': path, 'thumb_url': thumb}#, 'in_progress': 'true'}
			self.item_list.append(self.make_contextmenu_item('[B]%s[/B]' % ls(32785), 'RunPlugin(%s)', delete_file_params))
		else:
			name = self.list_item.getProperty('name')
			down_file_params = {'mode': 'downloader', 'action': 'image', 'name': name, 'thumb_url': thumb, 'image_url': path, 'media_type': 'image', 'image': thumb}
			self.item_list.append(self.make_contextmenu_item(ls(32747), 'RunPlugin(%s)', down_file_params))

class SlideShow(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = 5000
		self.all_images = kwargs.get('all_images')
		self.index = kwargs.get('index')
		self.set_properties()
		self.make_items()

	def onInit(self):
		self.win = self.getControl(self.window_id)
		self.win.addItems(self.item_list)
		self.win.selectItem(self.index)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		return self.position

	def onAction(self, action):
		if action in self.closing_actions:
			self.position = self.get_position(self.window_id)
			self.close()

	def make_items(self):
		def builder():
			for item in self.all_images:
				try:
					listitem = self.make_listitem()
					listitem.setProperty('image', item[0])
					listitem.setProperty('title', item[1])
					yield listitem
				except: pass
		self.item_list = list(builder())

	def set_properties(self):
		self.setProperty('fanart', addon_fanart)
