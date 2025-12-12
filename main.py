# main.py

import sys
import os

import shlex
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

from drover import Drover
from config_types import ConfigSelector

from typing import List

# =========================================================
# CROSS-PLATFORM GUI MESSAGE FUNCTION
# =========================================================
# Used for displaying messages
if sys.platform == "win32":
    import ctypes
    def show_error_message(title, message):
        # Using win32 MessageBox for native dialog
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)
elif sys.platform == "linux":
    # Placeholder for Linux notification using notify-send (requires desktop environment)
    def show_error_message(title, message):
        # FIX: Use shlex.quote for robustly escaping shell arguments (title and message)
        title_quoted = shlex.quote(title)
        message_quoted = shlex.quote(message)
        os.system(f"notify-send {title_quoted} {message_quoted}")
else:
    # Fallback for other platforms
    def show_error_message(title, message):
        print(f"--- GUI MESSAGE ---\nTitle: {title}\nMessage: {message}\n-------------------")

# =========================================================
# END OF GUI MESSAGE FUNCTION
# =========================================================

class MainApp:
    """Equivalent to TfrmMain"""
    def __init__(self):
        self.drover = Drover()
        self.is_system_proxy_enabled = False

        # Create a simple generic icon image
        self.icon_image = self.create_icon_image()

        # Initialize icon and menu
        self.menu_items = self.create_menu_items()
        self.tray_icon = Icon(
            'DroverApp',
            self.icon_image,
            'Drover Proxy Manager',
            self.menu_items
        )

        # TrayIcon.OnClick behavior (toggle system proxy)
        self.tray_icon.title = 'Drover Proxy Manager (Disabled)'
        self.tray_icon.menu = Menu(*self.menu_items)
        self.tray_icon.left_click = self.tray_icon_click

        if self.drover.options.system_proxy_auto:
            self.toggle_system_proxy(True)
        else:
            self.toggle_system_proxy_icon(False)

    def create_icon_image(self, enabled: bool = True) -> Image:
        """Creates a simple, generic icon for the tray."""
        # A simple colored square or circle as a placeholder
        width, height = 64, 64
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        color = (0, 150, 0) if enabled else (150, 0, 0) # Green for enabled, Red for disabled
        draw.ellipse((5, 5, width - 5, height - 5), fill=color)
        return image

    def toggle_system_proxy_icon(self, enable: bool):
        """Updates the icon and title based on proxy status."""
        self.icon_image = self.create_icon_image(enable)
        self.tray_icon.icon = self.icon_image
        self.tray_icon.title = f'Drover Proxy Manager ({"Enabled" if enable else "Disabled"})'

    def toggle_system_proxy(self, enable: bool):
        """Enables/Disables the system proxy."""
        if enable:
            success = self.drover.enable_system_proxy()
        else:
            success = self.drover.disable_system_proxy()

        if success:
            self.is_system_proxy_enabled = enable
            self.toggle_system_proxy_icon(enable)
        else:
            print(f"Failed to {'enable' if enable else 'disable'} system proxy.")
            # If failed to enable, ensure state remains disabled
            if enable:
                self.is_system_proxy_enabled = False
                self.toggle_system_proxy_icon(False)

    # --- Event Handlers ---

    def tray_icon_click(self, icon, item):
        """Equivalent to TfrmMain.TrayIconClick (toggles proxy on click)."""
        self.toggle_system_proxy(not self.is_system_proxy_enabled)

    def mi_quit_click(self, icon, item):
        """Equivalent to TfrmMain.miQuitClick (closes the application)."""
        # FormCloseQuery logic is implemented here
        if self.drover.options.system_proxy_auto:
            self.toggle_system_proxy(False)

        self.drover.stop_singbox()
        self.tray_icon.stop()

    def mi_system_proxy_click(self, icon, item):
        """Equivalent to TfrmMain.miSystemProxyClick (toggles proxy from menu)."""
        # The pystray MenuItem handles checked state automatically
        self.toggle_system_proxy(not self.is_system_proxy_enabled)

    def mi_selector_click(self, selector_name: str, outbound_name: str):
        """Equivalent to TfrmMain.miSelectorClick (changes a selector outbound)."""
        def handler(icon, item):
            print(f"Setting selector '{selector_name}' to '{outbound_name}'")
            self.drover.edit_selector(selector_name, outbound_name)
        return handler

    def create_menu_items(self) -> List[MenuItem]:
        """Equivalent to TfrmMain.DrawSelectors and PopupMenu initialization."""

        # 1. System Proxy Toggle (miSystemProxy)
        def system_proxy_checked(item):
            return self.is_system_proxy_enabled

        mi_system_proxy = MenuItem(
            'System Proxy',
            self.mi_system_proxy_click,
            checked=system_proxy_checked
        )

        menu_list: List[MenuItem] = [mi_system_proxy, Menu.SEPARATOR] # miBeforeSelectors is implicitly here

        # 2. Selector Items
        is_nested = self.drover.options.selector_menu_layout == 'nested'

        for selector in self.drover.sb_config.selectors:
            # Create outbound menu items for the current selector
            outbound_items: List[MenuItem] = []
            for outbound_name in selector.outbounds:

                # Logic to determine which outbound is currently selected
                # Note: The original code used item.Checked to set the default on menu creation.
                # Here, we need a dynamic check for the pystray MenuItem.
                # In a real-world app, we'd fetch the current setting from the sing-box API,
                # but for simplicity, we assume the initial 'default' is the current setting.

                def outbound_checked_func(outbound_name=outbound_name, selector_default_name=selector.default_name):
                    # We can't easily query the live state, so we mark the default as checked initially
                    return outbound_name == selector_default_name

                outbound_item = MenuItem(
                    outbound_name,
                    self.mi_selector_click(selector.name, outbound_name),
                    radio=True,
                    checked=outbound_checked_func # Will not update dynamically without API query
                )
                outbound_items.append(outbound_item)

            if is_nested:
                # Nested menu: Selector name is the parent menu item
                selector_menu = MenuItem(selector.name, Menu(*outbound_items))
                menu_list.append(selector_menu)
            else:
                # Flat menu: Selector name is a disabled caption, followed by outbounds
                menu_list.append(MenuItem(selector.name, lambda x: None, enabled=False))
                menu_list.extend(outbound_items)
                menu_list.append(Menu.SEPARATOR) # Separator after the group

        # 3. Quit
        menu_list.append(Menu.SEPARATOR)
        menu_list.append(MenuItem('Quit', self.mi_quit_click))

        return menu_list

    def run(self):
        """Starts the main loop for the tray icon."""
        print(f"Starting Drover App in {self.drover.options.selector_menu_layout} layout...")
        try:
            self.tray_icon.run()
        except NotImplementedError as e:
            # Catch exceptions from system_proxy.py if OS is unsupported
            print(f"FATAL ERROR: {e}")
            self.drover.stop_singbox()
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.drover.stop_singbox()
            sys.exit(1)


if __name__ == '__main__':
    # Place a dummy config.json and sing-box.exe for testing
    # e.g., run the app in a directory containing:
    # 1. sing-box.exe (or the executable for your OS)
    # 2. config.json (a valid sing-box config)
    # 3. options.json (for custom settings)
    try:
        app = MainApp()
        app.run()
    except Exception as e:
        print(f"Application initialization failed: {e}")
        # The main app initialization should now handle most critical errors,
        # but this is a final fallback.
        show_error_message("Critical Error", f"Application failed to initialize: {e}") # <-- This line triggers the GUI message
        sys.exit(1)
