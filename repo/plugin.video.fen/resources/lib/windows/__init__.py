# -*- coding: utf-8 -*-
import re
from xml.dom.minidom import parse as mdParse
from modules import kodi_utils
from modules.settings import skin_location, use_skin_fonts
from modules.utils import manual_function_import

closing_actions, selection_actions, context_actions = kodi_utils.window_xml_closing_actions, kodi_utils.window_xml_selection_actions, kodi_utils.window_xml_context_actions
build_url, execute_builtin, set_property, get_property = kodi_utils.build_url, kodi_utils.execute_builtin, kodi_utils.set_property, kodi_utils.get_property
translate_path, get_infolabel, list_dirs, current_skin = kodi_utils.translate_path, kodi_utils.get_infolabel, kodi_utils.list_dirs, kodi_utils.current_skin
current_skin_prop, use_skin_fonts_prop, addon_installed = kodi_utils.current_skin_prop, kodi_utils.use_skin_fonts_prop, kodi_utils.addon_installed
left_action, right_action, info_action = kodi_utils.window_xml_left_action, kodi_utils.window_xml_right_action, kodi_utils.window_xml_info_action
window_xml_dialog, logger, player, notification = kodi_utils.window_xml_dialog, kodi_utils.logger, kodi_utils.player, kodi_utils.notification
make_listitem, sleep, open_file, path_exists = kodi_utils.make_listitem, kodi_utils.sleep, kodi_utils.open_file, kodi_utils.path_exists
extras_keys, folder_options = ('upper', 'uppercase', 'italic', 'capitalize', 'black', 'mono', 'symbol'), ('xml', '1080', '720', '1080p', '720p', '1080i', '720i', '16x9')
needed_font_values = ((21, False, 'font10'), (26, False, 'font12'), (30, False, 'font13'), (33, False, 'font14'), (38, False, 'font16'), (60, True, 'font60'))
addon_skins_folder = 'special://home/addons/plugin.video.fen/resources/skins/Default/1080i/'

def open_window(import_info, skin_xml, **kwargs):
	'''
	import_info: tuple with ('module', 'function')
	'''
	try:
		xml_window = create_window(import_info, skin_xml, **kwargs)
		choice = xml_window.run()
		del xml_window
		return choice
	except Exception as e:
		logger('error in open_window', str(e))

def create_window(import_info, skin_xml, **kwargs):
	'''
	import_info: tuple with ('module', 'function')
	'''
	try:
		function = manual_function_import(*import_info)
		args = (skin_xml, skin_location())
		xml_window = function(*args, **kwargs)
		return xml_window
	except Exception as e:
		logger('error in create_window', str(e))
		return notification(32574)

class BaseDialog(window_xml_dialog):
	def __init__(self, *args):
		window_xml_dialog.__init__(self, args)
		self.player = player
		self.closing_actions = closing_actions
		self.selection_actions = selection_actions
		self.context_actions = context_actions
		self.info_action = info_action
		self.left_action = left_action
		self.right_action = right_action

	def make_listitem(self):
		return make_listitem()

	def build_url(self, params):
		return build_url(params)

	def execute_code(self, command):
		return execute_builtin(command)
	
	def get_position(self, window_id):
		return self.getControl(window_id).getSelectedPosition()

	def get_listitem(self, window_id):
		return self.getControl(window_id).getSelectedItem()

	def make_contextmenu_item(self, label, action, params):
		cm_item = self.make_listitem()
		cm_item.setProperty('label', label)
		cm_item.setProperty('action', action % self.build_url(params))
		return cm_item

	def get_infolabel(self, label):
		return get_infolabel(label)
	
	def open_window(self, import_info, skin_xml, **kwargs):
		return open_window(import_info, skin_xml, **kwargs)

	def sleep(self, time):
		sleep(time)

	def path_exists(self, path):
		return path_exists(path)

	def translate_path(self, path):
		return translate_path(path)

	def set_home_property(self, prop, value):
		set_property('fen.%s' % prop, value)

	def get_home_property(self, prop):
		return get_property('fen.%s' % prop)

	def get_attribute(self, obj, attribute):
		return getattr(obj, attribute)

	def set_attribute(self, obj, attribute, value):
		return setattr(obj, attribute, value)

	def get_current_skin(self):
		return current_skin()

	def clear_modals(self):
		try: del self.player
		except: pass

	def notification(self, text, duration=3000):
		return notification(text, duration)

	def addon_installed(self, addon_id):
		return addon_installed(addon_id)

