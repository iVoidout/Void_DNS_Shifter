from ping3 import ping
import threading

choice = "Fastest"
dnsDict = {
    '403': "10.202.10.202",
    'Shecan': "178.22.122.100",
    'Google': "8.8.8.8",
    'CF': "1.1.1.1"
}
dnsList = ['403', 'Shecan', 'Google', 'CF']

if choice == "Fastest":

    resultList = [0]
    fastest = 99999999
    fastestName = ""

    def pinging():
        global fastest, fastestName, resultList
        for name in dnsList:
            ip = dnsDict[name]

            latency = ping(ip)
            if latency is not None:
                latency = round(latency * 1000, 0)
                resultList[0] = int(latency)
                print(latency)
            else:
                resultList[0] = -1

            latency = resultList[0]
            if latency < fastest and latency != -1:
                fastest = latency
                fastestName = name

        print(f"Name: {fastestName} Ping: {fastest}")

    thread = threading.Thread(target=pinging)
    thread.start()




