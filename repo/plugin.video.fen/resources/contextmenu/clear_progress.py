# -*- coding: utf-8 -*-
from xbmc import executebuiltin, getInfoLabel

executebuiltin('RunPlugin(%s)' % getInfoLabel('ListItem.Property(fen.clearprog_params)'))