class FontUtils:
	def execute_custom_fonts(self):
		if not self.skin_change_check(): return
		self.replacement_values = []
		self.replacement_values_append = self.replacement_values.append
		try: self.skin_font_xml = translate_path('special://skin/%s/Font.xml' % [i for i in list_dirs(translate_path('special://skin'))[0] if i in folder_options][0])
		except: self.skin_font_xml = None
		self.all_addon_xmls = list_dirs(translate_path(addon_skins_folder))[1]
		if self.use_skin_fonts == 'true': self.skin_font_info = self.get_font_info() or self.default_font_info()
		else: self.skin_font_info = self.default_font_info()
		for item in needed_font_values: self.replacement_values_append(self.match_font(*item))
		for item in self.all_addon_xmls: self.replace_font(item)
		for item in ((current_skin_prop, self.current_skin), (use_skin_fonts_prop, self.use_skin_fonts)): set_property(*item)

	def skin_change_check(self):
		self.current_skin, self.use_skin_fonts = current_skin(), use_skin_fonts()
		if self.current_skin != get_property(current_skin_prop): return True
		if self.use_skin_fonts != get_property(use_skin_fonts_prop): return True
		return False

	def match_font(self, size, bold, fallback):
		font_tag = 'FEN_%s%s' % (size, '_BOLD' if bold else '')
		size_range = range(int(size * 0.75), int(size * 1.25))
		compatibility_range = range(int(size * 0.50), int(size * 1.50))
		compatibility_fonts = [i['name'] for i in self.skin_font_info if i['name'] == fallback and i['size'] in compatibility_range]
		if compatibility_fonts: return (font_tag, compatibility_fonts[0])
		sized_fonts = [i for i in self.skin_font_info if i['size'] in size_range]
		if not sized_fonts: return fallback
		fonts = [i for i in sized_fonts if i['bold'] == bold and not i['extra_styles']] or [i for i in sized_fonts if i['bold'] == bold] \
				or [i for i in sized_fonts if not i['extra_styles']] or sized_fonts
		return (font_tag, [i['name'] for i in fonts if i['size'] == min([i['size'] for i in fonts], key=lambda k: abs(k-size))][0])

	def get_font_info(self):
		results = []
		results_append = results.append
		try:
			for item in mdParse(self.skin_font_xml).getElementsByTagName('fontset')[0].getElementsByTagName('font'):
				try: name = item.getElementsByTagName('name')[0].firstChild.data
				except: continue
				name_compare = name.lower()
				try: size = int(item.getElementsByTagName('size')[0].firstChild.data)
				except: continue
				try: style = item.getElementsByTagName('style')[0].firstChild.data.lower()
				except: style = ''
				bold = any('bold' in item for item in (name_compare, style))
				extra_styles = any(item in style for item in extras_keys)
				if not extra_styles: extra_styles = any(item in name_compare for item in extras_keys)
				results_append({'name': name, 'size': size, 'bold': bold, 'extra_styles': extra_styles})
		except: pass
		return results

	def replace_font(self, window):
		file = translate_path(addon_skins_folder + window)
		with open_file(file) as f: content = f.read()
		for item in self.replacement_values:
			try: content = re.sub(r'<font>(.*?)</font> <\!-- %s -->' % item[0], '<font>%s</font> <!-- %s -->' % (item[1], item[0]), content)
			except: pass
		with open_file(translate_path(file), 'w') as f: f.write(content)

	def default_font_info(self):
		return [{'name': 'font10', 'size': 21, 'bold': False, 'extra_styles': False},
				{'name': 'font12', 'size': 26, 'bold': False, 'extra_styles': False},
				{'name': 'font13', 'size': 30, 'bold': False, 'extra_styles': False},
				{'name': 'font14', 'size': 33, 'bold': False, 'extra_styles': False},
				{'name': 'font16', 'size': 38, 'bold': False, 'extra_styles': False},
				{'name': 'font60', 'size': 60, 'bold': False, 'extra_styles': False}]
