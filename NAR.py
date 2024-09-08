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
    
class ConfigManager(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr    
    
    def load_config(self, file_path):
        try:
            self.read(file_path, encoding='gb18030')
            settings = self["Settings"]
            check_device_status_flag = settings.getboolean("check_device_status")
            check_service_status_flag = settings.getboolean("check_service_status")
            auto_login_flag = settings.getboolean("auto_login")
            devcon_path = settings["devcon_path"]
            number_of_attempts = int(settings["number_of_attempts"])
            check_interval = int(settings["check_interval"])
            sleep_interval = int(settings["sleep_interval"])
            log_path = settings["log_path"]

            websites = [value for key, value in self["Websites"].items()]
            devices = [value for key, value in self["Devices"].items()]
            services = [value for key, value in self["Services"].items()]
            login_headers = dict(self["Login_Headers"])
            login_info = dict(self["Login_Info"])
        
            return check_device_status_flag, check_service_status_flag, auto_login_flag, devcon_path, number_of_attempts, check_interval, sleep_interval, log_path, websites, devices, services, login_headers, login_info
        except KeyError as e:
            OperationManager.optLog("The configuration file lacks necessary configuration items: {0}".format(e))
            sys.exit(1)
        except ValueError as e:
            OperationManager.optLog("Invalid value in configuration file: {0}".format(e))
            sys.exit(1)
        except Exception as e:
            OperationManager.optLog("Error loading configuration file: {0}".format(e))
            sys.exit(1)

class DeviceManager:
    def toggle_device(self, action, devcon_path, device_id):
        subprocess.run([devcon_path, action , device_id], shell=True)

    def check_device_status(self, devcon_path, device_id):
        result = subprocess.run([devcon_path, "status", device_id], shell=True, capture_output=True, text=True)
        return "running" in result.stdout.lower()  # Running is True，otherwise False
class ServiceManager:
    def toggle_service(self, action, service_name):
        subprocess.run(["sc", action, service_name], shell=True)

    def check_service_status(self, service_name):
        result = subprocess.run(["sc", "query", service_name], capture_output=True, text=True, shell=True)
        if "STOPPED" in result.stdout:
            return False
        else: 
            return True

class RequestManager:
    def check_internet_connection(self, website):
        try:
            status=requests.get(website)   # Test if fetching the homepage is successful
            OperationManager.optLog("[Connection Check]Requesting: {0}".format(website))
            if status.status_code == 200:
                OperationManager.optLog("[Connection Check]Internet Status: OK (200)")
            else : 
                OperationManager.optLog("[Connection Check]Internet Status: {0}".format(status.status_code))
            return True
        except:
            return False
    
    def login(self, url, data, headers):
        try:
            # Send request
            conn = requests.post(url, data=data, headers=headers)
            OperationManager.optLog("[Auth]Status: {0}".format(conn.status_code))
        except Exception as e:
            OperationManager.optLog("[Auth]Status: Error: {0}".format(e))

class OperationManager:
    def __init__(self, deviceManager, serviceManager, requestManager):
        self.deviceManager = deviceManager
        self.serviceManager = serviceManager
        self.requestManager = requestManager
    
    @staticmethod
    def optLog(text):
        time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        text ="["+time1+"]" + text
        print(text)
        file_write_obj = open(log_path, 'a')
        file_write_obj.writelines(text)
        file_write_obj.write('\n')
        file_write_obj.close()
        return
    
    def fix_connection(self):
        if check_device_status_flag:
            it = iter(devices)
            for index in it:
                if deviceManager.check_device_status(devcon_path, index):
                    self.optLog("[Device]Device {0} is running, no need to fix.".format(index))
                else:
                    deviceManager.toggle_device("disable",devcon_path,index)
                    deviceManager.toggle_device("enable",devcon_path,index)
                    self.optLog("[Device]Device {0} stopping detected, now it is restarted.".format(index))
    
        if check_service_status_flag:
            it = iter(services)
            for index in it:
                if (serviceManager.check_service_status(index)):
                    self.optLog("[Service]Service {0} is running, no need to fix.".format(index))
                else:
                    serviceManager.toggle_service("stop",index)
                    serviceManager.toggle_service("start",index)
                    self.optLog("[Service]Service {0} stopping detected, now it is restarted.".format(index))

        if auto_login_flag:
            requestManager.login(login_url,login_data,login_headers)
            self.optLog("[Auth]Relogin tried.")
    


if __name__ == "__main__":
    
    configManager = ConfigManager()
    deviceManager = DeviceManager()
    serviceManager = ServiceManager()
    requestManager = RequestManager()
    operationManager = OperationManager(deviceManager, serviceManager, requestManager)

    # Check if the program is running as an administrator
    if not pyuac.isUserAdmin():
        OperationManager.optLog("[Main]Getting Admin...")
        pyuac.runAsAdmin()
    
    OperationManager.optLog("NAR - Network Automatic Reconnector")
    OperationManager.optLog("[Main]Cycle detection has started.")
    # Load Config File
    config_file_path = "config.ini"
    check_device_status_flag, check_service_status_flag, auto_login_flag, devcon_path, number_of_attempts, check_interval, sleep_interval, log_path, websites, devices, services, login_headers, login_info = configManager.load_config(config_file_path)
    
    login_url = login_info.pop("url")
    login_data = login_info  # POST
    
    OperationManager.optLog("[Main]Config loaded successfully.")
    
    
    while True:
        websites_ = iter(websites)
        for index in websites_:
            if requestManager.check_internet_connection(index):
                number_of_attempted = 0
            else:
                if number_of_attempted < number_of_attempts:
                    operationManager.fix_connection()
                    number_of_attempted += 1
                    OperationManager.optLog("[Main]Can't connect to the Internet. Fixing attempts: {0}".format(number_of_attempted))
                if number_of_attempted == number_of_attempts:
                    OperationManager.optLog("[Main]Can't fix the Internet, manual operation required.")
                    toaster.show_toast("NAR",
                    "Can't fix the Internet, manual operation required.",
                    icon_path=None,
                    duration=10)
                    number_of_attempted += 1
            time.sleep(check_interval)  
        OperationManager.optLog("[Main]The cycle ends and sleeps for {0} seconds.".format(sleep_interval))
        time.sleep(sleep_interval)
    # The above sleep statement is to avoid frequent requests and can be changed appropriately
