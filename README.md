
# SingDrover

A cross-platform system tray utility for managing the proxy settings and selector groups of a local `sing-box` instance via its Clash API.

This project is inspired by the original **sing-box-drover** application, available at [https://github.com/hdrover/sing-box-drover](https://github.com/hdrover/sing-box-drover "null"). DroverProxyManager is a Python port of this application, primarily focused on providing a cross-platform solution (especially for Linux) for quick control over system proxy activation and switching proxy/outbound nodes defined in your `sing-box` configuration file.

## ✨ Features

-   **System Tray Integration:** Provides control via a persistent icon in the system tray (AppIndicator on Linux, Notification Area on Windows).
    
-   **System Proxy Management:** Quickly enables and disables system-wide proxy settings (requires Administrator/root permissions for some OS configurations).
    
-   **Cross-Platform:** Built using Python and PyInstaller for Linux and Windows executables.


## 💻 Requirements

### Runtime Requirements

To run the compiled executable on Linux, you need the following system library package installed to ensure the system tray icon (AppIndicator) functions correctly.
`sudo apt install gir1.2-appindicator3-0.1` 

### Build Requirements

To build the executable from source, you must have Python 3.8+ and the packages listed in `requirements.txt` installed.

## 🛠️ Build and Setup

### 1. Prerequisites

Ensure you have Python and Git installed.

```
# Clone the repository (if applicable)
git clone <repository-url>
cd SingDrover

# Install required Python packages
pip install -r requirements.txt


```

### 2. Build Process

The `build.sh` script is used to create the standalone executable using PyInstaller.

#### `build.sh` Content:

```
#!/bin/bash

# Build script for DroverProxyManager
# Creates a single-file, console-less executable, excluding many standard Python modules
# to reduce the final binary size.

pyinstaller --name DroverProxyManager --onefile --noconsole main.py \
    --exclude-module bz2 \
    --exclude-module lzma \
    --exclude-module multiprocessing \
    --exclude-module pwd \
    --exclude-module grp \
    --exclude-module fcntl \
    --exclude-module posix \
    --exclude-module _hashlib \
    --exclude-module _ssl \
    --exclude-module _ctypes \
    --exclude-module defusedxml \
    --exclude-module uharbfuzz \
    --exclude-module reportlab_settings \
    --exclude-module dis \
    --exclude-module opcode \
    --exclude-module inspect \
    --exclude-module unittest \
    --exclude-module sqlite3 \
    --exclude-module pdb \
    --exclude-module cProfile \
    --exclude-module asyncio \
    --exclude-module trace \
    --exclude-module timeit


```

#### Execution:

1.  Make the script executable (Linux/macOS):
    
    ```
    chmod +x build.sh
    
    
    ```
    
2.  Run the build:
    
    ```
    ./build.sh
    
    
    ```
    
    The final executable will be located in the `./dist` directory.
