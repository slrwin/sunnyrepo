# -*- coding: utf-8 -*-
import json
import xbmcgui

def getWindowProperty(prop):
    window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    data = window.getProperty(prop)
    return json.loads(data) if data else None

def setWindowProperty(prop, data):
    window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    temp = json.dumps(data)
    window.setProperty(prop, temp)

def clearWindowProperty(prop):
    window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    window.clearProperty(prop)

def testWindowProperty(prop):
    window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    return window.getProperty(prop) != ''

def getRawWindowProperty(prop):
    window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    return window.getProperty(prop)

def setRawWindowProperty(prop, data):
    window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    window.setProperty(prop, data)
