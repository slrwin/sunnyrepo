# -*- coding: utf-8 -*-
from windows import BaseDialog
from modules.settings import get_art_provider, suppress_episode_plot
from modules.kodi_utils import empty_poster, addon_fanart
# from modules.kodi_utils import logger

class ConfirmProgressMedia(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.is_canceled = False
		self.enable_fullscreen = False
		self.skip_resolve = False
		self.resolver_enabled = False
		self.selected = None
		self.meta = kwargs['meta']
		self.meta_get = self.meta.get
		self.text = kwargs.get('text', '')
		self.enable_buttons = kwargs.get('enable_buttons', False)
		if self.enable_buttons: self.true_button, self.false_button, self.focus_button = kwargs.get('true_button', ''), kwargs.get('false_button', ''), kwargs.get('focus_button', 10)
		else: self.enable_fullscreen = kwargs.get('enable_fullscreen', True)
		self.percent = float(kwargs.get('percent', 0))
		self.make_text()
		self.set_properties()

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
		if not self.enable_buttons:
			if action in self.closing_actions:
				self.is_canceled = True
				if self.resolver_enabled: self.close()
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
		self.year = str(self.meta_get('year'))
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
		self.setProperty('percent_label', self.make_percent_label(self.percent))
		self.setProperty('enable_fullscreen', str(self.enable_fullscreen))

	def set_resolver_properties(self):
		self.setProperty('enable_resolver', 'true')
		self.setProperty('text', self.text)

	def update(self, content='', percent=0):
		try:
			if self.enable_fullscreen:
				self.getControl(2001).setText(content)
				self.setProperty('percent', str(percent))
				self.setProperty('percent_label', self.make_percent_label(percent))
			else:
				self.getControl(2000).setText(content)
				self.getControl(5000).setPercent(percent)
		except: pass

	def update_resolver(self, content=''):
		try: self.getControl(2002).setText('••••  %s  ••••[CR]••••  %s  ••••' % content)
		except: self.getControl(2002).setText('')

	def make_percent_label(self, percent):
		return '[B]%s%%[/B]' % str(min(round(percent), 99)) if percent > 0 else ''
