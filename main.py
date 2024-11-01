import time
import customtkinter
import appFuncitons as af
import os
import csv
import json
import subprocess
from ping3 import ping
import threading
import re
import requests
import webbrowser

# variable
VERSION = "1.2.0"
github_main = "https://github.com/iVoidout/Void_DNS_Shifter/"
github_release = "https://github.com/iVoidout/Void_DNS_Shifter/releases"
github_version_file = "https://raw.githubusercontent.com/iVoidout/Void_DNS_Shifter/master/VERSION.txt"
dns_name = ""
primary_dns = "0.0.0.0"
secondary_dns = "0.0.0.0"
adapter_list = af.get_adapters()
adapter_name = adapter_list[0]
dns_dict = {}
dns_list = []
settings = {}
on_startup = "Current"

appearance_mode = "system"

local_appdata_path = os.getenv('LOCALAPPDATA')

app_local_folder = local_appdata_path + "\\VOIDSHIFTER"
os.makedirs(app_local_folder, exist_ok=True)

purple_theme = "assets\\theme-purple.json"
blue_theme = "assets\\theme-blue.json"
retro_theme = "assets\\theme-retro.json"

app_theme = purple_theme
icon_path = af.resource_path(r"logo.ico")
config_path = app_local_folder + "\\config.json"
dns_file_path = app_local_folder + "\\dns.csv"


fontH = ("Cascadia Code", 20, "bold")
font = ("Cascadia Code", 18, "normal")
font_widget = ("Cascadia Code", 14, "normal")


