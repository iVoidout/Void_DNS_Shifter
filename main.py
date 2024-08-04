import time
import customtkinter
import appFuncitons as af
from os import path
import csv
import json
import subprocess
from ping3 import ping
import threading
import re

# variable
dnsName = ""
primarydns = "0.0.0.0"
secondarydns = "0.0.0.0"
adapterName = "Ethernet"
dnsDict = {}
dnsList = []
settings = {}
adapterList = af.get_adapters()
adapterAvailable = True
onStartup = "Current"


appearanceMode = "system"
purpleTheme = r"assets\theme-purple.json"
blueTheme = r"assets\theme-blue.json"
retroTheme = r"assets\theme-retro.json"
themesCheck = True

if path.isfile(purpleTheme) is False or path.isfile(blueTheme) is False or path.isfile(retroTheme) is False:
    themesCheck = False

appTheme = purpleTheme
iconPath = af.resource_path(r"logo.ico")

configPath = r"assets\config.json"
dnsFilePath = r"dns.csv"

fontH = ("Cascadia Code", 20, "bold")
font = ("Cascadia Code", 18, "normal")
fontWidget = ("Cascadia Code", 14, "normal")


# Main Window
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.iconbitmap(iconPath)
        self.geometry(af.center_window(self, 300, 400))
        self.title("Void DNS Shifter")
        self.resizable(False, False)
        self.toplevel_window = None
        # Grid Configuration
        # Columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        # Rows
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Starting Functions
        self.check_adapter()
        if onStartup == "Fastest":
            thread = threading.Thread(target=self.get_fastest)
            thread.start()
        else:
            self.get_current_dns()
        if themesCheck is False:
            self.themes_lost()

        # Functions
        def change_dns_values(choice):
            global primarydns, secondarydns, dnsList, dnsDict, dnsName

            # try:
            if choice == "Fastest":
                subThread = threading.Thread(target=self.get_fastest)
                subThread.start()

            else:
                dnsName = choice
                primarydns = dnsDict[choice][0]
                secondarydns = dnsDict[choice][1]

                self.frame.frameUpdate()
                self.setbutton.configure(state="normal")

        def set_dns():
            global primarydns, secondarydns, adapterName
            try:
                subprocess.run(
                    ["netsh", "interface", "ipv4", "set", "dns", adapterName, "static", primarydns],
                    check=True
                )
                if secondarydns != "" or secondarydns != "0.0.0.0":
                    subprocess.run(
                        ["netsh", "interface", "ipv4", "add", "dns", adapterName, secondarydns, "index=2"],
                        check=True
                    )
                subprocess.run(["ipconfig", "/flushdns"], check=True)
                af.MessageBox(title="Done!", message=f"The DNS has been set!", width=250, parent=self)

            except subprocess.CalledProcessError:
                af.MessageBox(title="Error", message="Something went wrong!\nTry running as Admin.",
                              parent=self, height=110)

        def reset_dns():
            try:
                subprocess.run(["netsh", "interface", "ip", "set", "dns", adapterName, "source=dhcp"], check=True)
                subprocess.run(["ipconfig", "/flushdns"], check=True)
                self.frame.label_primary.configure(text="0.0.0.0")
                self.frame.label_secondary.configure(text="0.0.0.0")
                self.setbutton.configure(state="disabled")
                self.frame.pingResult.set("Ping: 0")
                self.combobox.set("Select DNS")
                af.show_toplevel(self, af.MessageBox(title="Info!", message="The DNS has been reset!",
                                                     width=250, parent=self))
            except subprocess.CalledProcessError:
                af.MessageBox(title="Error", message="Something went wrong!\nTry running as Admin.",
                              parent=self, height=110)

        def add_dns():
            af.show_toplevel(self, DnsInputWindow())

        def settingsOpen():
            af.show_toplevel(self, SettingsWindow())

        self.frame = AppFrame(self, fg_color="transparent")
        self.frame.grid(row=0, columnspan=3, sticky="news", pady=(20, 20), padx=20)

        ComboList = []
        ComboList.extend(dnsList)
        ComboList.insert(0, "Fastest")

        self.combobox = customtkinter.CTkComboBox(self, values=ComboList, command=change_dns_values, font=fontWidget)
        self.combobox.grid(row=1, column=0, pady=(0, 10), padx=(30, 0), columnspan=2, sticky="ew")

        addbutton = customtkinter.CTkButton(self, text="+", width=40, command=add_dns)
        addbutton.grid(row=1, column=2, pady=(0, 10), padx=(20, 30), sticky="ew")

        self.setbutton = customtkinter.CTkButton(self, text="Set DNS", command=set_dns, font=fontWidget)
        self.setbutton.grid(row=2, column=0, pady=(0, 20), padx=(30, 0), sticky="ew")
        self.setbutton.configure(state="disabled")
        settingsButton = customtkinter.CTkButton(self, text="⚙", width=30, command=settingsOpen)
        settingsButton.grid(row=2, column=1, pady=(0, 20), padx=(20, 0),  sticky="ew")

        resetbutton = customtkinter.CTkButton(self, text="Reset", width=30, command=reset_dns,
                                              font=("Cascadia Code", 12, "normal"))
        resetbutton.grid(row=2, column=2, pady=(0, 20), padx=(10, 30), sticky="ew")

    def updateComboBox(self):
        self.combobox.configure(values=dnsList)

    def configFileInfo(self):
        af.MessageBox(title="Info!", message="Config.json was not found\n\nit is now replaced",
                      height=150, width=250, parent=self).get_input()
        af.restart_program()

    def dnsFileInfo(self):
        af.MessageBox(title="Info!", message="DNS file was not found\n\nit is now replaced",
                      height=150, width=250, parent=self).wait_window()
        af.restart_program()

    def configReset(self):
        userInput = af.MessageBox(title="Error", message="Config.json might be corrupted!\n\nReset File?", msgType=1,
                                  height=150, width=250, parent=self).get_input()

        if userInput is True:

            settingsDict = {
                'Adapter': adapterName,
                'Mode': appearanceMode,
                'Theme': appTheme,
                'Startup': onStartup
            }

            with open(configPath, 'w') as jsonFile:
                json.dump(settingsDict, jsonFile)

            af.restart_program()

        else:
            af.close_app()

    def themes_lost(self):
        af.MessageBox(title="Info!", message="Theme files are missing!\n\nDefault blue will be used",
                      height=150, width=250, parent=self)

    def check_adapter(self):
        global adapterAvailable, adapterName
        if adapterList.count(adapterName) == 0:
            adapterName = adapterList[0]
            af.MessageBox(title="Info!", message=f"The selected adapter is unavailable!\n\nThe DNS has been selected",
                          width=250, height=130, parent=self)
            handle_config(force=True)

    def get_fastest(self):
        global primarydns, secondarydns, dnsList, dnsDict, dnsName

        statusText = "Finding Fastest"
        self.after(200, lambda: self.frame.pingResult.set(statusText))
        self.combobox.set("Pinging...")
        self.combobox.configure(state="disabled")
        self.setbutton.configure(state="disabled")

        stop_event_dots = threading.Event()

        def dotdotdot():
            dotCount = 0
            while not stop_event_dots.is_set():
                time.sleep(0.200)
                if dotCount <= 3:
                    self.frame.pingResult.set(statusText + ("." * dotCount))
                    dotCount += 1
                else:
                    dotCount = 0

        threadDots = threading.Thread(target=dotdotdot)
        threadDots.start()

        try:
            resultList = [0]
            fastest = 99999999
            fastestName = ""
            for name in dnsList:
                ip = dnsDict[name][0]
                self.combobox.set(name)
                latency = ping(ip)
                if latency is not None:
                    latency = round(latency * 1000, 0)
                    resultList[0] = int(latency)
                else:
                    resultList[0] = -1

                latency = resultList[0]
                if latency < fastest and latency != -1:
                    fastest = latency
                    fastestName = name

            stop_event_dots.set()
            dnsName = fastestName
            primarydns = dnsDict[fastestName][0]
            secondarydns = dnsDict[fastestName][1]

            self.frame.frameUpdate(pingBool=False)
            self.after(250, lambda: self.frame.pingResult.set(f"Ping: {fastest}"))
            self.setbutton.configure(state="normal")
            self.combobox.configure(state="normal")
            self.combobox.set(fastestName)

        except Exception:
            self.after(200, lambda: self.frame.pingResult.set("Couldn't get Fastest"))
            self.combobox.set("Select DNS")

    def get_current_dns(self):
        global primarydns, secondarydns

        res = subprocess.run(["netsh", "interface", "ipv4", "show", "dnsservers", adapterName],
                             capture_output=True, text=True, check=True).stdout
        pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\b'

        match = re.findall(pattern, str(res))

        primarydns = match[0]

        if len(match) != 1:
            secondarydns = match[1]
        else:
            secondarydns = "0.0.0.0"

        # self.frame.frameUpdate(pingBool=True)
        self.after(300, lambda: self.frame.frameUpdate(pingBool=True))
        self.after(100, lambda: self.combobox.set("Current DNS"))


