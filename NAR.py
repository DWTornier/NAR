import requests
import time
import datetime
import configparser
import subprocess
import ctypes
import pyuac
import sys
import os
from win10toast import ToastNotifier
#Ref:https://blog.alx962.eu.org/?p=496
toaster = ToastNotifier()
number_of_attempted = 0
log_path = "log.txt" #Default log path
def is_admin():
    try:
        return ctypes.windll.shel32.IsUserAnAdmin()
    except:
        return False
    
def optLog(text):
    time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    text ="["+time1+"]" + text
    print(text)
    file_write_obj = open(log_path, 'a')
    file_write_obj.writelines(text)
    file_write_obj.write('\n')
    file_write_obj.close()
    return

def load_config(file_path):
    config = configparser.ConfigParser()
    try:
        config.read(file_path, encoding='gb18030')
        settings = config["Settings"]
        check_device_status_flag = settings.getboolean("check_device_status")
        check_service_status_flag = settings.getboolean("check_service_status")
        auto_login_flag = settings.getboolean("auto_login")
        devcon_path = settings["devcon_path"]
        number_of_attempts = int(settings["number_of_attempts"])
        check_interval = int(settings["check_interval"])
        sleep_interval = int(settings["sleep_interval"])
        log_path = settings["log_path"]

        websites = [value for key, value in config["Websites"].items()]
        devices = [value for key, value in config["Devices"].items()]
        services = [value for key, value in config["Services"].items()]
        
        login_info = dict(config["Login"])
        return check_device_status_flag, check_service_status_flag, auto_login_flag, devcon_path, number_of_attempts, check_interval, sleep_interval, log_path, websites, devices, services, login_info
    except KeyError as e:
        optLog("The configuration file lacks necessary configuration items: {0}".format(e))
        sys.exit(1)
    except ValueError as e:
        optLog("Invalid value in configuration file: {0}".format(e))
        sys.exit(1)
    except Exception as e:
        optLog("Error loading configuration file: {0}".format(e))
        sys.exit(1)

def toggle_device(action, devcon_path, device_id):
    subprocess.run([devcon_path, action , device_id], shell=True)

def toggle_service(action, service_name):
    subprocess.run(["sc", action, service_name], shell=True)



def check_device_status(devcon_path, device_id):
    result = subprocess.run([devcon_path, "status", device_id], shell=True, capture_output=True, text=True)
    return "running" in result.stdout.lower()  # Running is True，otherwise False

def check_service_status(service_name):
    result = subprocess.run(["sc", "query", service_name], capture_output=True, text=True, shell=True)
    if "STOPPED" in result.stdout:
        return False
    else: 
        return True

def check_internet_connection(website):
    try:
        status=requests.get(website)   # Test if fetching the homepage is successful
        optLog("[Connection Check]Requesting: {0}".format(website))
        if status.status_code == 200:
            optLog("[Connection Check]Internet Status: OK (200)")
        else : 
            optLog("[Connection Check]Internet Status: {0}".format(status.status_code))
        return True
    except:
        return False
    
def login(login_info):
    try:
        # Reading URL and login info from the Config File
        url = login_info.pop("url")  # Extract URL， and the rest are POST data.
        data = set(login_info)  # POST
        # Send request
        conn = requests.post(url=url, data=data)
    except Exception as e:
        optLog("[Auth]Reconnect Status : Timeout. Error: {0}".format(e))

def fix_connection():
    if check_device_status_flag:
        it = iter(devices)
        for index in it:
            if check_device_status(devcon_path, index):
                optLog("[Device]Device {0} is running, no need to fix.".format(index))
            else:
                toggle_device("disable",devcon_path,index)
                toggle_device("enable",devcon_path,index)
                optLog("[Device]Device {0} stopping detected, now it is restarted.".format(index))
    
    if check_service_status_flag:
        it = iter(services)
        for index in it:
            if (check_service_status(index)):
                optLog("[Service]Service {0} is running, no need to fix.".format(index))
            else:
                toggle_service("stop",index)
                toggle_service("start",index)
                optLog("[Service]Service {0} stopping detected, now it is restarted.".format(index))

    if auto_login_flag:
        login(login_info)
        optLog("[Auth]Relogin tried.")
    


if __name__ == "__main__":

    if not pyuac.isUserAdmin():
        optLog("[Main]Getting Admin...")
        pyuac.runAsAdmin()

    optLog("NAR - Network Automatic Reconnector")
    optLog("[Main]Cycle detection has started.")
    # Load Config File
    config_file_path = "config.ini"
    check_device_status_flag, check_service_status_flag, auto_login_flag, devcon_path, number_of_attempts, check_interval, sleep_interval, log_path, websites, devices, services, login_info = load_config(config_file_path)
    optLog("[Main]Config loaded successfully.")
    
    
    while True:
        websites_ = iter(websites)
        for index in websites_:
            if check_internet_connection(index):
                number_of_attempted = 0
            else:
                if number_of_attempted < number_of_attempts:
                    fix_connection()
                    number_of_attempted += 1
                    optLog("[Main]Can't connect to the Internet. Fixing attempts: {0}".format(number_of_attempted))
                if number_of_attempted == number_of_attempts:
                    optLog("[Main]Can't fix the Internet, manual operation required.")
                    toaster.show_toast("NAR",
                    "Can't fix the Internet, manual operation required.",
                    icon_path=None,
                    duration=10)
                    number_of_attempted += 1
            time.sleep(check_interval)  
        optLog("[Main]The cycle ends and sleeps for {0} seconds.".format(sleep_interval))
        time.sleep(sleep_interval)
    # The above sleep statement is to avoid frequent requests and can be changed appropriately
