"""Example scripts for thermal printer."""

import sys
sys.path.insert(0, "../src")

from thermal_printer import ThermalPrinter, Alignment, BarcodeType
from thermal_printer import config


def get_printer_config():
    """Get printer MAC and channel from config or environment."""
    mac = config.get_printer_mac()
    channel = config.get_printer_channel()
    if not mac:
        raise RuntimeError(
            "No printer configured. Set THERMAL_PRINTER_MAC env var, "
            "run 'thermal-printer set-printer' or 'thermal-printer select-printer'"
        )
    return mac, channel


PRINTER_MAC, PRINTER_CHANNEL = get_printer_config()


def print_hello_world():
    """Print simple hello world."""
    with ThermalPrinter(PRINTER_MAC, channel=PRINTER_CHANNEL) as printer:
        printer.initialize()
        printer.print_text("Hello World!", align=Alignment.CENTER)
        printer.print_lines(3)
        printer.cut_paper()


def print_receipt_example():
    """Print a receipt example."""
    items = [
        {"name": "Coffee", "price": 3.50, "qty": 2},
        {"name": "Sandwich", "price": 6.00, "qty": 1},
        {"name": "Cookie", "price": 2.00, "qty": 3},
    ]
    total = sum(item["price"] * item["qty"] for item in items)

    with ThermalPrinter(PRINTER_MAC, channel=PRINTER_CHANNEL) as printer:
        printer.print_receipt(
            store_name="My Coffee Shop",
            items=items,
            total=total,
            receipt_number="001",
            footer="Thank you for your purchase!"
        )


def print_banner(text: str):
    """Print a banner."""
    with ThermalPrinter(PRINTER_MAC, channel=PRINTER_CHANNEL) as printer:
        printer.print_text(text, align=Alignment.CENTER, size=(2, 2))
        printer.print_lines(3)
        printer.cut_paper()


def print_qr_code(url: str):
    """Print a QR code."""
    with ThermalPrinter(PRINTER_MAC, channel=PRINTER_CHANNEL) as printer:
        printer.print_qr(url, size=8)
        printer.print_lines(3)
        printer.cut_paper()


def print_barcode_example():
    """Print a barcode."""
    with ThermalPrinter(PRINTER_MAC, channel=PRINTER_CHANNEL) as printer:
        printer.print_barcode("123456789", BarcodeType.CODE128)
        printer.print_lines(3)
        printer.cut_paper()


def print_formatted_text():
    """Print text with various formatting."""
    with ThermalPrinter(PRINTER_MAC, channel=PRINTER_CHANNEL) as printer:
        printer.print_text("Normal Text")
        printer.print_text("Bold Text", bold=True)
        printer.print_text("Underlined Text", underline=True)
        printer.print_text("Double Size", size=(2, 2))
        printer.print_text("Centered", align=Alignment.CENTER)
        printer.print_text("Right Aligned", align=Alignment.RIGHT)
        printer.print_lines(3)
        printer.cut_paper()


def print_recharge_card():
    """Print a recharge card."""
    import random

    card_number = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    pin = f"{random.randint(100, 999)}-{random.randint(100, 999)}"

    with ThermalPrinter(PRINTER_MAC, channel=PRINTER_CHANNEL) as printer:
        printer.initialize()
        printer.print_text("RECHARGE CARD", align=Alignment.CENTER, size=(2, 2))
        printer.print_lines(1)
        printer.print_line("-" * 32)
        printer.print_text(f"Card: {card_number}", align=Alignment.CENTER)
        printer.print_text(f"PIN: {pin}", align=Alignment.CENTER)
        printer.print_text("Value: $50.00", align=Alignment.CENTER)
        printer.print_line("-" * 32)
        printer.print_text("Expires: 30 days", align=Alignment.CENTER)
        printer.print_lines(3)
        printer.cut_paper()


def print_image_example(image_path: str):
    """Print an image."""
    with ThermalPrinter(PRINTER_MAC, channel=PRINTER_CHANNEL) as printer:
        printer.print_image(image_path)
        printer.print_lines(3)
        printer.cut_paper()


def continuous_print():
    """Example of continuous printing."""
    with ThermalPrinter(PRINTER_MAC, channel=PRINTER_CHANNEL) as printer:
        for i in range(5):
            printer.print_text(f"Print job #{i + 1}")
            printer.print_line("=" * 32)

        printer.cut_paper()


if __name__ == "__main__":
    import sys

    examples = {
        "hello": print_hello_world,
        "receipt": print_receipt_example,
        "banner": lambda: print_banner("Welcome!"),
        "qr": lambda: print_qr_code("https://example.com"),
        "barcode": print_barcode_example,
        "formatted": print_formatted_text,
        "recharge": print_recharge_card,
        "continuous": continuous_print,
    }

    if len(sys.argv) < 2:
        print("Usage: python print_examples.py <example>")
        print("\nAvailable examples:")
        for name in examples:
            print(f"  - {name}")
        sys.exit(1)

    example_name = sys.argv[1]
    if example_name not in examples:
        print(f"Unknown example: {example_name}")
        sys.exit(1)

    print(f"Running {example_name} example...")
    examples[example_name]()
    print("Done!")