# the Information Frame
class AppFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.pingResult = customtkinter.StringVar()
        self.after(200, self.pingResult.set(value=""))

        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)
        label1 = customtkinter.CTkLabel(self, text="PRIMARY DNS:", font=fontH)
        label1.grid(row=0, column=0, pady=(10, 0), sticky="ew")
        self.label_primary = customtkinter.CTkLabel(self, text=primarydns, font=font)
        self.label_primary.grid(row=1, pady=(0, 0))
        label2 = customtkinter.CTkLabel(self, text="SECONDARY DNS:", font=fontH)
        label2.grid(row=2, columnspan=3, pady=(0, 0))
        self.label_secondary = customtkinter.CTkLabel(self, text=secondarydns, font=font)
        self.label_secondary.grid(row=3, columnspan=3, pady=(0, 0))
        self.label_ping = customtkinter.CTkLabel(self, textvariable=self.pingResult, font=font, text="")
        self.label_ping.grid(row=4, columnspan=3, pady=(20, 5), padx=(0, 0))

    def frameUpdate(self, pingBool=True):
        self.label_primary.configure(text=primarydns)

        if af.is_valid_ip(str(secondarydns)):
            self.label_secondary.configure(text=secondarydns)
        else:
            self.label_secondary.configure(text="0.0.0.0")

        if pingBool:
            self.pingResult.set("Pinging...")
            af.start_threading(af.get_ping_frame, ip=primarydns, result=self.pingResult)


