import requests
import time
import datetime
import os
from win10toast import ToastNotifier
#Ref:https://blog.alx962.eu.org/?p=496
toaster = ToastNotifier()
websites = ['https://www.baidu.com/','https://www.bilibili.com/'] #it can be replaced with other websites
sleepTime = 30 #Second
shortSleepTime =15
logDir = "log.txt"

def optLog(text):
    
    time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    text ="["+time1+"]" + text
    print(text)
    file_write_obj = open(logDir, 'a')
    file_write_obj.writelines(text)
    file_write_obj.write('\n')
    file_write_obj.close()
    return

optLog("=====CNART=====")
optLog("(Campus Network Automatic Reconnection Tool)")
optLog("Cycle detection has started.")
while True :    # Loop detection
    for i in range (0,2):
        try:
            status=requests.get(websites[i])   # Test if fetching the homepage is successful
            optLog("Requesting: {0}".format(websites[i]))
            if status.status_code == 200:
                optLog("Internet Status: OK (200)")
            else : 
                optLog("Internet Status: {0}".format(status.status_code))
            optLog("The next operation is scheduled in {0} seconds.".format(sleepTime))
            time.sleep(sleepTime)  # If successful, recheck network connectivity after 30 seconds
        except:
            try:# Attempt to authenticate
                optLog("Can't connect to the internet. Now trying reconnect.")

                toaster.show_toast("CNART",
                   "Can't connect to the internet. Now trying reconnect.",
                   icon_path=None,
                   duration=10)
                
                url = 'http://xx.xx.xxx.xx/'   # Change the URL here to your actual authentication URL, POST form to the website you want
                data={
                    "DDDDD":"abcdefg", # replace it with your account
                    "upass":"qwerty", # replace it with your password (it is ciphertext, not plaintext)
                    "R1":"0",
                    "R2":"1",
                    "para":"00",
                    "0MKKey":"123456",
                    "v6ip":""
                }   # Send the form. Please modify the form information
                # The form information here can be anything, basically they are all different, no need to worry
                conn=requests.post(url=url,data=data)   # Send request
                optLog("The next operation is scheduled in {0} seconds.".format(shortSleepTime))
                time.sleep(shortSleepTime)  # Try fetching the homepage again to test the network after 15 seconds. If it fails, continue to authenticate and loop
            except:# If authentication fails, try to detect the network and authenticate again
                optLog("Reconnect Status : Timeout")
                continue
    optLog("The cycle ends and sleeps for {0} seconds.".format(sleepTime))
    time.sleep(sleepTime)
    # The above sleep statement is to avoid frequent requests and can be changed appropriately
