# -*- coding: utf-8 -*-
from windows import BaseDialog
from modules.kodi_utils import json, local_string as ls
# from modules.kodi_utils import logger

class Select(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = 2025
		self.kwargs = kwargs
		self.enumerate = self.kwargs.get('enumerate', 'false')
		self.multi_choice = self.kwargs.get('multi_choice', 'false')
		self.multi_line = self.kwargs.get('multi_line', 'false')
		self.preselect = self.kwargs.get('preselect', [])
		self.items = json.loads(self.kwargs['items'])
		self.heading = self.kwargs.get('heading', ls(32036))
		self.media_type = self.kwargs.get('media_type', '')
		self.enable_context_menu = self.kwargs.get('enable_context_menu', 'false') == 'true'
		self.item_list = []
		self.chosen_indexes = []
		self.append = self.chosen_indexes.append
		self.selected = None
		self.set_properties()
		self.make_menu()

	def onInit(self):
		self.win = self.getControl(self.window_id)
		self.win.addItems(self.item_list)
		if self.preselect:
			for index in self.preselect:
				self.item_list[index].setProperty('check_status', 'checked')
				self.append(index)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		self.clearProperties()
		return self.selected

	def onClick(self, controlID):
		if controlID == 10:
			self.selected = sorted(self.chosen_indexes)
			self.close()
		elif controlID == 11:
			self.close()

	def onAction(self, action):
		chosen_listitem = self.get_listitem(self.window_id)
		if action in self.selection_actions:
			position = self.get_position(self.window_id)
			if self.multi_choice == 'true':
				if chosen_listitem.getProperty('check_status') == 'checked':
					chosen_listitem.setProperty('check_status', '')
					self.chosen_indexes.remove(position)
				else:
					chosen_listitem.setProperty('check_status', 'checked')
					self.append(position)
			else:
				self.selected = position
				return self.close()
		elif action in self.context_actions:
			if self.enable_context_menu:
				choice = self.open_window(('windows.select_ok', 'SelectContextMenu'), 'contextmenu.xml',
										list_item=chosen_listitem, context_menu_type='imdb_keywords', media_type=self.media_type)
			else: return self.close()
			if choice: self.execute_code(choice)
		elif action in self.closing_actions:
			return self.close()

	def make_menu(self):
		def builder():
			for count, item in enumerate(self.items, 1):
				listitem = self.make_listitem()
				if enum: line1 = '%02d. %s' % (count, item['line1'])
				else: line1 = item['line1']
				if 'line2' in item: line2 = item['line2']
				else: line2 = ''
				if 'icon' in item: listitem.setProperty('icon', item['icon'])
				else: listitem.setProperty('default_icon', 'true')
				listitem.setProperty('line1', line1)
				listitem.setProperty('line2', line2)
				yield listitem
		enum = self.enumerate == 'true'
		self.item_list = list(builder())

	def set_properties(self):
		self.setProperty('multi_choice', self.multi_choice)
		self.setProperty('multi_line', self.multi_line)
		self.setProperty('heading', self.heading)

class Confirm(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.ok_label = kwargs['ok_label']
		self.cancel_label = kwargs['cancel_label']
		self.text = kwargs['text']
		self.heading = kwargs['heading']
		self.default_control = kwargs['default_control']
		self.selected = None

	def onInit(self):
		self.set_properties()
		self.setFocusId(self.default_control)

	def run(self):
		self.doModal()
		return self.selected

	def onClick(self, controlID):
		if controlID == 10: self.selected = True
		elif controlID == 11: self.selected = False
		self.close()

	def onAction(self, action):
		if action in self.closing_actions: self.close()

	def set_properties(self):
		self.setProperty('ok_label', self.ok_label)
		self.setProperty('cancel_label', self.cancel_label)
		self.setProperty('text', self.text)
		self.setProperty('heading', self.heading)

class OK(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.ok_label = kwargs.get('ok_label')
		self.text = kwargs['text']
		self.heading = kwargs['heading']

	def onInit(self):
		self.set_properties()

	def run(self):
		self.doModal()

	def onClick(self, controlID):
		self.close()

	def onAction(self, action):
		if action in self.closing_actions:
			self.close()

	def set_properties(self):
		self.setProperty('ok_label', self.ok_label)
		self.setProperty('text', self.text)
		self.setProperty('heading', self.heading)

class SelectContextMenu(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = 2020
		self.kwargs = kwargs
		self.list_item = self.kwargs['list_item']
		self.context_menu_type = self.kwargs['context_menu_type']
		self.media_type = self.kwargs.get('media_type', '')
		self.item_list = []
		self.selected = None
		self.make_menu()

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
		elif action in self.context_actions:
			return self.close()
		elif action in self.closing_actions:
			return self.close()

	def make_menu(self):
		if self.context_menu_type == 'imdb_keywords':
			mode = 'build_movie_list' if self.media_type == 'movies' else 'build_tvshow_list'
			keyword = self.list_item.getProperty('line1')
			menu_item = json.dumps({'mode': mode, 'action': 'imdb_keywords_list_contents', 'iconImage': 'imdb', 'list_id': keyword.lower()})
			add_external_params = {'mode': 'menu_editor.add_external', 'name': '%s (IMDb)' % keyword.upper(), 'iconImage': 'imdb', 'menu_item': menu_item}
			add_shortcut_folder_params = {'mode': 'menu_editor.shortcut_folder_add_item', 'name': '%s (IMDb)' % keyword.upper(), 'iconImage': 'imdb', 'menu_item': menu_item}
			self.item_list.append(self.make_contextmenu_item(ls(32730), 'RunPlugin(%s)', add_external_params))
			self.item_list.append(self.make_contextmenu_item(ls(32731), 'RunPlugin(%s)', add_shortcut_folder_params))
