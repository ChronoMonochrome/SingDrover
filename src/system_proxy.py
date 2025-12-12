# system_proxy.py

import sys
import os
import subprocess
from typing import Union

# --- Windows Implementation ---
if sys.platform == "win32":
    try:
        import winreg
    except ImportError:
        print("Warning: 'winreg' module not available. System proxy manipulation will fail.")
        winreg = None

    def enable_system_proxy(host: str, port: int) -> bool:
        """Enables system-wide proxy using winreg for Windows."""
        if not winreg:
            return False

        try:
            # Key path for current user's Internet settings
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                0,
                winreg.KEY_SET_VALUE
            )

            # Proxy Server string
            proxy_str = f"http={host}:{port};https={host}:{port};socks={host}:{port}"
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_str)

            # Enable proxy (1 = enabled, 0 = disabled)
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)

            # Bypass local addresses
            winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, "<local>")

            winreg.CloseKey(key)

            # Notify the system about the changes (equivalent to INTERNET_OPTION_SETTINGS_CHANGED/REFRESH)
            subprocess.run(['ipconfig', '/flushdns'], creationflags=subprocess.CREATE_NO_WINDOW, check=False)
            # In a real app, you might need to broadcast a message, but flushing DNS often helps.

            return True
        except Exception as e:
            print(f"Error enabling system proxy: {e}")
            return False

    def disable_system_proxy() -> bool:
        """Disables system-wide proxy using winreg for Windows."""
        if not winreg:
            return False

        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                0,
                winreg.KEY_SET_VALUE
            )

            # Disable proxy
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)

            winreg.CloseKey(key)
            subprocess.run(['ipconfig', '/flushdns'], creationflags=subprocess.CREATE_NO_WINDOW, check=False)
            return True
        except Exception as e:
            print(f"Error disabling system proxy: {e}")
            return False

# --- Linux/Cross-Platform Fallback (Often requires DE-specific tools like gsettings) ---
else:
    # A complete solution for Linux would involve interacting with D-Bus/GSettings/KDE config.
    # For a simplified, application-specific approach, we can rely on environment variables,
    # but this does not set the *system* proxy for all applications.
    # We will raise a NotImplementedError to signal the need for platform-specific implementation.

    def enable_system_proxy(host: str, port: int) -> bool:
        return NotImplementedError(f"System proxy not implemented for {sys.platform}. Requires OS-specific tools (e.g., GSettings on Linux).")

    def disable_system_proxy() -> bool:
        return NotImplementedError(f"System proxy not implemented for {sys.platform}. Requires OS-specific tools (e.g., GSettings on Linux).")
