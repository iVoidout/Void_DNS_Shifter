@echo off
cd /d E:\Programming\dnsChanger
pyinstaller --noconfirm --onefile --windowed --icon "E:\Programming\dnsChanger\logo.ico" --name "DNS Changer" --clean --noupx --hide-console "hide-early" "E:\Programming\dnsChanger\main.py" --distpath "E:\Programming\dnsChanger\output" --workpath "E:\Programming\dnsChanger\output\temp" --add-data "E:\Programming\dnsChanger\logo.ico;." --specpath"E:\Programming\dnsChanger\output\temp"
TIMEOUT 5