# Add DNS window
class DnsInputWindow(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.iconbitmap(iconPath)
        self.geometry(af.center_window(app, 200, 300, centerType='parent'))
        self.title("Add")
        self.toplevel_window = None
        self.grab_set()
        self.resizable(False, False)

        # Grid Configuration
        # Columns
        self.grid_columnconfigure(0, weight=3)
        # Rows
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # Functions
        def save_dns():
            name = name_entry.get()
            prDns = prDns_entry.get()
            scDns = scDns_entry.get()

            if name == "" or prDns == "":
                af.MessageBox(title="Error", message="Name and Primary is needed", parent=self)

            elif af.is_valid_ip(prDns) is False:
                af.MessageBox(title="Error", message="The Primary DNS is not valid!", parent=self)
            elif scDns != "" and af.is_valid_ip(scDns) is False:
                af.MessageBox(title="Error", message="The Primary DNS is not valid!", parent=self)

            else:
                for i in dnsList:
                    if i == name:
                        af.MessageBox(title="Error", message="The name has already been used!", width=250, parent=self)
                        return

                with open('dns.csv', mode='a', newline='') as dnsFile:
                    writer = csv.writer(dnsFile)
                    writer.writerow([name, prDns, scDns])
                    af.MessageBox(title="Done!", message="The DNS has been added!", width=250, parent=self)
                handle_dns_table()
                app.updateComboBox()
                name_entry.delete(0, customtkinter.END)
                prDns_entry.delete(0, customtkinter.END)
                if scDns_entry.get() != "":
                    scDns.delete(0, customtkinter.END)

        label1 = customtkinter.CTkLabel(self, text="Add Custom DNS", font=fontWidget)
        label1.grid(row=0, pady=(10, 0))
        name_entry = customtkinter.CTkEntry(self, placeholder_text="Name", font=fontWidget)
        name_entry.grid(row=1)
        prDns_entry = customtkinter.CTkEntry(self, placeholder_text="Primary", font=fontWidget)
        prDns_entry.grid(row=2)
        scDns_entry = customtkinter.CTkEntry(self, placeholder_text="Secondary", font=fontWidget)
        scDns_entry.grid(row=3)

        saveDns_Button = customtkinter.CTkButton(self, text="Save", command=save_dns, font=fontWidget)
        saveDns_Button.grid(row=4, pady=10)


# Settings Window
class SettingsWindow(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()

        settingsFont = ("Cascadia Code", 12, "normal")

        self.iconbitmap(iconPath)
        self.geometry(af.center_window(app, 300, 450, centerType='parent'))
        self.title("Settings")
        self.toplevel_window = None
        self.grab_set()
        self.resizable(False, False)

        self.radio_var_mode = customtkinter.IntVar(value=0)
        self.radio_var_theme = customtkinter.IntVar(value=0)
        self.radio_var_startup = customtkinter.IntVar(value=0)

        # Grid Configuration
        # Columns
        self.grid_columnconfigure((0, 1, 2), weight=1)
        # Rows
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure((1, 2, 3, 4, 5, 6, 7), weight=1)
        self.iconbitmap(iconPath)

        def set_adapter(choice):
            global adapterName
            adapterName = choice

        label1 = customtkinter.CTkLabel(self, text="Select Internet Adapter:", font=fontWidget)
        label1.grid(row=0, columnspan=3, pady=(15, 0))
        self.combobox = customtkinter.CTkComboBox(self, values=adapterList, command=set_adapter, font=fontWidget)
        self.combobox.set(adapterName)
        self.combobox.grid(row=1, columnspan=3)

        label2 = customtkinter.CTkLabel(self, text="Appearance Mode:", font=fontWidget)
        label2.grid(row=2, columnspan=3, pady=(10, 0))

        rb_Size = 20
        self.mode_radio1 = customtkinter.CTkRadioButton(self, text="System", value=0, command=self.mode_radio,
                                                        variable=self.radio_var_mode,
                                                        radiobutton_width=rb_Size, radiobutton_height=rb_Size,
                                                        font=settingsFont)

        self.mode_radio1.grid(row=3, column=0, padx=(20, 10), sticky="ew")
        self.mode_radio2 = customtkinter.CTkRadioButton(self, text="Dark", value=1, command=self.mode_radio,
                                                        variable=self.radio_var_mode,
                                                        radiobutton_width=rb_Size, radiobutton_height=rb_Size,
                                                        font=settingsFont)
        self.mode_radio2.grid(row=3, column=1, padx=10, sticky="ew")
        self.mode_radio3 = customtkinter.CTkRadioButton(self, text="Light", value=2, command=self.mode_radio,
                                                        variable=self.radio_var_mode,
                                                        radiobutton_width=rb_Size, radiobutton_height=rb_Size,
                                                        font=settingsFont)
        self.mode_radio3.grid(row=3, column=2, padx=10, sticky="ew")

        label2 = customtkinter.CTkLabel(self, text="Theme Color:", font=fontWidget)
        label2.grid(row=4, columnspan=3, pady=(10, 0))
        self.theme_radio1 = customtkinter.CTkRadioButton(self, text="Purple", value=0, command=self.theme_radio,
                                                         variable=self.radio_var_theme,
                                                         radiobutton_width=rb_Size, radiobutton_height=rb_Size,
                                                         font=settingsFont)
        self.theme_radio1.grid(row=5, column=0, padx=(20, 10), sticky="ew")
        self.theme_radio2 = customtkinter.CTkRadioButton(self, text="Blue", value=1, command=self.theme_radio,
                                                         variable=self.radio_var_theme,
                                                         radiobutton_width=rb_Size, radiobutton_height=rb_Size,
                                                         font=settingsFont)
        self.theme_radio2.grid(row=5, column=1, padx=10, sticky="ew")
        self.theme_radio3 = customtkinter.CTkRadioButton(self, text="Retro", value=2, command=self.theme_radio,
                                                         variable=self.radio_var_theme,
                                                         radiobutton_width=rb_Size, radiobutton_height=rb_Size,
                                                         font=settingsFont)
        self.theme_radio3.grid(row=5, column=2, padx=10, sticky="ew")

        label2 = customtkinter.CTkLabel(self, text="Startup:", font=fontWidget)
        label2.grid(row=6, columnspan=3, pady=(10, 0))
        self.startup_radio1 = customtkinter.CTkRadioButton(self, text="Fastest DNS", value=0, command=self.startup_radio,
                                                           variable=self.radio_var_startup,
                                                           radiobutton_width=rb_Size, radiobutton_height=rb_Size,
                                                           font=settingsFont)
        self.startup_radio1.grid(row=7, column=0, padx=(25, 10), sticky="ew", columnspan=2)
        self.startup_radio2 = customtkinter.CTkRadioButton(self, text="Current DNS", value=1, command=self.startup_radio,
                                                           variable=self.radio_var_startup,
                                                           radiobutton_width=rb_Size, radiobutton_height=rb_Size,
                                                           font=settingsFont)
        self.startup_radio2.grid(row=7, column=1, padx=(65, 10), sticky="ew", columnspan=2)

        saveDns_Button = customtkinter.CTkButton(self, text="Save", command=self.save_settings, font=fontWidget)
        saveDns_Button.grid(row=8, columnspan=3, pady=20)

        with open(configPath, 'r') as jFile:
            settingsDict = json.load(jFile)

        match settingsDict['Mode']:
            case "system":
                self.mode_radio1.select()
            case "dark":
                self.mode_radio2.select()
            case "light":
                self.mode_radio3.select()

        match settingsDict['Theme']:
            case "theme-purple.json":
                self.theme_radio1.select()
            case "theme-blue.json":
                self.theme_radio2.select()
            case "theme-retro.json":
                self.theme_radio3.select()

        match settingsDict['Startup']:
            case "Fastest":
                self.startup_radio1.select()
            case "Current":
                self.startup_radio2.select()

        if themesCheck is False:
            self.disable_radios()

    def disable_radios(self):
        self.theme_radio1.configure(state="disable", text="N/A")
        self.theme_radio2.configure(state="disable", text="N/A")
        self.theme_radio3.configure(state="disable", text="N/A")

    # Functions
    def save_settings(self):
        global adapterName, appearanceMode, appTheme, configPath
        try:
            with open(configPath, 'r') as jFile:
                settingsDict = json.load(jFile)

            settingsDict['Adapter'] = adapterName
            settingsDict['Mode'] = self.mode_radio()
            settingsDict['Theme'] = self.theme_radio()
            settingsDict['Startup'] = self.startup_radio()

            with open(configPath, 'w') as jFile:
                json.dump(settingsDict, jFile)

            af.MessageBox(title="Done!", message="The settings have been save!", width=250, parent=self).get_input()
            handle_config()
            af.restart_program()

        except WindowsError:
            af.MessageBox(title="Error", message="Something went wrong!", width=250, parent=self)

    def mode_radio(self):
        match self.radio_var_mode.get():
            case 0:
                modeVar = "system"
            case 1:
                modeVar = "dark"
            case 2:
                modeVar = "light"
            case _:
                modeVar = appearanceMode
        return modeVar

    def theme_radio(self):
        match self.radio_var_theme.get():
            case 0:
                themeVar = purpleTheme
            case 1:
                themeVar = blueTheme
            case 2:
                themeVar = retroTheme
            case _:
                themeVar = "System"

        return themeVar

    def startup_radio(self):
        match self.radio_var_startup.get():
            case 0:
                startVar = "Fastest"
            case 1:
                startVar = "Current"
            case _:
                startVar = onStartup

        return startVar


# Get and Update DNS table
def handle_dns_table():
    global dnsDict, dnsList, dnsFilePath
    dnsDict = {}
    dnsList = []

    try:
        if path.isfile(dnsFilePath):

            with open('dns.csv', mode='r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    dnsDict[row[0]] = [row[1], row[2]]
                    dnsList.append(row[0])

        else:
            with open(dnsFilePath, mode='w', newline='') as dnsFile:
                writer = csv.writer(dnsFile)
                writer.writerow(['403', "10.202.10.202", "10.202.10.102"])
                writer.writerow(['Shecan', "178.22.122.100", "185.51.200.2"])
                writer.writerow(['Electro', "78.157.42.101", "78.157.42.100"])
                writer.writerow(['Google', "8.8.8.8", "8.8.4.4"])
                writer.writerow(['CloudFlair', "1.1.1.1", "1.0.0.1"])
                writer.writerow(['Quad9', "9.9.9.9", "149.112.112.112"])
                writer.writerow(['OpenDNS', "208.67.222.222", "208.67.220.220"])

            with open('dns.csv', mode='r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    dnsDict[row[0]] = [row[1], row[2]]
                    dnsList.append(row[0])
            App().dnsFileInfo()

    except Exception:
        print("Unexpected Error!")
        af.MessageBox(title="Error", message="Somthing went wrong!")


# Handle config.json file
def handle_config(force=False):
    global adapterName, settings, appTheme, appearanceMode, configPath, onStartup

    try:
        if path.isfile(configPath) and force is False:
            with open(configPath, 'r') as jsonFile:
                settings = json.load(jsonFile)

            adapterName = settings['Adapter']
            appearanceMode = settings['Mode']
            appTheme = settings['Theme']
            onStartup = settings['Startup']

        else:
            settings = {
                'Adapter': adapterName,
                'Mode': appearanceMode,
                'Theme': purpleTheme,
                'Startup': onStartup
            }

            with open(configPath, 'w') as jsonFile:
                json.dump(settings, jsonFile)

            if force is False:
                App().configFileInfo()
    except Exception:
        print("Config must be reset")
        App().configReset()

    if themesCheck:
        customtkinter.set_appearance_mode(appearanceMode)
        customtkinter.set_default_color_theme(appTheme)
    else:
        customtkinter.set_appearance_mode(appearanceMode)
        customtkinter.set_default_color_theme("blue")


handle_dns_table()
handle_config()
app = App()


app.protocol("WM_DELETE_WINDOW", af.on_closing)
app.mainloop()
