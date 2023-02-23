# -*- coding: utf-8 -*-
from windows import BaseDialog
from modules.settings import get_art_provider, suppress_episode_plot
from modules.kodi_utils import empty_poster, addon_fanart, get_icon
# from modules.kodi_utils import logger

string = str
flag_sd, flag_720p, flag_1080p, flag_4k = get_icon('results_sd'), get_icon('results_720p'), get_icon('results_1080p'), get_icon('results_4k')
flag_total, flag_remaining = get_icon('results_total'), get_icon('results_remaining')
flag_properties = {0: (flag_sd, flag_720p, flag_1080p, flag_4k), 1: (flag_4k, flag_1080p, flag_720p, flag_sd)}

class ConfirmProgressMedia(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.is_canceled, self.enable_fullscreen, self.skip_resolve, self.resolver_enabled, self.selected = False, False, False, False, None
		self.meta = kwargs.get('meta')
		self.meta_get = self.meta.get
		self.flags_direction = kwargs.get('flags_direction', 0)
		self.text = kwargs.get('text', '')
		self.enable_buttons = kwargs.get('enable_buttons', False)
		if self.enable_buttons:
			self.true_button, self.false_button, self.focus_button = kwargs.get('true_button', ''), kwargs.get('false_button', ''), kwargs.get('focus_button', 10)
		else: self.enable_fullscreen = kwargs.get('enable_fullscreen', True)
		self.percent = float(kwargs.get('percent', 0))
		self.make_text()
		self.set_properties()
		if self.enable_fullscreen and not self.resolver_enabled: self.set_quality_flags()

	def onInit(self):
		if self.enable_buttons: self.setup_buttons()

	def run(self):
		self.doModal()
		self.clearProperties()
		self.clear_modals()
		return self.selected

	def iscanceled(self):
		if self.enable_buttons: return self.selected
		else: return self.is_canceled

	def skip_resolved(self):
		status = self.skip_resolve
		self.skip_resolve = False
		return status

	def onAction(self, action):
		if action in self.closing_actions:
			self.is_canceled = True
			if self.enable_buttons: self.close()
		if self.resolver_enabled:
			if action == self.right_action: self.skip_resolve = True

	def reset_is_cancelled(self):
		self.is_canceled = False

	def enable_resolver(self):
		self.resolver_enabled = True
		self.make_resolver_text()
		self.set_resolver_properties()

	def onClick(self, controlID):
		self.selected = controlID == 10
		self.close()

	def setup_buttons(self):
		self.update(self.text, self.percent)
		self.setFocusId(self.focus_button)

	def make_text(self):
		self.poster_main, self.poster_backup, self.fanart_main, self.fanart_backup, self.clearlogo_main, self.clearlogo_backup = get_art_provider()
		self.title = self.meta_get('title')
		self.year = string(self.meta_get('year'))
		self.poster = self.meta_get('custom_poster') or self.meta_get(self.poster_main) or self.meta_get(self.poster_backup) or empty_poster
		self.fanart = self.meta_get('custom_fanart') or self.meta_get(self.fanart_main) or self.meta_get(self.fanart_backup) or addon_fanart
		self.clearlogo = self.meta_get('custom_clearlogo') or self.meta_get(self.clearlogo_main) or self.meta_get(self.clearlogo_backup) or ''

	def make_resolver_text(self):
		if self.meta_get('media_type') == 'movie': self.text = self.meta_get('plot')
		else:
			if suppress_episode_plot(): plot = self.meta_get('tvshow_plot') or '* Hidden to Prevent Spoilers *'
			else: plot = self.meta_get('plot', '') or self.meta_get('tvshow_plot', '')
			self.text = '[B]%02dx%02d - %s[/B][CR][CR]%s' % (self.meta_get('season'), self.meta_get('episode'), self.meta_get('ep_name', 'N/A').upper(), plot)

	def set_properties(self):
		if self.enable_buttons:
			self.setProperty('buttons', 'true')
			self.setProperty('true_button', self.true_button)
			self.setProperty('false_button', self.false_button)
		self.setProperty('title', self.title)
		self.setProperty('fanart', self.fanart)
		self.setProperty('clearlogo', self.clearlogo)
		self.setProperty('year', self.year)
		self.setProperty('poster', self.poster)
		self.setProperty('enable_fullscreen', string(self.enable_fullscreen))

	def set_quality_flags(self):
		flag_props = flag_properties[self.flags_direction]
		self.setProperty('flag_0', flag_props[0])
		self.setProperty('flag_1', flag_props[1])
		self.setProperty('flag_2', flag_props[2])
		self.setProperty('flag_3', flag_props[3])
		self.setProperty('flag_total', flag_total)
		self.setProperty('flag_remaining', flag_remaining)

	def set_resolver_properties(self):
		self.setProperty('enable_resolver', 'true')
		self.setProperty('text', self.text)

	def update(self, content='', percent=0):
		try:
			if self.enable_fullscreen:
				self.getControl(2001).setText(content)
				self.setProperty('percent', string(percent))
				if not self.resolver_enabled and content: self.setProperty('show_remaining', 'true')
			else:
				self.getControl(2000).setText(content)
				self.getControl(5000).setPercent(percent)
		except: pass

	def update_results_count(self, results_sd, results_720p, results_1080p, results_4k, results_total, content='', percent=0):
		if self.flags_direction == 0:
			self.setProperty('results_0', string(results_sd))
			self.setProperty('results_1', string(results_720p))
			self.setProperty('results_2', string(results_1080p))
			self.setProperty('results_3', string(results_4k))
		else:
			self.setProperty('results_0', string(results_4k))
			self.setProperty('results_1', string(results_1080p))
			self.setProperty('results_2', string(results_720p))
			self.setProperty('results_3', string(results_sd))
		self.setProperty('results_total', string(results_total))
		self.update(content, percent)

	def update_resolver(self, content=''):
		try: self.getControl(2002).setText('••••  %s  ••••[CR]••••  %s  ••••' % content)
		except: self.getControl(2002).setText('')
