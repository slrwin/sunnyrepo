# -*- coding: utf-8 -*-
from windows.base_window import BaseDialog, ok_dialog
from modules.kodi_utils import unzip, colorpalette_path, colorpalette_zip_path, userdata_path
from modules.meta_lists import color_palette
from modules.kodi_utils import dialog, path_join
# from modules.kodi_utils import logger

class SelectColor(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, *args)
		self.kwargs = kwargs
		self.current_setting = self.kwargs.get('current_setting')
		self.window_id = 2000
		self.selected = None
		self.texture_location = path_join(colorpalette_path, '%s.png')
		self.make_menu()

	def onInit(self):
		palette_status = self.palette_check()
		if palette_status == 'failed':
			self.notification('Color Palette Folder not Found. Please Report this Issue', duration=5000)
			self.close()
		self.add_items(self.window_id, self.item_list)
		if palette_status == 'fresh_install': self.sleep(2000)
		self.setFocusId(self.window_id)
		self.select_item(self.window_id, 0)

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
				self.current_setting = chosen_listitem.getProperty('label')
				self.selected = self.current_setting
				self.setFocusId(10)
			elif focus_id == 10: self.close()
			elif focus_id == 11:
				self.selected = None
				self.close()
			else:
				color_value = self.color_input()
				if not color_value: return
				self.current_setting = color_value
				self.selected = self.current_setting
				self.close()

	def make_menu(self):
		def builder():
			for count, item in enumerate(color_palette):
				try:
					listitem = self.make_listitem()
					listitem.setProperties({'label': item, 'image': self.texture_location % item})
					yield listitem
				except: pass
		self.item_list = list(builder())

	def palette_check(self):
		if self.path_exists(colorpalette_path): palette_status = 'exists'
		else:
			self.busy_dialog()
			install_status = unzip(colorpalette_zip_path, userdata_path, colorpalette_path, False)
			self.busy_dialog('false')
			if install_status: palette_status = 'fresh_install'
			else: palette_status = 'failed'
		return palette_status

	def color_input(self):
		color_value = dialog.input('Enter Highight Color Value', defaultt=self.current_setting)
		if not color_value: return None
		color_value = color_value.upper()
		if not color_value.isalnum() or not color_value.startswith('FF') or not len(color_value) == 8:
			ok_dialog(text='Value must begin with [B]FF[/B], be [B]8[/B] characters in length and be [B]Alphanumeric[/B].[CR][CR]Please try again..')
			return self.color_input()
		return color_value

	def busy_dialog(self, state='true'):
		self.setProperty('show_busy_dialog', state)
