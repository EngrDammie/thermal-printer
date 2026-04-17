"""Bluetooth device scanner for thermal printers."""

import bluetooth
from typing import List, Optional


class Device:
    """Represents a discovered Bluetooth device."""

    def __init__(self, address: str, name: str = None, device_class: int = None):
        self.address = address
        self.name = name
        self.device_class = device_class

    def __repr__(self):
        return f"Device({self.address}, {self.name})"

    def __str__(self):
        name = self.name if self.name else "Unknown"
        return f"{self.address} - {name}"


class BluetoothScanner:
    """Scanner for discovering Bluetooth devices."""

    def __init__(self, duration: int = 10):
        """
        Initialize the scanner.

        Args:
            duration: Scan duration in seconds
        """
        self.duration = duration

    def discover_devices(self, lookup_names: bool = True) -> List[Device]:
        """
        Discover nearby Bluetooth devices.

        Args:
            lookup_names: Whether to look up device names

        Returns:
            List of discovered devices
        """
        devices = bluetooth.discover_devices(
            duration=self.duration,
            lookup_names=lookup_names,
            flush_cache=True
        )

        return [Device(addr, name) for addr, name in devices]

    def find_printer(self, mac_address: str = None, name_contains: str = None) -> Optional[Device]:
        """
        Find a specific printer by MAC address or name.

        Args:
            mac_address: MAC address to look for (e.g., "98:B2:6A:F7:AD:50")
            name_contains: Substring to match in device name

        Returns:
            Device if found, None otherwise
        """
        devices = self.discover_devices()

        if mac_address:
            mac_address = mac_address.upper().replace("-", ":")
            for device in devices:
                if device.address.upper() == mac_address:
                    return device

        if name_contains:
            name_contains = name_contains.lower()
            for device in devices:
                if device.name and name_contains in device.name.lower():
                    return device

        return None

    def find_all_printers(self) -> List[Device]:
        """
        Find all potential printer devices.

        Returns:
            List of devices that might be printers
        """
        devices = self.discover_devices()
        printer_keywords = ["printer", "thermal", "print", "bt", "mini", "portable"]

        printers = []
        for device in devices:
            if device.name:
                name_lower = device.name.lower()
                if any(keyword in name_lower for keyword in printer_keywords):
                    printers.append(device)

        return printers

    def lookup_name(self, address: str) -> Optional[str]:
        """
        Look up the name of a device by its MAC address.

        Args:
            address: MAC address

        Returns:
            Device name or None
        """
        return bluetooth.lookup_name(address)

    def get_device_info(self, address: str) -> dict:
        """
        Get detailed information about a device.

        Args:
            address: MAC address

        Returns:
            Dictionary with device information
        """
        try:
            info = bluetooth.lookup_name(address)
            return {
                "address": address,
                "name": info,
                "found": info is not None
            }
        except Exception as e:
            return {
                "address": address,
                "name": None,
                "found": False,
                "error": str(e)
            }


def scan_interactive():
    """Interactive scanner that prints results to console."""
    print("Scanning for Bluetooth devices...")
    print("-" * 50)

    scanner = BluetoothScanner(duration=10)
    devices = scanner.discover_devices()

    if not devices:
        print("No devices found.")
        return

    print(f"Found {len(devices)} device(s):\n")

    for i, device in enumerate(devices, 1):
        print(f"{i}. {device}")

    return devices


if __name__ == "__main__":
    scan_interactive()
