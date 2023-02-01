# -*- coding: utf-8 -*-
from windows import BaseDialog
from modules.meta_lists import colors
# from modules.kodi_utils import logger

button_ids = (10, 11)

class SelectColor(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.kwargs = kwargs
		self.default_setting = self.kwargs.get('default_setting')
		self.window_id = 2000
		self.selected = None
		self.start_index = 0
		self.palette_location = self.translate_path('special://profile/addon_data/plugin.video.fen/color_palette/')
		self.texture_location = self.palette_location + '%s.png'
		self.palette_status = self.palette_check()
		self.make_menu()

	def palette_check(self):
		if self.path_exists(self.palette_location): status = True
		else:
			self.notification(33110)
			from modules.utils import download_color_palette
			status = download_color_palette(self.palette_location)
		return status

	def onInit(self):
		if not self.palette_status:
			self.notification(33111, duration=5000)
			self.close()
		self.win = self.getControl(self.window_id)
		self.win.addItems(self.item_list)
		self.setFocusId(self.window_id)
		self.win.selectItem(self.start_index)

	def run(self):
		self.doModal()
		self.clearProperties()
		return self.selected

	def onAction(self, action):
		if action in self.closing_actions: self.setFocusId(11)
		elif action in self.selection_actions:
			focus_id = self.getFocusId()
			if focus_id == 2000:
				chosen_listitem = self.get_listitem(self.window_id)
				self.selected = chosen_listitem.getProperty('label')
				self.setFocusId(10)
			elif focus_id == 10: self.close()
			else:
				self.selected = None
				self.close()

	def make_menu(self):
		def builder():
			for count, item in enumerate(colors):
				try:
					listitem = self.make_listitem()
					listitem.setProperty('label', item)
					listitem.setProperty('image', self.texture_location % item)
					if item == self.default_setting: self.start_index = count
					yield listitem
				except: pass
		if self.palette_status: self.item_list = list(builder())
