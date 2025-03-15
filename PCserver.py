from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, Response
import hashlib
import json
import functools
import webbrowser
import psutil
import os
import platform
import subprocess
import pyautogui
import socket
import shutil
import time
import ctypes
from pywinauto import Application
import win32clipboard
import wmi
import screen_brightness_control as sbc
from pynput.keyboard import Key, Controller
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import win32api
import win32con
import winerror
import win32file
import win32gui
import win32process
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import mimetypes
import io
from waitress import serve
import logging
import ctypes
from ctypes import windll
import sys
from modules.auth import login_required, load_users, hash_password
from modules.display_control import set_brightness_dx, get_brightness_methods
from modules.utils import setup_logging
from modules.system_control import get_processes, system_commands
from modules.file_ops import get_drive_list, get_directory_contents

# Setup logging
setup_logging()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure random key

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
   
    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required"})
    
    # Hash the password
    hashed_password = hash_password(password)
    print(f"Debug - Hashed password: {hashed_password}")  # For debugging
    
    users = load_users()
    for user in users:
        print(f"Debug - User: {user['password']} HashedPassword {hashed_password}")  # For debugging
        if user['username'] == username and user['password'] == hashed_password:
            session['logged_in'] = True
            session['username'] = username
            return jsonify({"status": "success"})
    
    return jsonify({"status": "error", "message": "Invalid credentials"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/processes', methods=['GET'])
@login_required
def get_process_list():
    return jsonify(get_processes())

@app.route('/explorer', methods=['POST'])
@login_required
def file_explorer():
    action = request.json.get('action')
    path = request.json.get('path', '')
    
    if not path:
        return jsonify({"status": "success", "items": get_drive_list()})
        
    path = os.path.normpath(path)
    try:
        if action == "list":
            return jsonify({"status": "success", "items": get_directory_contents(path)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/open_url', methods=['POST'])
@login_required
def open_url():
    url = request.json.get('url')
    if url:
        webbrowser.open(url)
        return jsonify({"status": "success", "message": f"Opened {url}"})
    return jsonify({"status": "error", "message": "No URL provided"})

@app.route('/kill_process', methods=['POST'])
@login_required
def kill_process():
    pid = request.json.get('pid')
    try:
        p = psutil.Process(pid)
        p.terminate()
        return jsonify({"status": "success", "message": f"Terminated {p.name()}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/shutdown', methods=['POST'])
@login_required
def shutdown():
    if platform.system() == "Windows":
        os.system("shutdown /s /t 0")
    else:
        os.system("shutdown -h now")
    return jsonify({"status": "success", "message": "Shutting down..."})

@app.route('/restart', methods=['POST'])
@login_required
def restart():
    if platform.system() == "Windows":
        os.system("shutdown /r /t 0")
    else:
        os.system("reboot")
    return jsonify({"status": "success", "message": "Restarting..."})

@app.route('/volume', methods=['POST'])
@login_required
def set_volume():
    level = request.json.get('level')
    try:
        if platform.system() == "Windows":
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            # Convert percentage to scalar value between 0 and 1
            volume.SetMasterVolumeLevelScalar(level / 100, None)
            return jsonify({"status": "success", "message": f"Volume set to {level}%"})
        else:
            subprocess.run(["amixer", "sset", "Master", f"{level}%"])
            return jsonify({"status": "success", "message": f"Volume set to {level}%"})
    except Exception as e:
        logging.error(f"Volume control error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/mouse_move', methods=['POST'])
@login_required
def move_mouse():
    x = request.json.get('x')
    y = request.json.get('y')
    pyautogui.moveTo(x, y)
    return jsonify({"status": "success", "message": f"Mouse moved to {x}, {y}"})

@app.route('/key_press', methods=['POST'])
@login_required
def press_key():
    key = request.json.get('key')
    pyautogui.press(key)
    return jsonify({"status": "success", "message": f"Key {key} pressed"})

@app.route('/system_info', methods=['GET'])
@login_required
def system_info():
    info = {
        "OS": platform.system(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "IP Address": socket.gethostbyname(socket.gethostname())
    }
    return jsonify(info)

@app.route('/storage', methods=['GET'])
@login_required
def storage_info():
    total, used, free = shutil.disk_usage("/")
    return jsonify({
        "Total": f"{total // (1024**3)} GB",
        "Used": f"{used // (1024**3)} GB",
        "Free": f"{free // (1024**3)} GB"
    })

@app.route('/sleep', methods=['POST'])
@login_required
def sleep():
    try:
        if platform.system() == "Windows":
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"])
        else:
            os.system("systemctl suspend")
        return jsonify({"status": "success", "message": "PC going to sleep"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/lock', methods=['POST'])
@login_required
def lock_pc():
    try:
        if platform.system() == "Windows":
            ctypes.windll.user32.LockWorkStation()
        else:
            os.system("gnome-screensaver-command -l")
        return jsonify({"status": "success", "message": "PC locked"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/display', methods=['POST'])
@login_required
def control_display():
    action = request.json.get('action')
    try:
        if action == "off":
            if platform.system() == "Windows":
                subprocess.run(["nircmd.exe", "monitor", "off"])
        elif action == "on":
            if platform.system() == "Windows":
                subprocess.run(["nircmd.exe", "monitor", "on"])
        elif action == "brightness":
            level = request.json.get('level', 50)
            success = False
            error_messages = []
            
            # Try all available brightness methods
            for method_name, monitors in get_brightness_methods():
                try:
                    if method_name == "sbc":
                        for monitor in monitors:
                            sbc.set_brightness(int(level), display=monitor['name'])
                        success = True
                        break
                    elif method_name == "wmi":
                        for monitor in monitors:
                            monitor.WmiSetBrightness(int(level), 0)
                        success = True
                        break
                except Exception as e:
                    error_messages.append(f"{method_name} method failed: {str(e)}")
            
            # Try DirectX method as last resort
            if not success and set_brightness_dx(level):
                success = True
            
            if success:
                return jsonify({"status": "success", "message": f"Brightness set to {level}%"})
            return jsonify({
                "status": "error",
                "message": "All brightness control methods failed",
                "details": error_messages
            })
                
        return jsonify({"status": "success", "message": f"Display {action} successful"})
    except Exception as e:
        logging.error(f"Display control error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/audio', methods=['POST'])
@login_required
def control_audio():
    action = request.json.get('action')
    keyboard = Controller()
    try:
        if action == "mute":
            keyboard.press(Key.media_volume_mute)
        elif action == "next":
            keyboard.press(Key.media_next)
        elif action == "previous":
            keyboard.press(Key.media_previous)
        elif action == "play_pause":
            keyboard.press(Key.media_play_pause)
        return jsonify({"status": "success", "message": f"Audio {action} successful"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/clipboard', methods=['GET', 'POST'])
@login_required
def clipboard_operations():
    if request.method == 'GET':
        win32clipboard.OpenClipboard()
        try:
            data = win32clipboard.GetClipboardData()
        except:
            data = ""
        win32clipboard.CloseClipboard()
        return jsonify({"status": "success", "data": data})
    else:
        text = request.json.get('text')
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()
        return jsonify({"status": "success", "message": "Clipboard updated"})

@app.route('/download/<path:filepath>')
@login_required
def download_file(filepath):
    try:
        # Normalize and secure the path
        filepath = os.path.normpath(filepath)
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return send_file(filepath, as_attachment=True)
        return jsonify({"status": "error", "message": "File not found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file provided"})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No file selected"})

        upload_path = request.form.get('path', '')
        if not upload_path or not os.path.exists(upload_path):
            return jsonify({"status": "error", "message": "Invalid upload path"})

        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_path, filename)
        file.save(filepath)
        
        return jsonify({
            "status": "success", 
            "message": "File uploaded successfully",
            "filename": filename
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/launch', methods=['POST'])
@login_required
def launch_application():
    app_path = request.json.get('path')
    try:
        Application().start(app_path)
        return jsonify({"status": "success", "message": f"Launched {app_path}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/network_info', methods=['GET'])
@login_required
def get_network_info():
    try:
        c = wmi.WMI()
        network_info = []
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=1):
            network_info.append({
                "description": interface.Description,
                "ip_address": interface.IPAddress[0] if interface.IPAddress else None,
                "mac_address": interface.MACAddress,
                "dns_servers": interface.DNSServerSearchOrder
            })
        return jsonify({"status": "success", "networks": network_info})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/cmd', methods=['POST'])
@login_required
def execute_command():
    command = request.json.get('command')
    if not command:
        return jsonify({"status": "error", "message": "No command provided"})
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        
        return jsonify({
            "status": "success",
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": process.returncode
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/get_brightness', methods=['GET'])
@login_required
def get_brightness():
    try:
        # Try multiple methods to get brightness
        try:
            # Method 1: screen_brightness_control
            monitors = sbc.list_monitors_info()
            if monitors:
                total_brightness = 0
                count = 0
                for monitor in monitors:
                    try:
                        brightness = sbc.get_brightness(display=monitor['name'])[0]
                        total_brightness += brightness
                        count += 1
                    except:
                        continue
                if count > 0:
                    return jsonify({"status": "success", "brightness": int(total_brightness/count)})
        except Exception as e:
            logging.warning(f"Primary brightness detection failed: {str(e)}")
        
        # Method 2: WMI
        try:
            c = wmi.WMI(namespace='wmi')
            brightness = c.WmiMonitorBrightness()[0]
            return jsonify({"status": "success", "brightness": brightness.CurrentBrightness})
        except Exception as e:
            logging.warning(f"WMI brightness detection failed: {str(e)}")
        
        return jsonify({"status": "error", "message": "Could not detect brightness"})
    except Exception as e:
        logging.error(f"Brightness detection error: {str(e)}")
        return jsonify({"status": "error", "message": "Could not detect brightness"})

@app.route('/get_volume', methods=['GET'])
@login_required
def get_volume():
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current_volume = round((volume.GetMasterVolumeLevelScalar() * 100))
        return jsonify({"status": "success", "volume": current_volume})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/get_drives', methods=['GET'])
@login_required
def get_drives():
    try:
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        drive_info = []
        
        for drive in drives:
            try:
                drive_type = win32file.GetDriveType(drive)
                drive_types = {
                    win32file.DRIVE_UNKNOWN: "Unknown",
                    win32file.DRIVE_NO_ROOT_DIR: "No Root Directory",
                    win32file.DRIVE_REMOVABLE: "Removable",
                    win32file.DRIVE_FIXED: "Fixed",
                    win32file.DRIVE_REMOTE: "Network",
                    win32file.DRIVE_CDROM: "CD-ROM",
                    win32file.DRIVE_RAMDISK: "RAM Disk"
                }
                
                try:
                    volume_name = win32api.GetVolumeInformation(drive)[0]
                except:
                    volume_name = ""

                try:
                    total, used, free = shutil.disk_usage(drive)
                except:
                    total, used, free = 0, 0, 0

                drive_info.append({
                    "path": drive,
                    "name": volume_name,
                    "total": f"{total // (1024**3)} GB" if total else "Unknown",
                    "free": f"{free // (1024**3)} GB" if free else "Unknown",
                    "used": f"{used // (1024**3)} GB" if used else "Unknown",
                    "type": drive_types.get(drive_type, "Unknown")
                })
            except Exception as e:
                print(f"Error accessing drive {drive}: {str(e)}")
                continue
                
        return jsonify({"status": "success", "drives": drive_info})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/stream/<path:filepath>')
@login_required
def stream_file(filepath):
    try:
        filepath = os.path.normpath(filepath)
        if not os.path.exists(filepath):
            return jsonify({"status": "error", "message": "File not found"})
            
        mime_type, _ = mimetypes.guess_type(filepath)
        if not mime_type:
            mime_type = 'application/octet-stream'

        def generate():
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk

        return Response(generate(), mimetype=mime_type)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    print("Starting PC Controller server...")
    print("Access at: http://localhost:80")
    
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Configure the server for long-running connections
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    try:
        # Use Waitress WSGI server with connection timeout settings
        serve(
            app,
            host='0.0.0.0',
            port=80,
            threads=4,
            connection_limit=1000,
            channel_timeout=3600,  # 1 hour
            cleanup_interval=30,   # 30 seconds
            url_scheme='http'
        )
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        print(f"Server error: {str(e)}")
        input("Press Enter to exit...")  # Prevent immediate closing on error
