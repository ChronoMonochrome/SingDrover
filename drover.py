# drover.py

import subprocess
import os
import sys
import json
import time
import shutil # New import for finding executable in PATH
from typing import List, Dict, Any, Tuple
from threading import Thread

import requests

from config_types import SingBoxConfig, ConfigSelector
from json_utils import normalize_json
from system_proxy import enable_system_proxy, disable_system_proxy

# Placeholder for TDroverOptions - replace with actual implementation if needed
class DroverOptions:
    def __init__(self, sb_config_file: str, sb_dir: str, system_proxy_auto: bool = False, selector_menu_layout: str = 'flat'):
        self.sb_config_file = sb_config_file
        self.sb_dir = sb_dir
        self.system_proxy_auto = system_proxy_auto
        self.selector_menu_layout = selector_menu_layout # 'nested' or 'flat'

# Placeholder for LoadOptions - replace with actual implementation if needed
def load_options(path: str) -> DroverOptions:
    # Default values for demonstration:
    return DroverOptions(
        sb_config_file=os.path.join(os.getcwd(), 'config.json'),
        sb_dir=os.getcwd(),
        system_proxy_auto=True,
        selector_menu_layout='flat'
    )

class SelectorThreadTask:
    def __init__(self, name: str, value: str):
        self.name: str = name
        self.value: str = value

class SelectorThread(Thread):
    # ... (No change)
    def __init__(self, drover: 'Drover', tasks: List[SelectorThreadTask]):
        super().__init__()
        self.drover = drover
        self.tasks = tasks
        self.daemon = True

    def run(self):
        for task in self.tasks:
            self.drover.send_api_request('PUT', f'/proxies/{task.name}', json.dumps({"name": task.value}))

        self.drover.send_api_request('DELETE', '/connections', '')


