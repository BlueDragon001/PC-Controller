import logging
import wmi
import screen_brightness_control as sbc
import pythoncom
import ctypes
from ctypes import windll

def set_brightness_dx(brightness_value):
    """Set brightness using DirectX method"""
    try:
        pythoncom.CoInitialize()
        brightness = int((brightness_value * 255) / 100)
        class _GAMMARAMP(ctypes.Structure):
            _fields_ = [('red', ctypes.c_ushort * 256),
                       ('green', ctypes.c_ushort * 256),
                       ('blue', ctypes.c_ushort * 256)]
        
        dc = windll.gdi32.CreateDCW('DISPLAY', None, None, None)
        ramp = _GAMMARAMP()
        for i in range(256):
            value = min(65535, int((i * brightness * 65535) / 65535))
            ramp.red[i] = ramp.green[i] = ramp.blue[i] = value
        
        windll.gdi32.SetDeviceGammaRamp(dc, ctypes.byref(ramp))
        windll.gdi32.DeleteDC(dc)
        return True
    except Exception as e:
        logging.error(f"DirectX brightness control failed: {str(e)}")
        return False
    finally:
        pythoncom.CoUninitialize()

def get_brightness_methods():
    methods = []
    # Screen Brightness Control method
    try:
        monitors = sbc.list_monitors_info()
        if monitors:
            methods.append(("sbc", monitors))
    except:
        pass
    
    # WMI method
    try:
        c = wmi.WMI(namespace='wmi')
        monitors = c.WmiMonitorBrightnessMethods()
        if monitors:
            methods.append(("wmi", monitors))
    except:
        pass
    
    return methods
