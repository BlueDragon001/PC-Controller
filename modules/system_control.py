from flask import jsonify
import platform
import os
import subprocess
import psutil
import time
import ctypes

def get_processes():
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            cpu_percent = p.cpu_percent()
            time.sleep(0.1)
            cpu_percent = p.cpu_percent()
            processes.append({
                "pid": p.pid,
                "name": p.name(),
                "cpu": cpu_percent
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    processes.sort(key=lambda x: x['cpu'], reverse=True)
    return processes

def system_commands(action):
    try:
        if action == "shutdown":
            if platform.system() == "Windows":
                os.system("shutdown /s /t 0")
            else:
                os.system("shutdown -h now")
        elif action == "restart":
            if platform.system() == "Windows":
                os.system("shutdown /r /t 0")
            else:
                os.system("reboot")
        elif action == "sleep":
            if platform.system() == "Windows":
                subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"])
            else:
                os.system("systemctl suspend")
        elif action == "lock":
            if platform.system() == "Windows":
                ctypes.windll.user32.LockWorkStation()
            else:
                os.system("gnome-screensaver-command -l")
        return True
    except Exception as e:
        return str(e)
