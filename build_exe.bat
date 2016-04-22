echo "---- BUILD PROJECT icon=cpu_apps.ico"

rmdir build /s /Q
c:\Anaconda3\Scripts\pyinstaller.exe main.py --onefile --icon=cpu_apps.ico
move dist\main.exe dist\imitator_device.exe

