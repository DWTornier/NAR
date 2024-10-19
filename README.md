# NAR
Network Automatic Reconnector

Ref: https://blog.alx962.eu.org/?p=496  
## Features
**1. Running in the background:** The program runs in the background without interruption.  
**2. Device Status Check:** Automatically checks if the specified network device is enabled. If not, the script attempts to enable it.
**3. Service Status Check:** Checks the status of specific network-related services and ensures they are running. If a service is stopped, the script attempts to start it.  
**4. Automatic Network Login:** The script attempts to automatically log in to the network when a disconnection is detected.  
**5. Notifications:** Provides notifications to the user when a manual intervention is required after an automatic attempt fails.
## Installation & Usage
1. Make sure your OS is Windows 10 and Python is installed: https://www.python.org/downloads/
2. Make sure Windows SDK and WDK(Windows Driver Kit) are installed.
3. Download or clone this repository.
4. Run `pip install -r requirements.txt` to install dependencies.
5. Edit `Config.ini` File  
   The script requires a configuration file `config.ini` to specify various settings such as device ID, service status checks, and login credentials.
  **Here is an example to help you to understand the file:**  
   ```ini
   [Settings]
   # Set to true or false to enable or disable.
   check_device_status = true 
   check_service_status = true
   auto_login = true           
   # The absolute path of devcon.exe, which is included in the WDK.
   devcon_path = C:\Path\To\DevCon.exe
   # The maximum number of network repair attempts allowed.
   number_of_attempts = 3 
   # How many seconds a check for a website.
   check_interval = 15
   # How many seconds a cycle, which is checked all websites in list.
   sleep_interval = 30
   # Relative path to the log file, defalt is the root path.
   log_path = log.txt

   [Websites]
   # Websites for connection check
   site1 = https://www.google.com/
   site2 = https://www.bilibili.com/

   [Devices] 
   # You can find this value by viewing the "Details" tab in the network card properties through the Device Manager and selecting "Hardware ID"
   device1 = PCI\VEN_XXXX&DEV_YYYY #Replace with your hardware IDs

   [Services] 
   #Service names on your computer, generally no modification is required.
   service1 = WlanSvc
   service2 = dot3svc
   
   [Login_Headers]
   # Please modify the login headers, which are all different, depends on your operator, no need to worry.
   User-Agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36

   [Login_Info]   
   # Please modify the login form information, which are all different, depends on your operator, no need to worry.
   # [required]Change the URL here to your actual authentication URL.
   url = http://xxx.xxx.xxx.xxx/ 
   DDDDD = your_account  
   upass = your_password
   R1 = 0
   R2 = 1
   para = 00
   0MKKey = 123456
   v6ip = 
   ```
  

6. Run the `run.bat` and pass the UAC to start the program. If successful, the `log.txt` will be generated and updated in real-time. 
   Then you can close the cmd window, The program will run in the background as `pythonw.exe`or `Terminal` (you can check it out in the task manager) without manual intervention.  
   You can add `run.bat` to the startup task by creating a shortcut, so you don't need to start it manually in the future.
