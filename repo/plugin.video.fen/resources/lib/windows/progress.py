# -*- coding: utf-8 -*-
from windows import BaseDialog
from modules.kodi_utils import addon_icon, local_string as ls
# from modules.kodi_utils import logger

class Progress(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.is_canceled = False
		self.heading = kwargs.get('heading', ls(32036))
		self.icon = kwargs.get('icon', addon_icon)

	def run(self):
		self.doModal()
		self.clearProperties()

	def onInit(self):
		self.set_controls()

	def iscanceled(self):
		return self.is_canceled

	def onAction(self, action):
		if action in self.closing_actions:
			self.is_canceled = True
			self.close()

	def set_controls(self):
		self.getControl(200).setImage(self.icon)
		self.getControl(2000).setLabel(self.heading)

	def update(self, content='', percent=0, icon=None):
		try:
			self.getControl(2001).setText(content)
			self.getControl(5000).setPercent(percent)
			if icon: self.getControl(200).setImage(icon)
		except: pass
