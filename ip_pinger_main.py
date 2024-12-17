import sys

import customtkinter
import ping3
from ping3 import ping
import csv
import os
import time
import appFuncitons as af
import threading
from datetime import datetime

ipDict = {}
ipList = []

avg_ping = 0
loss_packets = 0.0
max_ping = 0
packetsLost = 0
pingCount = 0

runPinging = False

main_font = ("Arial", 14, "normal")


def appFont(name="Arial", size=20, weight="normal"):
    return name, size, weight


def main_status(self, label, text="Error!", color="red"):
    label.configure(text=text)
    label.configure(text_color=color)
    self.after(1000, lambda: label.configure(text_color="white"))
    self.after(3000, lambda: label.configure(text="Ping: N/A"))


appFolder = af.makeAppData("VOIDSHIFTER")

ipFilePath = appFolder + "\\ipList.csv"


class App(customtkinter.CTk):
    def __init__(self, app_theme="theme-0.json", appearance_mode="system", parent=None, ip_address=None):
        super().__init__()
        stop_ping_event = threading.Event()
        customtkinter.set_default_color_theme(af.resource_path(app_theme))
        customtkinter.set_appearance_mode(appearance_mode)
        self.iconbitmap(af.resource_path("pinger_logo.ico"))
        self.geometry(af.center_window(self if parent is None else parent, 200, 300,
                                       centerType="screen" if parent is None else "parent", offsety=0))
        self.title("Ping")
        self.resizable(False, False)

        def get_ip_from_dns():
            if ip_address is not None:
                self.ip_entry.insert(0, ip_address)

        def run_ping():
            ping3.EXCEPTIONS = False
            global runPinging
            try:
                if runPinging is False:
                    ip = self.ip_entry.get()
                    if ip == "":
                        main_status(text="Enter IP", self=self, label=main_label)

                    elif af.is_valid_ip(ip) is False:
                        main_status(text="Invalid IP", self=self, label=main_label)

                    else:
                        def pinging():
                            global avg_ping, max_ping, loss_packets, pingCount, packetsLost
                            max_ping = 0
                            pingCount = 0
                            sumPing = 0
                            packetsLost = 0
                            while not stop_ping_event.is_set():
                                latency = ping(ip, timeout=1)
                                pingCount += 1

                                if latency is None:
                                    packetsLost += 1
                                else:
                                    latency = round(latency * 1000, 1)
                                    sumPing += latency

                                    if latency > 9999:
                                        main_label.configure(text_color="#a104c4")
                                        latency = 9999

                                    if latency > max_ping:
                                        max_ping = round(latency, 0)
                                        max_label.configure(text=f"Max: {max_ping:.0f}")

                                    if latency < 70:
                                        main_label.configure(text_color="#09ed5d")
                                    elif 70 < latency < 100:
                                        main_label.configure(text_color="yellow")
                                    elif 100 <= latency:
                                        main_label.configure(text_color="red")

                                    main_label.configure(text=f"Ping: {latency:.0f}")

                                avg_ping = round(sumPing / pingCount, 0)
                                avg_label.configure(text=f"Avg: {avg_ping:.0f}")
                                loss_packets = round((packetsLost / pingCount) * 100, 2)
                                loss_label.configure(text=f"Loss: {loss_packets:.1f}% "
                                                          f"({packetsLost} / {pingCount})")

                                if pingCount == (9999 if max_entry.get() == "" else int(max_entry.get())):
                                    if auto_check.get() == 1:
                                        add_log()
                                        for i in range(1, 11):
                                            time.sleep(1)
                                            main_label.configure(text=f"Running in {10 - i}s")

                                        pinging()

                                    else:
                                        stop_running()

                                time.sleep(0.5 if sleep_entry.get() == "" else float(sleep_entry.get()))

                        runPinging = True
                        run_button.configure(text="Stop")
                        stop_ping_event.clear()
                        pingThread = threading.Thread(target=pinging)
                        pingThread.start()
                else:
                    stop_running()

            except ping3.errors as e:
                print(e)
                pass

            except Exception as e:
                print(f"Error: {e}")

        def setIp(choice):
            self.ip_entry.delete(0, customtkinter.END)
            self.ip_entry.insert(0, ipDict[choice][0])

            stop_running()
            main_label.configure(text="Ping: N/A")
            self.after(301, lambda: main_label.configure(text_color="gray92"))
            avg_label.configure(text="Avg: 0")
            max_label.configure(text="Max: 0")
            loss_label.configure(text="Loss: 0% (0 / 0)")

        def saveIp():
            try:
                ipaddress = self.ip_entry.get()
                ipName = ip_combobox.get()
                if af.is_valid_ip(ipaddress) is False:
                    main_status(text="Invalid IP", self=self, label=main_label)
                elif ipName == "":
                    main_status(text="Enter a name", self=self, label=main_label)

                else:
                    for i in ipList:
                        if i == ipName:
                            main_status(text="Name already used!", self=self, label=main_label)
                            return

                    with open(ipFilePath, mode='a', newline='') as dnsFile:
                        writer = csv.writer(dnsFile)
                        writer.writerow([ipName, ipaddress])
                    handle_ip_table()
                    ip_combobox.configure(values=ipList)
                    main_label.configure(text="Added!")
                    self.after(3000, lambda: main_label.configure(text="Ping: N/A"))
            except Exception as e:
                print(e)

        def add_log():
            if ip_combobox.get() == "" or ip_combobox.get().lower() == "select":
                main_status(text="Invalid Name", self=self, label=main_label)
            else:
                serverName = ip_combobox.get()
                timeNow = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

                if os.path.isfile("logs.csv") is False:
                    with open("logs.csv", mode="a", newline="") as log:
                        writer = csv.writer(log)
                        writer.writerow(["Time", "Server", "Average", "Max Ping", "Loss %", "Packet Count"])
                        writer.writerow([timeNow, serverName, avg_ping, max_ping, loss_packets,
                                         f"{packetsLost} of {pingCount}"])
                        main_label.configure(text="Logged!")
                        main_label.configure(text_color="Yellow")
                        self.after(1000, lambda: main_label.configure(text_color="white"))
                else:
                    with open("logs.csv", mode="a", newline="") as log:
                        writer = csv.writer(log)
                        writer.writerow([timeNow, serverName, avg_ping, max_ping, loss_packets,
                                         f"{packetsLost} of {pingCount}"])
                        main_label.configure(text="Logged!")
                        main_label.configure(text_color="Yellow")

        def char_limiter_ip(event):
            count = len(self.ip_entry.get())
            if count >= 15 and event.keysym not in {'BackSpace', 'Delete', 'Left', 'Right'}:
                return 'break'

        def char_limiter_sleep(event):
            count = len(sleep_entry.get())
            if count >= 3 and event.keysym not in {'BackSpace', 'Delete', 'Left', 'Right'}:
                return 'break'

        def char_limiter_max(event):
            count = len(max_entry.get())
            if count >= 4 and event.keysym not in {'BackSpace', 'Delete', 'Left', 'Right'}:
                return 'break'

        def clear_all():
            global max_ping, avg_ping, loss_packets
            max_ping = 0
            avg_ping = 0
            loss_packets = 0

            self.ip_entry.delete(0, customtkinter.END)
            self.ip_entry.configure(placeholder_text="127.0.0.1")
            ip_combobox.set("Select")

            max_entry.delete(0, customtkinter.END)
            max_entry.configure(placeholder_text="100")

            sleep_entry.delete(0, customtkinter.END)
            sleep_entry.configure(placeholder_text="1")

            stop_running()
            main_label.configure(text="Ping: N/A")
            self.after(301, lambda: main_label.configure(text_color="gray92"))
            avg_label.configure(text="Avg: 0")
            max_label.configure(text="Max: 0")
            loss_label.configure(text="Loss: 0% (0 / 0)")


        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure((1, 2, 3, 4), weight=1)

        # Details
        detail_frame = customtkinter.CTkFrame(self)
        detail_frame.grid(row=0, pady=10)
        detail_frame.grid_columnconfigure((0, 1, 3), weight=1)
        detail_frame.grid_rowconfigure((0, 1), weight=1)
        detail_frame.configure(fg_color="transparent")
        main_label = customtkinter.CTkLabel(detail_frame, text="Ping: N/A", font=appFont(size=20, weight="bold"))
        main_label.grid(row=0, sticky="", columnspan=3, pady=(0, 5))
        avg_label = customtkinter.CTkLabel(detail_frame, text="Avg: 0", font=main_font)
        avg_label.grid(row=1, sticky="", column=0, padx=5)
        max_label = customtkinter.CTkLabel(detail_frame, text="Max: 0", font=main_font)
        max_label.grid(row=1, sticky="", column=1, padx=5)
        loss_label = customtkinter.CTkLabel(detail_frame, text="Loss: 0% (0 / 0)", font=main_font)
        loss_label.grid(row=2, sticky="", columnspan=2, padx=5)

        self.ip_entry = customtkinter.CTkEntry(self, placeholder_text="127.0.0.1", width=122, font=("", 15, "normal"))
        self.ip_entry.grid(row=1, pady=(0, 0), padx=(0, 40), sticky="")
        self.ip_entry.bind('<KeyPress>', char_limiter_ip)
        self.ip_entry.bind('<KeyRelease>', char_limiter_ip)
        get_ip_from_dns()

        add_button = customtkinter.CTkButton(self, text="+", width=30, command=saveIp)
        add_button.grid(row=1, pady=(0, 0), padx=(130, 0), sticky="")

        ip_combobox = customtkinter.CTkComboBox(self, values=ipList, command=setIp, width=162)
        ip_combobox.set("Select")
        ip_combobox.grid(row=2, pady=(0, 0), sticky="")

        sleep_entry = customtkinter.CTkEntry(self, placeholder_text="1", width=40, font=("", 15, "normal"))
        sleep_entry.grid(row=3, pady=(0, 0), padx=(0, 122), sticky="")
        sleep_entry.bind('<KeyPress>', char_limiter_sleep)
        sleep_entry.bind('<KeyRelease>', char_limiter_sleep)

        max_entry = customtkinter.CTkEntry(self, placeholder_text="100", width=75, font=("", 15, "normal"))
        max_entry.grid(row=3, pady=(0, 0), padx=(20, 0), sticky="")
        max_entry.bind('<KeyPress>', char_limiter_max)
        max_entry.bind('<KeyRelease>', char_limiter_max)
        auto_check = customtkinter.CTkCheckBox(self, text="")
        auto_check.grid(row=3, pady=(0, 0), padx=(156, 0))
        run_button = customtkinter.CTkButton(self, text="Run", command=run_ping, width=80)
        run_button.grid(row=4, pady=(15, 15), sticky="s", padx=(0, 90))

        log_button = customtkinter.CTkButton(self, text="Log", command=add_log, width=35)
        log_button.grid(row=4, pady=(15, 15), sticky="s", padx=(45, 0))

        clear_button = customtkinter.CTkButton(self, text="Clear", command=clear_all, width=35)
        clear_button.grid(row=4, pady=(15, 15), sticky="s", padx=(140, 0))

        def stop_running():
            global runPinging
            runPinging = False
            stop_ping_event.set()
            run_button.configure(text="Run")
            self.after(300, lambda: main_label.configure(text_color="gray"))


def handle_ip_table():
    global ipDict, ipList, ipFilePath
    ipDict = {}
    ipList = []

    try:
        if os.path.isfile(ipFilePath):

            with open(ipFilePath, mode='r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    ipDict[row[0]] = [row[1]]
                    ipList.append(row[0])

        else:
            with open(ipFilePath, mode='w', newline='') as dnsFile:
                writer = csv.writer(dnsFile)
                writer.writerow(['Google', "8.8.8.8"])
                writer.writerow(['CloudFlare', "1.1.1.1"])
                writer.writerow(['Hunt:Showdown (RU)', "77.223.103.204"])
                writer.writerow(['Valorant (BH)', "99.83.199.240"])

            with open(ipFilePath, mode='r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    ipDict[row[0]] = [row[1]]
                    ipList.append(row[0])

    except Exception as e:
        print(e)
        af.MessageBox(title="Error", message="Somthing went wrong!")


handle_ip_table()

if __name__ == "__main__":
    main = App()
    main.mainloop()
