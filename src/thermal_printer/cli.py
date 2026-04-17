"""CLI interface for thermal printer."""

import json
import sys
import datetime
import click

from .scanner import BluetoothScanner
from .printer import ThermalPrinter, Alignment, BarcodeType, QRErrorCorrection
from .connection import check_bluetooth_status
from . import config


PRINTER_WIDTH_58MM = 32
PRINTER_WIDTH_80MM = 48


def get_printer_address(ctx, param, value):
    """Get printer MAC address with fallback to config."""
    if value:
        return value
    mac = config.get_printer_mac()
    if mac:
        return mac
    ctx.fail("No printer specified. Use --mac or run 'thermal-printer set-printer' to configure a default.")


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Thermal Printer CLI - Print to Bluetooth thermal printers."""
    pass


@cli.command("scan")
@click.option("--timeout", default=10, help="Scan duration in seconds")
def scan_devices(timeout):
    """Scan for nearby Bluetooth devices."""
    click.echo(f"Scanning for Bluetooth devices for {timeout} seconds...")
    click.echo("-" * 50)

    scanner = BluetoothScanner(duration=timeout)
    devices = scanner.discover_devices()

    if not devices:
        click.echo("No devices found.")
        return

    click.echo(f"Found {len(devices)} device(s):\n")

    for i, device in enumerate(devices, 1):
        click.echo(f"  {i}. {device.address} - {device.name or 'Unknown'}")


@cli.command("status")
@click.option("--mac", "-m", help="Printer MAC address (or uses default from config)")
@click.option("--channel", "-c", default=None, help="RFCOMM channel (uses config default)")
def printer_status(mac, channel):
    """Check printer status."""
    mac = mac or config.get_printer_mac()
    channel = channel or config.get_printer_channel()
    if not mac:
        click.echo("Error: No printer configured. Use --mac or run 'thermal-printer set-printer'")
        sys.exit(1)

    click.echo(f"Checking status of printer at {mac}...")

    try:
        printer = ThermalPrinter(mac, channel=channel)
        if printer.connect():
            status = printer.status()
            click.echo(f"  Connected: {status['connected']}")
            click.echo(f"  MAC Address: {status['mac_address']}")
            click.echo(f"  Channel: {status['channel']}")
            click.echo(f"  Width: {status['width']} characters")
            printer.disconnect()
            click.echo("\nPrinter is ready!")
        else:
            click.echo("Failed to connect to printer.")
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command("print-text")
@click.option("--mac", "-m", help="Printer MAC address (or uses default from config)")
@click.option("--text", "-t", required=True, help="Text to print")
@click.option("--channel", "-c", default=None, help="RFCOMM channel (uses config default)")
@click.option("--align", type=click.Choice(["left", "center", "right"]), default="left")
@click.option("--bold", is_flag=True, help="Bold text")
@click.option("--underline", is_flag=True, help="Underlined text")
@click.option("--size", default="1,1", help="Text size as width,height (e.g., 2,2)")
def print_text(mac, text, channel, align, bold, underline, size):
    """Print plain text."""
    mac = mac or config.get_printer_mac()
    channel = channel or config.get_printer_channel()
    if not mac:
        click.echo("Error: No printer configured. Use --mac or run 'thermal-printer set-printer'")
        sys.exit(1)
    
    align_map = {"left": Alignment.LEFT, "center": Alignment.CENTER, "right": Alignment.RIGHT}

    try:
        width, height = map(int, size.split(","))
    except:
        width, height = 1, 1

    try:
        with ThermalPrinter(mac, channel=channel) as printer:
            result = printer.print_text(
                text,
                align=align_map[align],
                bold=bold,
                underline=underline,
                size=(width, height)
            )

            if result:
                click.echo("Text printed successfully!")
            else:
                click.echo("Failed to print text.")
                sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command("print-receipt")
@click.option("--mac", "-m", help="Printer MAC address (or uses default from config)")
@click.option("--data", "-d", required=True, help="JSON receipt data")
@click.option("--channel", "-c", default=None, help="RFCOMM channel (uses config default)")
@click.option("--width", type=int, default=PRINTER_WIDTH_58MM, help="Character width (32 for 58mm, 48 for 80mm)")
def print_receipt(mac, data, channel, width):
    """Print a receipt from JSON data."""
    mac = mac or config.get_printer_mac()
    channel = channel or config.get_printer_channel()
    if not mac:
        click.echo("Error: No printer configured. Use --mac or run 'thermal-printer set-printer'")
        sys.exit(1)
    
    try:
        receipt_data = json.loads(data)
    except json.JSONDecodeError:
        click.echo("Error: Invalid JSON data")
        sys.exit(1)

    store_name = receipt_data.get("store", "Store")
    items = receipt_data.get("items", [])
    total = receipt_data.get("total", 0.0)
    footer = receipt_data.get("footer")
    receipt_number = receipt_data.get("receipt_number")
    date = receipt_data.get("date")

    if not date:
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with ThermalPrinter(mac, channel=channel, width=width) as printer:
            result = printer.print_receipt(
                store_name=store_name,
                items=items,
                total=total,
                footer=footer,
                receipt_number=receipt_number,
                date=date
            )

            if result:
                click.echo("Receipt printed successfully!")
            else:
                click.echo("Failed to print receipt.")
                sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command("print-qr")
@click.option("--mac", "-m", help="Printer MAC address (or uses default from config)")
@click.option("--data", "-d", required=True, help="Data to encode in QR code")
@click.option("--channel", "-c", default=None, help="RFCOMM channel (uses config default)")
@click.option("--size", default=6, type=int, help="QR code size (1-16)")
def print_qr(mac, data, channel, size):
    """Print a QR code."""
    mac = mac or config.get_printer_mac()
    channel = channel or config.get_printer_channel()
    if not mac:
        click.echo("Error: No printer configured. Use --mac or run 'thermal-printer set-printer'")
        sys.exit(1)
    
    try:
        with ThermalPrinter(mac, channel=channel) as printer:
            result = printer.print_qr(data, size=size)

            if result:
                click.echo("QR code printed successfully!")
            else:
                click.echo("Failed to print QR code.")
                sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command("print-barcode")
@click.option("--mac", "-m", help="Printer MAC address (or uses default from config)")
@click.option("--data", "-d", required=True, help="Barcode data")
@click.option("--channel", "-c", default=None, help="RFCOMM channel (uses config default)")
@click.option("--type", "barcode_type", type=click.Choice(["EAN13", "EAN8", "UPCA", "CODE39", "CODE128", "ITF"]), default="CODE128")
@click.option("--height", type=int, default=80, help="Barcode height")
@click.option("--width", type=int, default=2, help="Barcode width")
def print_barcode(mac, data, channel, barcode_type, height, width):
    """Print a barcode."""
    mac = mac or config.get_printer_mac()
    channel = channel or config.get_printer_channel()
    if not mac:
        click.echo("Error: No printer configured. Use --mac or run 'thermal-printer set-printer'")
        sys.exit(1)
    
    type_map = {
        "EAN13": BarcodeType.EAN13,
        "EAN8": BarcodeType.EAN8,
        "UPCA": BarcodeType.UPC_A,
        "CODE39": BarcodeType.CODE39,
        "CODE128": BarcodeType.CODE128,
        "ITF": BarcodeType.ITF,
    }

    try:
        with ThermalPrinter(mac, channel=channel) as printer:
            result = printer.print_barcode(
                data,
                barcode_type=type_map[barcode_type],
                height=height,
                width=width
            )

            if result:
                click.echo("Barcode printed successfully!")
            else:
                click.echo("Failed to print barcode.")
                sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command("print-image")
@click.option("--mac", "-m", help="Printer MAC address (or uses default from config)")
@click.option("--file", "-f", required=True, help="Image file path")
@click.option("--channel", "-c", default=None, help="RFCOMM channel (uses config default)")
def print_image(mac, file, channel):
    """Print an image."""
    mac = mac or config.get_printer_mac()
    channel = channel or config.get_printer_channel()
    if not mac:
        click.echo("Error: No printer configured. Use --mac or run 'thermal-printer set-printer'")
        sys.exit(1)
    
    try:
        with ThermalPrinter(mac, channel=channel) as printer:
            result = printer.print_image(file)

            if result:
                click.echo("Image printed successfully!")
            else:
                click.echo("Failed to print image.")
                sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command("bt-status")
def bt_status():
    """Check Bluetooth adapter status."""
    status = check_bluetooth_status()

    click.echo("Bluetooth Status:")
    click.echo(f"  Powered: {status['powered']}")
    click.echo(f"  Discoverable: {status['discoverable']}")

    if status.get("adapters"):
        click.echo("  Adapters:")
        for adapter in status["adapters"]:
            click.echo(f"    - {adapter['name']}: {adapter['mac']}")
    else:
        click.echo("  No adapters found.")

    if status.get("error"):
        click.echo(f"  Error: {status['error']}")


@cli.command("set-printer")
@click.option("--mac", "-m", required=True, help="Printer MAC address")
@click.option("--channel", "-c", default=1, help="RFCOMM channel (default: 1)")
def set_printer(mac, channel):
    """Set the default printer (saves to config file)."""
    normalized_mac = config.set_printer_mac(mac)
    config.set_printer_channel(channel)
    
    click.echo(f"Default printer set to: {normalized_mac}")
    click.echo(f"Channel: {channel}")
    click.echo(f"Config saved to: {config.get_config_path()}")


@cli.command("remove-printer")
def remove_printer():
    """Remove the default printer from config."""
    config_path = config.get_config_path()
    if config_path.exists():
        config_path.unlink()
        click.echo("Default printer removed.")
    else:
        click.echo("No config file found.")


@cli.command("show-printer")
def show_printer():
    """Show the current default printer."""
    printer = config.get_default_printer()
    if printer:
        click.echo(f"MAC Address: {printer['mac_address']}")
        click.echo(f"Channel: {printer['channel']}")
    else:
        click.echo("No default printer configured.")
        click.echo("Use --mac to specify a printer or run 'thermal-printer set-printer' to configure one.")


@cli.command("select-printer")
@click.option("--timeout", default=10, help="Scan duration in seconds")
@click.option("--save/--no-save", default=True, help="Save selection as default")
def select_printer(timeout, save):
    """Interactively select a printer from discovered devices."""
    click.echo(f"Scanning for Bluetooth devices for {timeout} seconds...")
    click.echo("-" * 50)

    scanner = BluetoothScanner(duration=timeout)
    devices = scanner.discover_devices()

    if not devices:
        click.echo("No devices found.")
        return

    click.echo(f"Found {len(devices)} device(s):\n")
    for i, device in enumerate(devices, 1):
        click.echo(f"  {i}. {device.address} - {device.name or 'Unknown'}")

    click.echo(f"\n  0. Enter MAC address manually")
    
    choice = click.prompt("\nSelect a printer", type=int, default=1)
    
    if choice == 0:
        mac = click.prompt("Enter MAC address (e.g., 98:B2:6A:F7:AD:50)")
    elif 1 <= choice <= len(devices):
        mac = devices[choice - 1].address
    else:
        click.echo("Invalid selection.")
        return

    if save:
        config.set_printer_mac(mac)
        click.echo(f"\nDefault printer set to: {mac}")
        click.echo(f"Config saved to: {config.get_config_path()}")
    else:
        click.echo(f"\nSelected printer: {mac}")
        click.echo("Use --mac flag or set THERMAL_PRINTER_MAC environment variable to use it.")


@cli.command("bind-rfcomm")
@click.option("--mac", "-m", required=True, help="Printer MAC address")
@click.option("--channel", "-c", default=None, help="RFCOMM channel (uses config default)")
@click.option("--device", "-d", default="/dev/rfcomm0", help="RFCOMM device path")
def bind_rfcomm(mac, channel, device):
    """Bind printer to RFCOMM device (requires sudo)."""
    from .connection import BluetoothConnection

    click.echo(f"Binding {mac} to {device}...")

    conn = BluetoothConnection(mac, channel=channel, rfcomm_device=device)

    if conn.bind_rfcomm():
        click.echo("Successfully bound!")
        click.echo(f"Device: {device}")
        click.echo("\nYou can now connect using the device path.")
    else:
        click.echo("Failed to bind. Make sure you have sudo permissions.")
        sys.exit(1)


@cli.command("release-rfcomm")
@click.option("--device", "-d", default="/dev/rfcomm0", help="RFCOMM device path")
def release_rfcomm(device):
    """Release RFCOMM device (requires sudo)."""
    from .connection import BluetoothConnection

    click.echo(f"Releasing {device}...")

    conn = BluetoothConnection("00:00:00:00:00:00", rfcomm_device=device)

    if conn.release_rfcomm():
        click.echo("Successfully released!")
    else:
        click.echo("Failed to release. Make sure you have sudo permissions.")
        sys.exit(1)


@cli.command("test")
@click.option("--mac", "-m", help="Printer MAC address (or uses default from config)")
@click.option("--channel", "-c", default=None, help="RFCOMM channel (uses config default)")
def test_printer(mac, channel):
    """Run a simple test print."""
    mac = mac or config.get_printer_mac()
    channel = channel or config.get_printer_channel()
    if not mac:
        click.echo("Error: No printer configured. Use --mac or run 'thermal-printer set-printer'")
        sys.exit(1)
    
    click.echo(f"Running printer test on {mac}...")

    try:
        with ThermalPrinter(mac, channel=channel) as printer:
            click.echo("1. Initializing printer...")
            if not printer.initialize():
                click.echo("Failed to initialize printer")
                sys.exit(1)

            click.echo("2. Printing text...")
            if not printer.print_text("Thermal Printer Test", align=Alignment.CENTER, size=(2, 2)):
                click.echo("Failed to print text")
                sys.exit(1)

            click.echo("3. Printing line...")
            if not printer.print_line("-"):
                click.echo("Failed to print line")
                sys.exit(1)

            click.echo("4. Printing QR code...")
            if not printer.print_qr("https://example.com"):
                click.echo("Failed to print QR")
                sys.exit(1)

            click.echo("5. Printing barcode...")
            if not printer.print_barcode("123456789"):
                click.echo("Failed to print barcode")
                sys.exit(1)

            click.echo("6. Cutting paper...")
            if not printer.cut_paper():
                click.echo("Failed to cut paper")
                sys.exit(1)

            click.echo("\nTest completed successfully!")
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