# Main Window
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.iconbitmap(icon_path)
        self.geometry(af.center_window(self, 300, 400))
        self.title("Void Shifter")
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
        if on_startup == "Fastest":
            thread = threading.Thread(target=self.get_fastest)
            thread.start()
        else:
            self.get_current_dns()

        # Functions
        def change_dns_values(choice):
            global primary_dns, secondary_dns, dns_list, dns_dict, dns_name

            # try:
            if choice == "Fastest":
                subThread = threading.Thread(target=self.get_fastest)
                subThread.start()

            elif choice == "Current":
                self.get_current_dns()
                self.set_button.configure(state="disabled")
            else:
                dns_name = choice
                primary_dns = dns_dict[choice][0]
                secondary_dns = dns_dict[choice][1]

                self.frame.frameUpdate()
                self.set_button.configure(state="normal")

        def set_dns():
            global primary_dns, secondary_dns, adapter_name
            try:
                def set_def():
                    subprocess.run(
                        ["netsh", "interface", "ipv4", "set", "dns", adapter_name, "static", primary_dns],
                        check=True, shell=True
                    )
                    if secondary_dns != "" or secondary_dns != "0.0.0.0":
                        subprocess.run(
                            ["netsh", "interface", "ipv4", "add", "dns", adapter_name, secondary_dns, "index=2"],
                            check=True, shell=True
                        )
                    subprocess.run(["ipconfig", "/flushdns"], check=True)
                    af.MessageBox(title="Done!", message=f"The DNS has been set!", width=250, parent=self)
                    self.set_button.configure(state="normal")
                    self.set_button.configure(text="Set DNS")

                self.set_button.configure(state="disabled")
                self.set_button.configure(text="Wait...")
                set_thread = threading.Thread(target=set_def)
                set_thread.start()

            except subprocess.CalledProcessError:
                af.MessageBox(title="Error", message="Something went wrong!\nTry running as Admin.",
                              parent=self, height=110)
                self.set_button.configure(state="normal")
                self.set_button.configure(text="Set DNS")

        def reset_dns():
            try:
                def reset_def():
                    subprocess.run(["netsh", "interface", "ip", "set", "dns", adapter_name, "source=dhcp"],
                                   check=True, shell=True)
                    subprocess.run(["ipconfig", "/flushdns"], check=True, shell=True)
                    self.frame.label_primary.configure(text="0.0.0.0")
                    self.frame.label_secondary.configure(text="0.0.0.0")
                    self.set_button.configure(state="disabled")
                    self.frame.pingResult.set("Ping: 0")
                    self.combobox.set("Select DNS")
                    af.show_toplevel(self, af.MessageBox(title="Info!", message="The DNS has been reset!",
                                                         width=250, parent=self))

                thread_reset = threading.Thread(reset_def())
                thread_reset.start()

            except subprocess.CalledProcessError:
                af.MessageBox(title="Error", message="Something went wrong!\nTry running as Admin.",
                              parent=self, height=110)

        def add_dns():
            af.show_toplevel(self, DnsInputWindow())

        def settingsOpen():
            self.toplevel_window = None
            af.show_toplevel(self, SettingsWindow())

        self.frame = AppFrame(self, fg_color="transparent")
        self.frame.grid(row=0, columnspan=3, sticky="news", pady=(20, 20), padx=20)

        combo_list = []
        combo_list.extend(dns_list)
        combo_list.insert(0, "Fastest")
        combo_list.insert(1, "Current")

        self.combobox = customtkinter.CTkComboBox(self, values=combo_list, command=change_dns_values, font=font_widget)
        self.combobox.grid(row=1, column=0, pady=(0, 10), padx=(30, 0), columnspan=2, sticky="ew")

        add_button = customtkinter.CTkButton(self, text="+", width=40, command=add_dns)
        add_button.grid(row=1, column=2, pady=(0, 10), padx=(20, 30), sticky="ew")

        self.set_button = customtkinter.CTkButton(self, text="Set DNS", command=set_dns, font=font_widget)
        self.set_button.grid(row=2, column=0, pady=(0, 20), padx=(30, 0), sticky="ew")
        self.set_button.configure(state="disabled")
        settings_button = customtkinter.CTkButton(self, text="⚙", width=30, command=settingsOpen)
        settings_button.grid(row=2, column=1, pady=(0, 20), padx=(20, 0),  sticky="ew")

        reset_button = customtkinter.CTkButton(self, text="Reset", width=30, command=reset_dns,
                                              font=("Cascadia Code", 12, "normal"))
        reset_button.grid(row=2, column=2, pady=(0, 20), padx=(10, 30), sticky="ew")

    def updateComboBox(self):
        self.combobox.configure(values=dns_list)

    def configFileInfo(self):
        af.MessageBox(title="Info!", message="Config File has been reset",
                      height=100, width=250, parent=self).wait_window()
        af.restart_program()

    def dnsFileInfo(self):
        af.MessageBox(title="Info!", message="DNS file was not found\n\nit is now replaced",
                      height=150, width=250, parent=self).wait_window()
        af.restart_program()

    def check_adapter(self):
        af.MessageBox(title="Info!", message=f"The selected adapter is unavailable!\n\n{adapter_name} been selected",
                      width=250, height=130, parent=self).wait_window()
        af.restart_program()

    def get_fastest(self):
        global primary_dns, secondary_dns, dns_list, dns_dict, dns_name

        statusText = "Finding Fastest"
        self.after(200, lambda: self.frame.pingResult.set(statusText))
        self.combobox.set("Pinging...")
        self.combobox.configure(state="disabled")
        self.set_button.configure(state="disabled")

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
            def get_fastest_dns():
                global dns_name, primary_dns, secondary_dns

                resultList = [0]
                fastest = 99999999
                fastestName = ""
                for name in dns_list:
                    ip = dns_dict[name][0]
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
                dns_name = fastestName
                primary_dns = dns_dict[fastestName][0]
                secondary_dns = dns_dict[fastestName][1]

                self.frame.frameUpdate(pingBool=False)
                self.after(250, lambda: self.frame.pingResult.set(f"Ping: {fastest}"))
                self.set_button.configure(state="normal")
                self.combobox.configure(state="normal")
                self.combobox.set(fastestName)

            get_fastest_thread = threading.Thread(target=get_fastest_dns)
            get_fastest_thread.start()

        except Exception as e:
            print(e)
            self.after(200, lambda: self.frame.pingResult.set("Couldn't get Fastest"))
            self.combobox.set("Select DNS")

    def get_current_dns(self):
        try:

            def current():
                global primary_dns, secondary_dns

                emptyList = []
                res = subprocess.run(["netsh", "interface", "ipv4", "show", "dnsservers", adapter_name],
                                     capture_output=True, text=True, check=True, shell=True).stdout
                pattern = (r'\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|'
                           r'[1-9]?[0-9])\b')

                match = re.findall(pattern, str(res))
                if match != emptyList:
                    primary_dns = match[0]

                    if len(match) != 1:
                        secondary_dns = match[1]

                    else:
                        secondary_dns = "0.0.0.0"

                    self.after(300, lambda: self.frame.frameUpdate(pingBool=True))
                    self.after(100, lambda: self.combobox.set("Current DNS"))

                else:
                    secondary_dns = "0.0.0.0"
                    self.after(100, lambda: self.combobox.set("Current DNS"))

            currentThread = threading.Thread(target=current)
            currentThread.start()

        except Exception as e:
            print(e)
            self.after(300, lambda: self.frame.pingResult.set("Ping: 0"))
            primary_dns = "0.0.0.0"
            secondary_dns = "0.0.0.0"
            self.after(300, lambda: self.frame.frameUpdate(pingBool=False))
            self.after(100, lambda: self.combobox.set("Current DNS"))


