#!/usr/bin/env python3
"""Easy print script for YHK thermal printer."""

import socket
import time
import struct
from PIL import Image, ImageDraw, ImageFont
import sys
import os

# Try to get MAC from environment or config
PRINTER_MAC = os.environ.get("THERMAL_PRINTER_MAC", "98:B2:6A:F7:AD:50")
PRINTER_CHANNEL = int(os.environ.get("THERMAL_PRINTER_CHANNEL", "2"))
PRINTER_WIDTH = 384


def wrap_text(text: str, font, max_width: int) -> list:
    """Wrap text into lines that fit within max_width."""
    lines = []
    words = text.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines


def create_text_image(lines: list, font_size: int = 25, left_margin: int = 5) -> Image.Image:
    """Create an image from a list of lines of text."""
    
    # Load font
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
            font_size
        )
    except:
        font = ImageFont.load_default()
    
    line_height = int(font_size * 1.3)
    img_height = (len(lines) * line_height) + 20
    
    img = Image.new('1', (PRINTER_WIDTH, img_height), color=0)
    draw = ImageDraw.Draw(img)
    
    y = 10
    for line in lines:
        draw.text((left_margin, y), line, fill=1, font=font)
        y += line_height
    
    return img


def send_image(s, img: Image.Image):
    """Send image to printer."""
    n = (img.width + 7) // 8
    buf = b'\x1d\x76\x30\x00'
    buf += struct.pack('B', n % 256)
    buf += struct.pack('B', n // 256)
    buf += struct.pack('B', img.height % 256)
    buf += struct.pack('B', img.height // 256)
    buf += img.tobytes()
    s.send(buf)
    time.sleep(0.5)


def print_text(text: str, font_size: int = 30):
    """Print text to YHK thermal printer with automatic wrapping."""
    
    max_text_width = PRINTER_WIDTH - 40
    
    # Load font
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
            font_size
        )
    except:
        font = ImageFont.load_default()
    
    line_height = int(font_size * 1.2)
    lines = wrap_text(text, font, max_text_width)
    img_height = (len(lines) * line_height) + 20
    
    img = Image.new('1', (PRINTER_WIDTH, img_height), color=0)
    draw = ImageDraw.Draw(img)
    
    y = 10
    for line in lines:
        draw.text((20, y), line, fill=1, font=font)
        y += line_height
    
    # Connect
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.settimeout(60)
    s.connect((PRINTER_MAC, PRINTER_CHANNEL))
    
    time.sleep(0.5)
    s.send(b'\x1b\x40')
    time.sleep(0.5)
    s.send(b'\x1d\x49\xf0\x19')
    time.sleep(0.5)
    
    send_image(s, img)
    
    s.send(b'\x0a\x0a\x0a\x0a')
    time.sleep(1)
    s.close()


def print_image(image_path: str):
    """Print an image file."""
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return
    
    # Convert to 1-bit if needed
    if img.mode != '1':
        img = img.convert('1')
    
    # Resize if wider than printer
    if img.width > PRINTER_WIDTH:
        ratio = PRINTER_WIDTH / img.width
        new_height = int(img.height * ratio)
        img = img.resize((PRINTER_WIDTH, new_height), Image.Resampling.LANCZOS)
    
    # Pad to full width if narrower
    if img.width < PRINTER_WIDTH:
        padded = Image.new('1', (PRINTER_WIDTH, img.height), color=1)
        padded.paste(img, (0, 0))
        img = padded
    
    # Connect
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.settimeout(60)
    s.connect((PRINTER_MAC, PRINTER_CHANNEL))
    
    time.sleep(0.5)
    s.send(b'\x1b\x40')
    time.sleep(0.5)
    s.send(b'\x1d\x49\xf0\x19')
    time.sleep(0.5)
    
    send_image(s, img)
    
    s.send(b'\x0a\x0a\x0a\x0a')
    time.sleep(1)
    s.close()


def print_receipt(store_name: str, items: list, total: float, footer: str = None):
    """
    Print a receipt.
    
    items: list of dicts with 'name', 'price', 'qty'
    Example: [{"name": "Coffee", "price": 3.50, "qty": 2}, {"name": "Cake", "price": 5.00, "qty": 1}]
    """
    lines = []
    
    # Store name (centered, larger)
    lines.append("=" * 30)
    lines.append(store_name.center(30))
    lines.append("=" * 30)
    lines.append("")
    
    # Items
    for item in items:
        name = item.get('name', '')
        price = item.get('price', 0)
        qty = item.get('qty', 1)
        line_total = price * qty
        
        # Format: Name xQty    $Total
        left = f"{name} x{qty}"
        right = f"₦{line_total:.2f}"
        spaces = 30 - len(left) - len(right)
        lines.append(left + " " * spaces + right)
    
    lines.append("")
    lines.append("-" * 30)
    
    # Total
    total_line = "TOTAL"
    total_amount = f"₦{total:.2f}"
    spaces = 30 - len(total_line) - len(total_amount)
    lines.append(total_line + " " * spaces + total_amount)
    
    lines.append("=" * 30)
    lines.append("")
    
    # Footer
    if footer:
        lines.append(footer.center(30))
        lines.append("")
    
    # Create image and print
    img = create_text_image(lines, font_size=22)
    
    # Connect
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.settimeout(60)
    s.connect((PRINTER_MAC, PRINTER_CHANNEL))
    
    time.sleep(0.5)
    s.send(b'\x1b\x40')
    time.sleep(0.5)
    s.send(b'\x1d\x49\xf0\x19')
    time.sleep(0.5)
    
    send_image(s, img)
    
    s.send(b'\x0a\x0a\x0a\x0a')
    time.sleep(1)
    s.close()


import re

def format_epin(epin: str) -> str:
    """Format EPIN with dashes every 4 digits."""
    # Remove any existing dashes/spaces
    epin = epin.replace('-', '').replace(' ', '')
    
    # Split into groups of 4 and join with dashes
    return '-'.join(re.findall('.{1,4}', epin))


def parse_epin_line(line: str) -> dict:
    """Parse an EPIN line and extract EPIN, network, and amount."""
    parts = line.strip().split()
    
    if len(parts) < 2:
        return None
    
    # EPIN is typically the first part (digits only or alphanumeric)
    # Network is after EPIN
    # Amount is after network
    
    epin = parts[0]
    network = None
    amount = None
    
    # Find network and amount
    for i, part in enumerate(parts[1:], 1):
        part_upper = part.upper()
        
        # Check for network
        if part_upper in ['AIRTEL', 'MTN', 'GLO', '9MOBILE']:
            network = part_upper
        elif 'AIRTEL' in part_upper:
            network = 'AIRTEL'
        elif 'MTN' in part_upper:
            network = 'MTN'
        elif 'GLO' in part_upper:
            network = 'GLO'
        elif '9MOBILE' in part_upper or '9MOBILE' in part_upper:
            network = '9MOBILE'
        
        # Check for amount (100, 200, 500)
        if part.isdigit():
            if int(part) in [100, 200, 500, 1000, 2000, 5000]:
                amount = int(part)
    
    # If amount not found, try last part
    if amount is None and parts[-1].isdigit():
        amount = int(parts[-1])
    
    return {'epin': epin, 'network': network, 'amount': amount}


def print_epins(file_path: str, separator_dashes: int = 16, company_name: str = None):
    """Print EPINs from a file."""
    
    # Read the file
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Parse each line
    epins = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parsed = parse_epin_line(line)
        if parsed and parsed['network'] and parsed['amount']:
            epins.append(parsed)
    
    if not epins:
        print("No valid EPINs found in file")
        return
    
    # Group by network and amount
    groups = {}
    for epin in epins:
        key = (epin['network'], epin['amount'])
        if key not in groups:
            groups[key] = []
        groups[key].append(epin['epin'])
    
    # Create formatted lines for printing
    print_lines = []
    
    separator = "-" * separator_dashes
    
    for (network, amount), epin_list in groups.items():
        for epin in epin_list:
            formatted_epin = format_epin(epin)
            
            # Build the line
            if company_name:
                line = f"{company_name} {network} ₦{amount}"
            else:
                line = f"{network} ₦{amount}"
            
            print_lines.append(line)
            print_lines.append(f"{formatted_epin} *311*PIN#")
            print_lines.append(separator)
    
    # Print in batches (max 5 EPINs per batch)
    max_epins_per_batch = 5
    
    # Split into batches (each EPIN has 3 lines)
    lines_per_epin = 3
    max_lines_per_batch = max_epins_per_batch * lines_per_epin
    
    batches = []
    for i in range(0, len(print_lines), max_lines_per_batch):
        batches.append(print_lines[i:i + max_lines_per_batch])
    
    # Connect once
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.settimeout(60)
    s.connect((PRINTER_MAC, PRINTER_CHANNEL))
    
    time.sleep(0.5)
    s.send(b'\x1b\x40')
    time.sleep(0.5)
    
    # Print each batch
    for batch_num, batch_lines in enumerate(batches):
        print(f"Printing batch {batch_num + 1} of {len(batches)}...")
        
        img = create_text_image(batch_lines, font_size=18, left_margin=5)
        
        s.send(b'\x1d\x49\xf0\x19')
        time.sleep(0.5)
        
        send_image(s, img)
        
        time.sleep(0.5)
    
    s.send(b'\x0a\x0a\x0a\x0a')
    time.sleep(1)
    s.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Check for EPIN mode
        if sys.argv[1] == "--epin":
            # Parse arguments: --epin filename [-d dashes] [-c company]
            file_path = None
            separator_dashes = 16
            company_name = None
            
            i = 2
            while i < len(sys.argv):
                if sys.argv[i] == '-d' and i + 1 < len(sys.argv):
                    separator_dashes = int(sys.argv[i + 1])
                    i += 2
                elif sys.argv[i] == '-c' and i + 1 < len(sys.argv):
                    company_name = sys.argv[i + 1]
                    i += 2
                else:
                    file_path = sys.argv[i]
                    i += 1
            
            if not file_path:
                print("Usage: print.py --epin filename [-d dashes] [-c 'Company Name']")
                print("Example: print.py --epin epins.txt -d 20 -c 'DAMMIE OPTIMUS'")
                sys.exit(1)
            
            print(f"Printing EPINs from {file_path}...")
            print_epins(file_path, separator_dashes, company_name)
            print("Done!")
        
        # Check for image mode
        elif sys.argv[1] == "--image":
            if len(sys.argv) < 3:
                print("Usage: print.py --image /path/to/image.jpg")
                print("Example: print.py --image photo.jpg")
                sys.exit(1)
            
            image_path = sys.argv[2]
            print(f"Printing image: {image_path}")
            print_image(image_path)
            print("Done!")
        
        # Check for receipt mode
        elif sys.argv[1] == "--receipt":
            if len(sys.argv) < 3:
                print("Usage: print.py --receipt 'Store Name' item1 price qty [item2 price qty...]")
                print("Example: print.py --receipt 'My Store' Coffee 350 2 Cake 500 1")
                sys.exit(1)
            
            store_name = sys.argv[2]
            items = []
            
            # Parse remaining arguments: name price qty
            args = sys.argv[3:]
            i = 0
            while i < len(args) - 2:
                name = args[i]
                try:
                    price = float(args[i + 1])
                    qty = int(args[i + 2])
                    items.append({"name": name, "price": price, "qty": qty})
                except:
                    pass
                i += 3
            
            total = sum(item["price"] * item["qty"] for item in items)
            
            print(f"Printing receipt for {store_name}...")
            print_receipt(store_name, items, total)
            print("Done!")
        else:
            # Regular text mode
            text = " ".join(sys.argv[1:])
            print(f"Printing: {text}")
            print_text(text)
            print("Done!")
    else:
        print("HELLO WORLD")
        print_text("HELLO WORLD")
        print("Done!")