class Drover:
    """Equivalent to TDrover"""
    def __init__(self):
        self.current_process_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.f_options = load_options(os.path.join(self.current_process_dir, 'options.json'))

        config_path = self.f_options.sb_config_file
        self.sb_config = self.read_singbox_config(config_path)
        self.check_singbox_config(self.sb_config)

        # Determine the executable name based on OS
        sb_exe_name = 'sing-box.exe' if sys.platform == "win32" else 'sing-box'

        # Determine the full path to the executable
        # 1. Check the options directory (self.f_options.sb_dir)
        exe_path = os.path.join(self.f_options.sb_dir, sb_exe_name)

        # 2. If not found in the options directory, check PATH
        if not os.path.exists(exe_path):
            exe_path = shutil.which(sb_exe_name)

        if not exe_path:
             raise FileNotFoundError(
                f"sing-box executable not found. Looked for '{sb_exe_name}' in "
                f"'{self.f_options.sb_dir}' and system PATH."
            )

        # Start sing-box and handle potential errors
        self.singbox_start_error = self.start_singbox(exe_path, config_path)

        if self.singbox_start_error:
            # If there's an error, the main app needs to handle the message
            print(f"Sing-box startup error captured: {self.singbox_start_error}")

        # Give sing-box a moment to start and expose the API
        time.sleep(2)

        self.reset_selectors()

    @property
    def options(self) -> DroverOptions:
        return self.f_options

    def start_singbox(self, exe_path: str, config_path: str) -> str:
        """
        Starts the sing-box process.
        Returns the captured stderr string if the process fails immediately, otherwise returns an empty string.
        """
        if not os.path.exists(config_path):
            return f"Configuration file not found at: {config_path}"

        cmd = [exe_path, 'run', '-c', config_path]
        work_dir = os.path.dirname(exe_path)

        try:
            # We use Popen with a short timeout to check for immediate failures.
            # stderr and stdout are captured to prevent a console from blocking.
            self.sb_process = subprocess.Popen(
                cmd,
                cwd=work_dir,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Check if the process exited immediately (failed to start)
            # Use a short timeout to check if the process is still running
            try:
                # Poll to check status immediately
                exit_code = self.sb_process.poll()
                if exit_code is not None:
                    # Process exited immediately, read stderr
                    _, stderr_data = self.sb_process.communicate(timeout=0.1)
                    error_msg = stderr_data.decode('utf-8', errors='ignore').strip()
                    return f"Sing-box exited with code {exit_code}. Error:\n{error_msg}"
            except subprocess.TimeoutExpired:
                 pass # Process is still running, good.

            return "" # Success

        except OSError as e:
            return f"Failed to execute sing-box binary ('{exe_path}'): {e}"

    # --- (Remaining methods remain the same) ---

    def read_singbox_config(self, config_path: str) -> SingBoxConfig:
        # ... (No change)
        if not os.path.exists(config_path):
            raise FileNotFoundError("Configuration file not found.")

        with open(config_path, 'r', encoding='utf-8') as f:
            json_text = f.read()

        json_text = normalize_json(json_text)

        try:
            root_obj = json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Configuration file is corrupted or contains invalid JSON: {e}")

        proxy_host, proxy_port = '', 0
        inbounds = root_obj.get('inbounds', [])
        for item in inbounds:
            if item.get('type') == 'mixed':
                proxy_host = item.get('listen', '')
                proxy_port = item.get('listen_port', 0)
                break

        selectors: List[ConfigSelector] = []
        outbounds = root_obj.get('outbounds', [])
        for item in outbounds:
            if item.get('type') == 'selector':
                sel_name = item.get('tag', '')
                sel_default_name = item.get('default', '')
                sel_outbounds_list: List[str] = item.get('outbounds', [])

                default_index = -1
                try:
                    default_index = sel_outbounds_list.index(sel_default_name)
                except ValueError:
                    pass

                if len(sel_outbounds_list) > 0:
                    selector = ConfigSelector(
                        name=sel_name,
                        outbounds=sel_outbounds_list,
                        default_index=default_index,
                        default_name=sel_default_name
                    )
                    selectors.append(selector)

        clash_api = root_obj.get('experimental', {}).get('clash_api', {})
        clash_api_controller = clash_api.get('external_controller', '')
        clash_api_secret = clash_api.get('secret', '')

        return SingBoxConfig(
            clash_api_controller=clash_api_controller,
            clash_api_secret=clash_api_secret,
            selectors=selectors,
            proxy_host=proxy_host,
            proxy_port=proxy_port
        )

    def check_singbox_config(self, cfg: SingBoxConfig):
        # ... (No change)
        if not cfg.proxy_host or cfg.proxy_port < 1:
            raise Exception('No suitable mixed inbound found for the system proxy.')

    def create_selector_thread(self, tasks: List[SelectorThreadTask]):
        # ... (No change)
        SelectorThread(self, tasks).start()

    def reset_selectors(self):
        # ... (No change)
        tasks: List[SelectorThreadTask] = []
        for selector in self.sb_config.selectors:
            if 0 <= selector.default_index < len(selector.outbounds):
                default_outbound = selector.outbounds[selector.default_index]
                tasks.append(SelectorThreadTask(selector.name, default_outbound))

        if tasks:
            self.create_selector_thread(tasks)

    def edit_selector(self, name: str, value: str):
        # ... (No change)
        task = SelectorThreadTask(name, value)
        self.create_selector_thread([task])

    def send_api_request(self, method: str, path: str, data: str = '') -> bool:
        # ... (No change)
        if not self.sb_config.clash_api_external_controller:
            return False

        url = f'http://{self.sb_config.clash_api_external_controller}{path}'
        headers = {
            'Authorization': f'Bearer {self.sb_config.clash_api_secret}',
            'Content-Type': 'application/json'
        }

        try:
            if method.upper() == 'PUT':
                response = requests.put(url, data=data, headers=headers, timeout=5)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=5)
            else:
                return False

            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"API Request Failed ({method} {url}): {e}")
            return False

    def enable_system_proxy(self) -> bool:
        # ... (No change)
        return enable_system_proxy(self.sb_config.proxy_host, self.sb_config.proxy_port)

    def disable_system_proxy(self) -> bool:
        # ... (No change)
        return disable_system_proxy()

    def stop_singbox(self):
        # ... (No change)
        if hasattr(self, 'sb_process') and self.sb_process.poll() is None:
            print("Stopping sing-box process...")
            self.sb_process.terminate()
            try:
                self.sb_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.sb_process.kill()