# the Information Frame
class AppFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.pingResult = customtkinter.StringVar()
        self.after(200, self.pingResult.set(value="Ping: 0"))

        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)
        label1 = customtkinter.CTkLabel(self, text="PRIMARY DNS:", font=fontH)
        label1.grid(row=0, column=0, pady=(10, 0), sticky="ew")
        self.label_primary = customtkinter.CTkLabel(self, text=primary_dns, font=font)
        self.label_primary.grid(row=1, pady=(0, 0))
        label2 = customtkinter.CTkLabel(self, text="SECONDARY DNS:", font=fontH)
        label2.grid(row=2, columnspan=3, pady=(0, 0))
        self.label_secondary = customtkinter.CTkLabel(self, text=secondary_dns, font=font)
        self.label_secondary.grid(row=3, columnspan=3, pady=(0, 0))
        self.label_ping = customtkinter.CTkLabel(self, textvariable=self.pingResult, font=font, text="")
        self.label_ping.grid(row=4, columnspan=3, pady=(20, 5), padx=(0, 0))
        self.label_ping.grid(row=4, columnspan=3, pady=(20, 5), padx=(0, 0))

    def frameUpdate(self, pingBool=True):
        self.label_primary.configure(text=primary_dns)

        if af.is_valid_ip(str(secondary_dns)):
            self.label_secondary.configure(text=secondary_dns)
        else:
            self.label_secondary.configure(text="0.0.0.0")

        if pingBool:
            self.pingResult.set("Pinging...")
            af.start_threading(af.get_ping_frame, ip=primary_dns, result=self.pingResult)


