import socket
import os
from ping3 import ping
from customtkinter import CTkToplevel, CTkButton, CTkLabel
import sys
import threading
from psutil import net_if_addrs


fontH = ("Cascadia Code", 20, "bold")
font = ("Cascadia Code", 18, "normal")
fontWidget = ("Cascadia Code", 14, "normal")


def center_window(instance, width, height, centerType='screen'):

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
        return f"{width}x{height}+{posx}+{posy}"


def show_toplevel(self, tl_window):
    if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
        self.toplevel_window = tl_window
    else:
        tl_window.focus(self)


# Message Box
class MessageBox(CTkToplevel):
    def __init__(self, parent=None, title="Info!", message="", buttontext="Ok", width=200, height=100,
                 msgType=0, true_button="Yes", false_button="No"):
        super().__init__()

        #
        self.title(title)
        self.geometry(center_window(self if parent is None else parent, width=width, height=height,
                                    centerType='parent'))
        self.attributes('-topmost', 'true')
        self.grab_set()
        self.focus()
        self.resizable(False, False)
        self.userInput = None
        self.iconbitmap(resource_path(r"logo.ico"))

        # Grid Configuration
        # Columns
        self.grid_columnconfigure((0, 1), weight=1)
        # Rows
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)

        message_label = CTkLabel(self, text=message)
        message_label.grid(row=0, pady=(10, 10), padx=20, sticky="news", columnspan=2)
        if msgType == 0:
            msgbox_button = CTkButton(self, text=buttontext, command=self.button_ok)
            msgbox_button.grid(row=1, pady=(0, 20), padx=30, sticky="news", columnspan=2)
        if msgType == 1:
            msgbox_yes = CTkButton(self, text=true_button, command=self.button_yes)
            msgbox_yes.grid(row=1,  column=0, pady=(0, 20), padx=20, sticky="ew")
            msgbox_no = CTkButton(self, text=false_button, command=self.button_no)
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


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)


def is_valid_ip(ip_str):
    try:
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

