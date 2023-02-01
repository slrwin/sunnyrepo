import win32com.client as comclt
import time
wsh= comclt.Dispatch("WScript.Shell")
while 1 == 1:
    wsh.SendKeys("{NumLock}") # send the keys 
    time.sleep(240)