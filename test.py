import subprocess
import re

adapterName = "Ethernet"
res = subprocess.run(["netsh", "interface", "ipv4", "show", "dnsservers", adapterName],
               capture_output=True, text=True, check=True).stdout
pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\b'

match = re.findall(pattern, str(res))

print(res)
print(match[0])
