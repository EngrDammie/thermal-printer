"""Configuration management for thermal printer."""

import json
import os
from pathlib import Path
from typing import Optional

CONFIG_FILE_NAME = ".thermal_printer.json"
ENV_VAR_NAME = "THERMAL_PRINTER_MAC"


def get_config_path() -> Path:
    """Get the config file path (current directory or home)."""
    local_config = Path.cwd() / CONFIG_FILE_NAME
    if local_config.exists():
        return local_config
    return Path.home() / CONFIG_FILE_NAME


def load_config() -> dict:
    """Load configuration from file."""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_config(config: dict) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def get_printer_mac(env_var: str = ENV_VAR_NAME) -> Optional[str]:
    """
    Get printer MAC address with fallback priority:
    1. Environment variable
    2. Config file
    3. None
    
    Args:
        env_var: Environment variable name
        
    Returns:
        MAC address or None
    """
    mac = os.environ.get(env_var)
    if mac:
        return mac.upper().replace("-", ":")
    
    config = load_config()
    mac = config.get("mac_address")
    if mac:
        return mac.upper().replace("-", ":")
    
    return None


def set_printer_mac(mac_address: str, save: bool = True) -> str:
    """
    Set the default printer MAC address.
    
    Args:
        mac_address: MAC address to set
        save: Whether to save to config file
        
    Returns:
        Normalized MAC address
    """
    normalized = mac_address.upper().replace("-", ":")
    
    if save:
        config = load_config()
        config["mac_address"] = normalized
        save_config(config)
    
    return normalized


def get_printer_channel() -> int:
    """Get RFCOMM channel from config or env var."""
    channel = os.environ.get("THERMAL_PRINTER_CHANNEL")
    if channel:
        return int(channel)
    
    config = load_config()
    return config.get("channel", 1)


def set_printer_channel(channel: int, save: bool = True) -> None:
    """Set the default RFCOMM channel."""
    if save:
        config = load_config()
        config["channel"] = channel
        save_config(config)


def get_default_printer() -> Optional[dict]:
    """Get default printer config."""
    mac = get_printer_mac()
    if mac:
        return {
            "mac_address": mac,
            "channel": get_printer_channel()
        }
    return None


def config_exists() -> bool:
    """Check if config file or env var exists."""
    if os.environ.get(ENV_VAR_NAME):
        return True
    return get_config_path().exists()
