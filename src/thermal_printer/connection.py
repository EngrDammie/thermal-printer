"""RFCOMM Bluetooth connection handler for thermal printers."""

import socket
import subprocess
import time
from typing import Optional

# Check if Bluetooth constants are available
try:
    AF_BLUETOOTH = socket.AF_BLUETOOTH
    BTPROTO_RFCOMM = socket.BTPROTO_RFCOMM
except AttributeError:
    AF_BLUETOOTH = None
    BTPROTO_RFCOMM = None
    print("WARNING: Bluetooth constants not available. Make sure pybluez is installed:")
    print("  pip3 install pybluez")
    print("  sudo apt install libbluetooth-dev")


class BluetoothConnection:
    """Handle RFCOMM Bluetooth connection to thermal printer."""

    def __init__(
        self,
        mac_address: str,
        channel: int = 1,
        rfcomm_device: str = "/dev/rfcomm0"
    ):
        """
        Initialize Bluetooth connection.

        Args:
            mac_address: MAC address of the printer (e.g., "98:B2:6A:F7:AD:50")
            channel: RFCOMM channel (default: 1)
            RFC rfcomm_device:OMM device path
        """
        self.mac_address = mac_address.upper().replace("-", ":")
        self.channel = channel
        self.rfcomm_device = rfcomm_device
        self.socket: Optional[socket.socket] = None
        self._bound = False

    def bind_rfcomm(self) -> bool:
        """
        Bind the printer to an RFCOMM device.

        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["rfcomm", "bind", self.rfcomm_device, self.mac_address, str(self.channel)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self._bound = True
                time.sleep(0.5)
                return True
            return False
        except Exception as e:
            print(f"Error binding RFCOMM: {e}")
            return False

    def release_rfcomm(self) -> bool:
        """
        Release the RFCOMM device.

        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["rfcomm", "release", self.rfcomm_device],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self._bound = False
                return True
            return False
        except Exception as e:
            print(f"Error releasing RFCOMM: {e}")
            return False

    def connect(self) -> bool:
        """
        Connect to the printer via RFCOMM.

        Returns:
            True if connected, False otherwise
        """
        print(f"Attempting to connect to {self.mac_address} on channel {self.channel}...")
        
        # Try direct connection first (no rfcomm binding needed)
        print("Trying direct RFCOMM connection...")
        if self._try_connect():
            print("Direct connection successful!")
            return True
        
        # If direct fails, try rfcomm binding
        print("Direct connection failed, trying RFCOMM binding...")
        if not self.bind_rfcomm():
            print("Failed to bind RFCOMM. Make sure the device is paired and you have permissions.")
            print("Try running: sudo rfcomm bind /dev/rfcomm0 " + self.mac_address + " " + str(self.channel))
            return False
        
        # Try connecting via rfcomm device
        print("RFCOMM bound, attempting connection via device...")
        time.sleep(1)
        if self._try_connect():
            print("Connection via RFCOMM successful!")
            return True
        
        print("All connection methods failed.")
        return False

    def _try_connect(self) -> bool:
        """Try to establish socket connection."""
        global AF_BLUETOOTH, BTPROTO_RFCOMM
        
        if AF_BLUETOOTH is None:
            try:
                AF_BLUETOOTH = socket.AF_BLUETOOTH
                BTPROTO_RFCOMM = socket.BTPROTO_RFCOMM
            except AttributeError:
                print("  ERROR: Bluetooth not available. Install pybluez:")
                print("    pip3 install pybluez")
                print("    sudo apt install libbluetooth-dev")
                return False
        
        try:
            self.socket = socket.socket(AF_BLUETOOTH, socket.SOCK_STREAM, BTPROTO_RFCOMM)
            self.socket.settimeout(10.0)
            self.socket.connect((self.mac_address, self.channel))
            return True
        except Exception as e:
            error_msg = str(e)
            print(f"  Connection attempt failed: {error_msg}")
            self.socket = None
            if "Permission denied" in error_msg or "Operation not permitted" in error_msg:
                print("  Hint: Try running with sudo or check Bluetooth permissions")
            return False

    def connect_direct(self) -> bool:
        """
        Connect directly without RFCOMM binding (alternative method).

        Returns:
            True if connected, False otherwise
        """
        return self._try_connect()

    def disconnect(self):
        """Disconnect from the printer."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        if self._bound:
            self.release_rfcomm()

    def send(self, data: bytes) -> bool:
        """
        Send data to the printer.

        Args:
            data: Bytes to send

        Returns:
            True if successful, False otherwise
        """
        if not self.socket:
            return False

        try:
            self.socket.send(data)
            return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False

    def send_text(self, text: str, encoding: str = "utf-8") -> bool:
        """
        Send text to the printer.

        Args:
            text: Text to send
            encoding: Text encoding

        Returns:
            True if successful, False otherwise
        """
        return self.send(text.encode(encoding))

    def is_connected(self) -> bool:
        """
        Check if connected to the printer.

        Returns:
            True if connected, False otherwise
        """
        if not self.socket:
            return False

        try:
            # Check if socket is still open
            self.socket.getpeername()
            return True
        except:
            return False

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def get_channel_from_service(mac_address: str) -> Optional[int]:
    """
    Get the RFCOMM channel from the printer's SDP service record.

    Args:
        mac_address: MAC address of the printer

    Returns:
        Channel number if found, None otherwise
    """
    try:
        import bluetooth
        services = bluetooth.find_service(address=mac_address)
        for svc in services:
            if svc["protocol"] == "RFCOMM":
                return svc["port"]
        return None
    except Exception as e:
        print(f"Error looking up service: {e}")
        return None


def check_bluetooth_status() -> dict:
    """
    Check Bluetooth adapter status.

    Returns:
        Dictionary with Bluetooth status information
    """
    status = {
        "powered": False,
        "discoverable": False,
        "adapters": []
    }

    try:
        result = subprocess.run(
            ["bluetoothctl", "show"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "Powered: yes" in line:
                    status["powered"] = True
                elif "Discoverable: yes" in line:
                    status["discoverable"] = True

        # List adapters
        result = subprocess.run(
            ["bluetoothctl", "list"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            for line in lines[1:]:  # Skip header
                parts = line.split()
                if parts:
                    status["adapters"].append({
                        "mac": parts[0] if len(parts) > 0 else None,
                        "name": parts[1] if len(parts) > 1 else "Unknown"
                    })

    except Exception as e:
        status["error"] = str(e)

    return status


if __name__ == "__main__":
    status = check_bluetooth_status()
    print("Bluetooth Status:")
    print(f"  Powered: {status['powered']}")
    print(f"  Discoverable: {status['discoverable']}")
    print(f"  Adapters: {status['adapters']}")
