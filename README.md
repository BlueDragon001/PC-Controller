# PC Controller

A web-based remote control system for Windows PCs that allows you to manage your computer through a browser interface.

## Features

- **System Control**
  - Shutdown/Restart/Sleep/Lock
  - Process management
  - System information
  - Storage information
  - Network information

- **Media Control**
  - Volume control
  - Brightness adjustment
  - Media playback controls (play/pause, next, previous)
  - Monitor on/off

- **Input Control**
  - Mouse movement
  - Keyboard input
  - Clipboard operations

- **File Management**
  - File explorer
  - File upload/download
  - Directory creation/deletion
  - File streaming

- **Security**
  - User authentication
  - Session management
  - Secure password hashing

## Requirements

- Python 3.7+
- Windows OS
- Required Python packages (install via pip):
  ```
  flask
  psutil
  pyautogui
  pywinauto
  pywin32
  wmi
  screen_brightness_control
  pynput
  pycaw
  waitress
  ```

## Setup

1. Clone or download the project to `D:\Tools\PC Controller\`
2. Create a `users.json` file with the following structure:
   ```json
   {
     "users": [
       {
         "username": "admin",
         "password": "YOUR_SHA256_HASHED_PASSWORD"
       }
     ]
   }
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the server:
   ```bash
   python PCserver.py
   ```
2. Access the web interface at: `http://localhost:80`
3. Log in with your credentials

## Project Structure

```
├── PCserver.py          # Main server file
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── users.json         # User credentials
├── static/            # Static files directory
└── modules/           # Python modules
    ├── __init__.py
    ├── auth.py        # Authentication functions
    ├── display_control.py  # Display/brightness control
    ├── file_ops.py    # File operations
    ├── system_control.py   # System control functions
    └── utils.py       # Utility functions
```

## Security Notes

- Change the default secret key in PCserver.py
- Use HTTPS in production
- Keep users.json secure and backup regularly
- Consider implementing rate limiting
- Review file access permissions

## Troubleshooting

- **Brightness Control**: Multiple methods are implemented (SBC, WMI, DirectX)
- **Volume Control**: Requires admin rights for some operations
- **File Access**: Check Windows permissions
- **Server Issues**: Check pc_controller.log for details

## Contributing

Fork the repository and submit pull requests for any improvements.

## License

This project is for personal use. All rights reserved.
