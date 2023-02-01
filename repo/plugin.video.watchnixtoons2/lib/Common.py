# -*- coding: utf-8 -*-
import json
import xbmcgui
import six

try:
    import md5
except ImportError:
    from hashlib import md5

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

def generateMd5(strToMd5):
    encrptedMd5 = ""

    if six.PY2:
        md5Instance = md5.new()
    else:
        md5Instance = md5()
        strToMd5 = bytes(strToMd5, "UTF-8")

    md5Instance.update(strToMd5)
    encrptedMd5 = md5Instance.hexdigest()
    return encrptedMd5
