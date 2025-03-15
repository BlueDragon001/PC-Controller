from flask import jsonify
import os
import shutil
import win32api
import win32file
import time

def get_drive_list():
    drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
    items = []
    drive_types = {
        win32file.DRIVE_UNKNOWN: "Unknown",
        win32file.DRIVE_NO_ROOT_DIR: "No Root Directory",
        win32file.DRIVE_REMOVABLE: "Removable",
        win32file.DRIVE_FIXED: "Fixed",
        win32file.DRIVE_REMOTE: "Network",
        win32file.DRIVE_CDROM: "CD-ROM",
        win32file.DRIVE_RAMDISK: "RAM Disk"
    }
    
    for drive in drives:
        try:
            drive_type = win32file.GetDriveType(drive)
            volume_name = ""
            try:
                volume_name = win32api.GetVolumeInformation(drive)[0]
            except:
                pass

            size_str = "Not accessible"
            try:
                total, used, free = shutil.disk_usage(drive)
                size_str = f"Free: {free // (1024**3)} GB"
            except:
                pass

            items.append({
                "name": drive,
                "is_directory": True,
                "size": size_str,
                "modified": "",
                "type": drive_types.get(drive_type, "Unknown"),
                "volume_name": volume_name
            })
        except Exception:
            continue
    return items

def get_directory_contents(path):
    items = []
    for item in os.listdir(path):
        try:
            full_path = os.path.join(path, item)
            stat = os.stat(full_path)
            if bool(stat.st_file_attributes & 2):  # Skip hidden
                continue
                
            size = stat.st_size
            mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
            is_dir = os.path.isdir(full_path)
            
            size_str = "Directory" if is_dir else format_size(size)
            if is_dir:
                try:
                    _, _, free = shutil.disk_usage(full_path)
                    size_str = f"Free: {free // (1024**3)} GB"
                except:
                    pass

            items.append({
                "name": item,
                "is_directory": is_dir,
                "size": size_str,
                "modified": mtime,
                "type": "Directory" if is_dir else os.path.splitext(item)[1] or "File"
            })
        except:
            continue
    
    items.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
    return items

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != 'B' else f"{size} {unit}"
        size /= 1024
    return f"{size:.1f} GB"
