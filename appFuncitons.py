import socket
import os
from ping3 import ping
import customtkinter
import sys
import threading
from psutil import net_if_addrs
import re

fontH = ("Cascadia Code", 20, "bold")
font = ("Cascadia Code", 18, "normal")
fontWidget = ("Cascadia Code", 14, "normal")


def center_window(instance, width, height, centerType='screen', offsetx=0, offsety=0):

    if centerType == "screen":
        sw = int(instance.winfo_screenwidth())
        sh = int(instance.winfo_screenheight())
        posx = (sw - width) // 2
        posy = (sh - height) // 2

        return f"{width}x{height}+{posx}+{posy}"

    elif centerType == "parent":
        geometry = instance.geometry()
        size, position = geometry.split('+', 1)
        x, y = position.split('+')
        x = int(x)
        y = int(y)
        sx, sy = size.split('x')
        sx = int(sx)
        sy = int(sy)
        posx = x + ((sx - width) // 2)
        posy = y + ((sy - height) // 2)
        return f"{width}x{height}+{posx + offsetx}+{posy + offsety}"


def show_toplevel(self, tl_window):
    if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
        self.toplevel_window = tl_window
    else:
        tl_window.focus(self)


class Bodge(customtkinter.CTk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.geometry(center_window(self, centerType="screen", height=0, width=0))
        self.overrideredirect(True)


# Message Box
class MessageBox(customtkinter.CTkToplevel):
    def __init__(self, parent=None, title="Info!", message="", button_text="Ok", width=200, height=100,
                 msgType="ok", true_button="Yes", false_button="No"):
        super().__init__(parent)

        # Configuration
        self.title(title)
        self.geometry(center_window(self if parent is None else parent, width=width, height=height,
                                    centerType="screen" if parent is None else "parent"))
        self.resizable(False, False)
        self.userInput = None
        self.attributes("-toolwindow", True)
        self.grab_set()
        self.focus()
        self.attributes('-topmost', 'true')
        customtkinter.set_default_color_theme(str(resource_path("theme-0.json")))

        # Grid Configuration
        # Columns
        self.grid_columnconfigure((0, 1), weight=1)
        # Rows
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)

        self.message_label = customtkinter.CTkLabel(self, text=message)
        self.message_label.grid(row=0, pady=(10, 10), padx=20, sticky="news", columnspan=2)
        if msgType == "ok":
            msgbox_button = customtkinter.CTkButton(self, text=button_text, command=self.button_ok)
            msgbox_button.grid(row=1, pady=(0, 20), padx=30, sticky="news", columnspan=2)
        if msgType == "yesno":
            msgbox_yes = customtkinter.CTkButton(self, text=true_button, command=self.button_yes)
            msgbox_yes.grid(row=1,  column=0, pady=(0, 20), padx=20, sticky="ew")
            msgbox_no = customtkinter.CTkButton(self, text=false_button, command=self.button_no)
            msgbox_no.grid(row=1, column=1,  pady=(0, 20), padx=20, sticky="ew")

    def button_ok(self):
        self.userInput = None
        self.grab_release()
        self.destroy()

    def button_yes(self):
        self.userInput = True
        self.grab_release()
        self.destroy()

    def button_no(self):
        self.userInput = False
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.wait_window(self)
        return self.userInput


class NewM(customtkinter.CTkToplevel):
    def __init__(self, title, message):
        super().__init__()
        self.geometry("300x300+0+300")
        self.title(title)

        self.message_label = customtkinter.CTkLabel(self, text=message)
        self.message_label.grid(row=0, pady=(10, 10), padx=20, sticky="news", columnspan=2)
        msgbox_button = customtkinter.CTkButton(self, text="nigga", command=self.button_ok)
        msgbox_button.grid(row=1, pady=(0, 20), padx=30, sticky="news", columnspan=2)

    def button_ok(self):
        self.destroy()


def show_test(title, meg):
    msg_box = NewM(title=title, message=meg)
    msg_box.grab_set()



def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)


def is_valid_ip(ip_str):
    try:
        pattern = (r'\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|'
                   r'[1-9]?[0-9])\b')
        emptyList = []
        match = re.findall(pattern, str(ip_str))
        if match == emptyList:
            return False

        socket.inet_aton(ip_str)
        return True
    except socket.error:
        return False


def close_app():
    sys.exit()


def get_ping_frame(ip, result):
    if is_valid_ip(ip):
        latency = ping(ip)
        if latency is not None:
            result.set(f"Ping: {latency * 1000:.0f}")
        else:
            result.set("Ping: N/A")
    else:
        result.set("Ping: N/A")


def start_threading(tTarget, ip, result):
    thread = threading.Thread(target=tTarget, args=(ip, result))
    thread.start()


def get_adapters():
    adapter_list = []
    adapters = net_if_addrs()
    for adapter_name, adapter_info in adapters.items():
        adapter_list.append(adapter_name)

    return adapter_list


def on_closing():
    sys.exit(0)


def makeAppData(folderName):
    local_appdata_path = os.getenv('LOCALAPPDATA')

    appLocalFolder = local_appdata_path + "\\" + folderName
    os.makedirs(appLocalFolder, exist_ok=True)

    return appLocalFolder


def get_platform():
    if sys.platform.startswith("win"):
        return 0
    if sys.platform.startswith("darwin"):
        return 1
    else:
        return 2


class TimeoutException(Exception):
    pass