# Add DNS window
class DnsInputWindow(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.iconbitmap(icon_path)
        self.geometry(af.center_window(app, 200, 300, centerType='parent'))
        self.title("Add")
        self.toplevel_window = None
        self.grab_set()
        self.resizable(False, False)
        self.attributes("-toolwindow", True)

        # Grid Configuration
        # Columns
        self.grid_columnconfigure(0, weight=3)
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
                for i in dns_list:
                    if i == name:
                        af.MessageBox(title="Error", message="The name has already been used!", width=250, parent=self)
                        return

                with open(dns_file_path, mode='a', newline='') as dnsFile:
                    writer = csv.writer(dnsFile)
                    writer.writerow([name, prDns, scDns])
                    af.MessageBox(title="Done!", message="The DNS has been added!", width=250, parent=self)
                handle_dns_table()
                app.updateComboBox()
                name_entry.delete(0, customtkinter.END)
                prDns_entry.delete(0, customtkinter.END)
                if scDns_entry.get() != "":
                    scDns.delete(0, customtkinter.END)

        label1 = customtkinter.CTkLabel(self, text="Add Custom DNS", font=font_widget)
        label1.grid(row=0, pady=(10, 0))
        name_entry = customtkinter.CTkEntry(self, placeholder_text="Name", font=font_widget)
        name_entry.grid(row=1)
        prDns_entry = customtkinter.CTkEntry(self, placeholder_text="Primary", font=font_widget)
        prDns_entry.grid(row=2)
        scDns_entry = customtkinter.CTkEntry(self, placeholder_text="Secondary", font=font_widget)
        scDns_entry.grid(row=3)

        saveDns_Button = customtkinter.CTkButton(self, text="Save", command=save_dns, font=font_widget)
        saveDns_Button.grid(row=4, pady=10)


# Settings Window
class SettingsWindow(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()

        settingsFont = ("Cascadia Code", 12, "normal")

        self.iconbitmap(icon_path)
        self.geometry(af.center_window(app, 300, 450, centerType='parent'))
        self.title("Settings")
        self.toplevel_window = None
        self.grab_set()
        self.resizable(False, False)
        self.attributes("-toolwindow", True)

        self.radio_var_mode = customtkinter.IntVar(value=0)
        self.radio_var_theme = customtkinter.IntVar(value=0)
        self.radio_var_startup = customtkinter.IntVar(value=0)

        # Grid Configuration
        # Columns
        self.grid_columnconfigure((0, 1, 2), weight=1)
        # Rows
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1)
        self.iconbitmap(icon_path)

        global adapter_list, adapter_name
        adapter_list = af.get_adapters()

        def set_adapter(choice):
            global adapter_name
            adapter_name = choice

        def open_folder():
            os.system(f"start {app_local_folder}")

        def close_window():
            self.grab_release()
            self.withdraw()

        label1 = customtkinter.CTkLabel(self, text="Select Internet Adapter:", font=font_widget)
        label1.grid(row=0, columnspan=3, pady=(15, 0))
        self.combobox = customtkinter.CTkComboBox(self, values=af.get_adapters(), command=set_adapter, font=font_widget)
        if adapter_name not in adapter_list:
            adapter_name = adapter_list[0]

        self.combobox.set(adapter_name)
        self.combobox.grid(row=1, columnspan=3)

        label2 = customtkinter.CTkLabel(self, text="Appearance Mode:", font=font_widget)
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

        label2 = customtkinter.CTkLabel(self, text="Theme Color:", font=font_widget)
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

        label2 = customtkinter.CTkLabel(self, text="Startup:", font=font_widget)
        label2.grid(row=6, columnspan=3, pady=(10, 0))
        self.startup_radio1 = customtkinter.CTkRadioButton(self, text="Fastest DNS", value=0,
                                                           command=self.startup_radio, variable=self.radio_var_startup,
                                                           radiobutton_width=rb_Size, radiobutton_height=rb_Size,
                                                           font=settingsFont)
        self.startup_radio1.grid(row=7, column=0, padx=(25, 10), sticky="ew", columnspan=2)
        self.startup_radio2 = customtkinter.CTkRadioButton(self, text="Current DNS", value=1,
                                                           command=self.startup_radio, variable=self.radio_var_startup,
                                                           radiobutton_width=rb_Size, radiobutton_height=rb_Size,
                                                           font=settingsFont)
        self.startup_radio2.grid(row=7, column=1, padx=(65, 10), sticky="ew", columnspan=2)

        open_dns_file = customtkinter.CTkButton(self, text="Files", command=open_folder, font=font_widget)
        open_dns_file.grid(row=8, column=0, padx=10, pady=10)

        self.check_version = customtkinter.CTkButton(self, text="Update", command=self.check_version, font=font_widget)
        self.check_version.grid(row=8, column=1, padx=10, pady=10)

        about_button = customtkinter.CTkButton(self, text="Details", command=self.app_details, font=font_widget)
        about_button.grid(row=8, column=2, padx=10, pady=10)

        saveDns_Button = customtkinter.CTkButton(self, text="Save", command=self.save_settings, font=font_widget,
                                                 width=100)
        saveDns_Button.grid(row=9, columnspan=3, padx=(10, 150), pady=(5, 15))

        cancel_button = customtkinter.CTkButton(self, text="Cancel", command=close_window, font=font_widget,
                                                width=100)
        cancel_button.grid(row=9, columnspan=3, padx=(150, 10), pady=(5, 15))

        with open(config_path, 'r') as jFile:
            settingsDict = json.load(jFile)

        match settingsDict['Mode']:
            case "system":
                self.mode_radio1.select()
            case "dark":
                self.mode_radio2.select()
            case "light":
                self.mode_radio3.select()

        match settingsDict['Theme']:
            case s if "theme-purple.json" in s:
                self.theme_radio1.select()
            case  s if "theme-blue.json" in s:
                self.theme_radio2.select()
            case  s if "theme-retro.json" in s:
                self.theme_radio3.select()

        match settingsDict['Startup']:
            case "Fastest":
                self.startup_radio1.select()
            case "Current":
                self.startup_radio2.select()

    # Functions
    def save_settings(self):
        global adapter_name, appearance_mode, app_theme, config_path
        try:
            with open(config_path, 'r') as jFile:
                settingsDict = json.load(jFile)

            settingsDict['Adapter'] = adapter_name
            settingsDict['Mode'] = self.mode_radio()
            settingsDict['Theme'] = self.theme_radio()
            settingsDict['Startup'] = self.startup_radio()

            with open(config_path, 'w') as jFile:
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
                modeVar = appearance_mode
        return modeVar

    def theme_radio(self):
        match self.radio_var_theme.get():
            case 0:
                themeVar = purple_theme
            case 1:
                themeVar = blue_theme
            case 2:
                themeVar = retro_theme
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
                startVar = on_startup

        return startVar

    def check_version(self):
        try:
            latest = ""

            def check_thread():
                self.check_version.configure(text="Checking")
                nonlocal latest
                temp = requests.get(github_version_file)
                temp.raise_for_status()
                latest = temp.text.strip()
                if latest != VERSION:
                    self.check_version.configure(text="Update")
                    response = af.MessageBox(parent=self, title="Info",
                                             message="New update is available!\nOpen github?", msgType=1, width=250,
                                             height=110).get_input()
                    if response is True:
                        webbrowser.open(github_release)

                    else:
                        af.MessageBox().destroy()
                else:
                    self.check_version.configure(text="Update")
                    af.MessageBox(parent=self, title="Info", message="You have the latest version")

            thread = threading.Thread(target=check_thread)
            thread.start()

        except Exception as e:
            print(e)
            af.MessageBox(parent=self, title="Info", message="Update check failed!")
            self.check_version.configure(text="Update")

    def app_details(self):
        response = af.MessageBox(parent=self, title="Details", message=f"Version: {VERSION}\n\nMade by Dani Abedini",
                                 msgType=1, true_button="Github", false_button="Close", height=150,
                                 width=230).get_input()
        if response:
            webbrowser.open(github_main)


# Get and Update DNS table
def handle_dns_table():
    global dns_dict, dns_list, dns_file_path
    dns_dict = {}
    dns_list = []

    try:
        if os.path.isfile(dns_file_path):

            with open(dns_file_path, mode='r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    dns_dict[row[0]] = [row[1], row[2]]
                    dns_list.append(row[0])

        else:
            with open(dns_file_path, mode='w', newline='') as dnsFile:
                writer = csv.writer(dnsFile)
                writer.writerow(['403', "10.202.10.202", "10.202.10.102"])
                writer.writerow(['Shecan', "178.22.122.100", "185.51.200.2"])
                writer.writerow(['Electro', "78.157.42.101", "78.157.42.100"])
                writer.writerow(['Google', "8.8.8.8", "8.8.4.4"])
                writer.writerow(['CloudFlair', "1.1.1.1", "1.0.0.1"])
                writer.writerow(['Quad9', "9.9.9.9", "149.112.112.112"])
                writer.writerow(['OpenDNS', "208.67.222.222", "208.67.220.220"])

            with open(dns_file_path, mode='r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    dns_dict[row[0]] = [row[1], row[2]]
                    dns_list.append(row[0])
            App().dnsFileInfo()

    except Exception as e:
        print(e)
        af.MessageBox(title="Error", message="Somthing went wrong!")


# Handle config.json file
def handle_config():
    global adapter_name, settings, app_theme, appearance_mode, config_path, on_startup

    try:
        if os.path.isfile(config_path):
            with open(config_path, 'r') as jsonFile:
                settings = json.load(jsonFile)

            adapter_name = settings['Adapter']
            appearance_mode = settings['Mode']
            app_theme = settings['Theme']
            on_startup = settings['Startup']

        adapterCheck = adapter_list.count(adapter_name) == 0

        if os.path.isfile(config_path) is False or adapterCheck:
            adapter_name = adapter_list[0]
            settings = {
                'Adapter': adapter_name,
                'Mode': appearance_mode,
                'Theme': purple_theme,
                'Startup': on_startup
            }

            with open(config_path, 'w') as jsonFile:
                json.dump(settings, jsonFile)

            if adapterCheck:
                App().check_adapter()
            else:
                App().configFileInfo()
    except Exception as e:
        af.MessageBox(title="Error", message="Something went wrong!\nCouldn't handle config.")
        print(e)

    customtkinter.set_appearance_mode(appearance_mode)
    customtkinter.set_default_color_theme(app_theme)


handle_dns_table()
handle_config()
app = App()


app.protocol("WM_DELETE_WINDOW", af.on_closing)
app.mainloop()
