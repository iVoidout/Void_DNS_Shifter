@echo off
cd /d E:\Programming\dnsChanger
pyinstaller --noconfirm --onefile --windowed --icon "E:\Programming\dnsChanger\logo.ico" --name "Void DNS Shifter" --clean --noupx --hide-console "hide-early" "E:\Programming\dnsChanger\main.py" --distpath "E:\Programming\voidDnsShifter\output" --workpath "E:\Programming\dnsChanger\output\temp" --add-data "E:\Programming\dnsChanger\logo.ico;." --specpath "E:\Programming\dnsChanger\output\temp"
TIMEOUT 5
