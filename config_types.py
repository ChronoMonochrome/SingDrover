# config_types.py

from typing import List, Dict, Any, Optional

class ConfigSelector:
    """Equivalent to TConfigSelector in Drover.pas"""
    def __init__(self, name: str, outbounds: List[str], default_index: int, default_name: str):
        self.name: str = name
        self.outbounds: List[str] = outbounds
        self.default_index: int = default_index
        self.default_name: str = default_name

class SingBoxConfig:
    """Equivalent to TSingBoxConfig in Drover.pas"""
    def __init__(self, clash_api_controller: str, clash_api_secret: str,
                 selectors: List[ConfigSelector], proxy_host: str, proxy_port: int):
        self.clash_api_external_controller: str = clash_api_controller
        self.clash_api_secret: str = clash_api_secret
        self.selectors: List[ConfigSelector] = selectors
        self.proxy_host: str = proxy_host
        self.proxy_port: int = proxy_port
