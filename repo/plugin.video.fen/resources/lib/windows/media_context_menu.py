# -*- coding: utf-8 -*-
from windows import BaseDialog
from modules.kodi_utils import json, local_string as ls
# from modules.kodi_utils import logger

class ContextMenu(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = 2025
		self.kwargs = kwargs
		self.items = json.loads(self.kwargs['items'])
		self.heading = self.kwargs.get('heading', ls(32036))
		self.media_type = self.kwargs.get('media_type', '')
		self.multi_line = self.kwargs.get('multi_line', 'false')
		self.item_list = []
		self.selected = None
		self.set_properties()
		self.make_menu()

	def onInit(self):
		self.win = self.getControl(self.window_id)
		self.win.addItems(self.item_list)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		self.clearProperties()
		return self.selected

	def onAction(self, action):
		if action in self.selection_actions:
			self.selected = self.get_position(self.window_id)
			return self.close()
		elif action in self.context_actions: return self.close()
		elif action in self.closing_actions: return self.close()

	def make_menu(self):
		def builder():
			for item in self.items:
				listitem = self.make_listitem()
				line1 = item['line1']
				if 'line2' in item: line2 = item['line2']
				else: line2 = ''
				if 'icon' in item: listitem.setProperty('icon', item['icon'])
				else: listitem.setProperty('default_icon', 'true')
				listitem.setProperty('line1', line1)
				listitem.setProperty('line2', line2)
				yield listitem
		self.item_list = list(builder())

	def set_properties(self):
		self.setProperty('heading', self.heading)
		self.setProperty('multi_line', self.multi_line)
