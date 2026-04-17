"""Main Thermal Printer class."""

from typing import Optional, List
from PIL import Image, ImageDraw, ImageFont
import qrcode

from .connection import BluetoothConnection
from .commands import (
    ESCPOSCommands,
    Alignment,
    BarcodeType,
    QRErrorCorrection,
    create_receipt,
    YHKCommands,
    is_yhk_printer
)


class ThermalPrinter:
    """Main class for thermal printer operations."""

    WIDTH_58MM = 32
    WIDTH_80MM = 48
    YHK_WIDTH = 384  # YHK printers use 384 dots width

    def __init__(
        self,
        mac_address: str,
        channel: int = 1,
        width: int = WIDTH_58MM,
        encoding: str = "utf-8",
        printer_model: str = None,
        font_path: str = None,
        font_size: int = 30
    ):
        """
        Initialize thermal printer.

        Args:
            mac_address: MAC address of the printer
            channel: RFCOMM channel (default: 1)
            width: Character width (32 for 58mm, 48 for 80mm)
            encoding: Text encoding
            printer_model: "escpos" or "yhk_cat" (auto-detected if not specified)
            font_path: Path to TTF font file (for YHK printers)
            font_size: Font size for text (for YHK printers)
        """
        self.mac_address = mac_address
        self.channel = channel
        self.width = width
        self.encoding = encoding
        self.connection: Optional[BluetoothConnection] = None
        self._connected = False
        self._printer_model = printer_model
        self._printer_name = None
        self.font_path = font_path
        self.font_size = font_size

    def connect(self) -> bool:
        """
        Connect to the printer.

        Returns:
            True if connected, False otherwise
        """
        self.connection = BluetoothConnection(
            mac_address=self.mac_address,
            channel=self.channel
        )
        self._connected = self.connection.connect()
        
        if self._connected and not self._printer_model:
            self._detect_printer_model()
        
        return self._connected

    def _detect_printer_model(self):
        """Detect printer model by querying its name."""
        try:
            from .scanner import BluetoothScanner
            scanner = BluetoothScanner()
            self._printer_name = scanner.lookup_name(self.mac_address)
            if self._printer_name and is_yhk_printer(self._printer_name):
                self._printer_model = "yhk_cat"
                print(f"Detected YHK Cat printer: {self._printer_name}")
            else:
                self._printer_model = "escpos"
        except Exception:
            self._printer_model = "escpos"

    def _get_commands(self):
        """Get appropriate command set based on printer model."""
        if self._printer_model == "yhk_cat":
            return YHKCommands()
        return ESCPOSCommands()

    def disconnect(self):
        """Disconnect from the printer."""
        if self.connection:
            self.connection.disconnect()
            self._connected = False

    def is_connected(self) -> bool:
        """Check if connected."""
        if self.connection:
            return self.connection.is_connected()
        return False

    def _ensure_connected(self):
        """Ensure printer is connected."""
        if not self.is_connected():
            raise RuntimeError("Printer not connected. Call connect() first.")

    def send(self, data: bytes) -> bool:
        """Send raw data to printer."""
        self._ensure_connected()
        
        if self._printer_model == "yhk_cat":
            cmds = self._get_commands()
            self.connection.send(cmds.start_print())
        
        result = self.connection.send(data)
        
        if self._printer_model == "yhk_cat":
            cmds = self._get_commands()
            self.connection.send(cmds.end_print())
        
        return result

    def initialize(self) -> bool:
        """Initialize the printer."""
        cmds = self._get_commands()
        return self.send(cmds.initialize())

    def _create_text_image(self, text: str, font_size: int = None, bold: bool = False) -> Image.Image:
        """Create a bitmap image from text for YHK printers."""
        if font_size is None:
            font_size = self.font_size
        
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Wrap text to fit printer width (no padding)
        max_width = self.YHK_WIDTH
        words = text.split()
        lines = []
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
        
        if not lines:
            lines = [""]
        
        # Calculate image height based on number of lines
        line_height = int(font_size * 1.3)
        img_height = (len(lines) * line_height) + 10
        
        img = Image.new('1', (self.YHK_WIDTH, img_height), color=0)
        draw = ImageDraw.Draw(img)
        
        # Draw each line (white text on black background)
        y = 5
        for line in lines:
            draw.text((2, y), line, fill=1, font=font)
            y += line_height
        
        return img

    def _send_image(self, img: Image.Image) -> bool:
        """Send a bitmap image to the printer."""
        import struct
        
        n = (img.width + 7) // 8
        buf = b'\x1d\x76\x30\x00'
        buf += struct.pack('B', n % 256)
        buf += struct.pack('B', n // 256)
        buf += struct.pack('B', img.height % 256)
        buf += struct.pack('B', img.height // 256)
        buf += img.tobytes()
        
        return self.connection.send(buf)

    def _print_text_as_image(self, text: str, font_size: int = None) -> bool:
        """Print text by converting to image (for YHK printers)."""
        import time
        
        if font_size is None:
            font_size = self.font_size
        
        img = self._create_text_image(text, font_size=font_size)
        
        cmds = self._get_commands()
        
        # YHK sequence
        self.connection.send(cmds.initialize())
        time.sleep(0.3)
        self.connection.send(cmds.start_print())
        time.sleep(0.3)
        
        # Send image
        self._send_image(img)
        time.sleep(0.5)
        
        # End
        self.connection.send(cmds.end_print())
        
        return True

    def print_text(
        self,
        text: str,
        align: Alignment = Alignment.LEFT,
        bold: bool = False,
        underline: bool = False,
        size: tuple = (1, 1)
    ) -> bool:
        """
        Print text with formatting.

        Args:
            text: Text to print
            align: Text alignment
            bold: Bold text
            underline: Underlined text
            size: Text size (width, height)

        Returns:
            True if successful
        """
        # For YHK printers, convert text to image
        if self._printer_model == "yhk_cat":
            return self._print_text_as_image(text, font_size=self.font_size)
        
        # Standard ESC/POS printers
        cmds = self._get_commands()
        data = b""

        data += cmds.initialize()
        data += cmds.set_alignment(align)
        data += cmds.set_text_size(size[0], size[1])

        if bold:
            data += cmds.bold_on()
        if underline:
            data += cmds.underline_on()

        data += text.encode(self.encoding)
        data += b"\n"

        if bold:
            data += cmds.bold_off()
        if underline:
            data += cmds.underline_off()

        return self.send(data)

    def print_line(self, char: str = "-") -> bool:
        """Print a line of characters."""
        return self.print_text(char * self.width)

    def print_lines(self, count: int = 1) -> bool:
        """Print blank lines."""
        cmds = self._get_commands()
        return self.send(cmds.line_feed(count))

    def print_qr(
        self,
        data: str,
        size: int = 6,
        error_correction: QRErrorCorrection = QRErrorCorrection.M
    ) -> bool:
        """
        Print QR code.

        Args:
            data: Data to encode in QR code
            size: QR code size (1-16)
            error_correction: Error correction level

        Returns:
            True if successful
        """
        cmds = self._get_commands()
        qr_cmds = cmds.print_qr(data, size, error_correction)
        return self.send(qr_cmds)

    def print_barcode(
        self,
        data: str,
        barcode_type: BarcodeType = BarcodeType.CODE128,
        height: int = 80,
        width: int = 2
    ) -> bool:
        """
        Print barcode.

        Args:
            data: Barcode data
            barcode_type: Barcode type
            height: Barcode height
            width: Barcode width

        Returns:
            True if successful
        """
        cmds = self._get_commands()
        bc_cmds = cmds.print_barcode(data, barcode_type, height, width)
        return self.send(bc_cmds)

    def print_image(
        self,
        image_path: str,
        grayscale: bool = True
    ) -> bool:
        """
        Print an image.

        Args:
            image_path: Path to image file
            grayscale: Convert to grayscale

        Returns:
            True if successful
        """
        try:
            img = Image.open(image_path)

            max_width = self.width * 8
            img.thumbnail((max_width, 1024), Image.Resampling.LANCZOS)

            if grayscale:
                img = img.convert('L')

            img = img.convert('1', dither=Image.Dither.FLOYDSTEINBERG)

            width = img.width
            height = img.height
            pixels = img.tobytes()

            cmds = self._get_commands()
            data = cmds.print_bit_image(pixels, width, height, 0)

            return self.send(data)
        except Exception as e:
            print(f"Error printing image: {e}")
            return False

    def print_receipt(
        self,
        store_name: str,
        items: List[dict],
        total: float,
        footer: str = None,
        receipt_number: str = None,
        date: str = None
    ) -> bool:
        """
        Print a receipt.

        Args:
            store_name: Store name
            items: List of dicts with 'name', 'price', 'qty'
            total: Total amount
            footer: Footer text
            receipt_number: Receipt number
            date: Date string

        Returns:
            True if successful
        """
        # For YHK printers, convert receipt to image
        if self._printer_model == "yhk_cat":
            return self._print_receipt_as_image(
                store_name=store_name,
                items=items,
                total=total,
                footer=footer,
                receipt_number=receipt_number,
                date=date
            )
        
        data = create_receipt(
            store_name=store_name,
            items=items,
            total=total,
            width=self.width,
            footer=footer,
            receipt_number=receipt_number,
            date=date
        )
        return self.send(data)

    def _print_receipt_as_image(
        self,
        store_name: str,
        items: List[dict],
        total: float,
        footer: str = None,
        receipt_number: str = None,
        date: str = None
    ) -> bool:
        """Print receipt by converting to image (for YHK printers)."""
        import time
        
        # Format receipt lines - maximize width (48 chars for 384 dots)
        lines = []
        width = 46
        
        lines.append("=" * width)
        lines.append(store_name.center(width))
        lines.append("=" * width)
        lines.append("")
        
        if receipt_number:
            lines.append(f"Receipt: {receipt_number}")
        if date:
            lines.append(f"Date: {date}")
        lines.append("-" * width)
        
        for item in items:
            name = item.get('name', '')
            price = item.get('price', 0)
            qty = item.get('qty', 1)
            line_total = price * qty
            left = f"{name} x{qty}"
            right = f"N{line_total:.2f}"
            spaces = width - len(left) - len(right)
            lines.append(left + " " * spaces + right)
        
        lines.append("-" * width)
        
        left = "TOTAL"
        right = f"N{total:.2f}"
        spaces = width - len(left) - len(right)
        lines.append(left + " " * spaces + right)
        
        lines.append("=" * width)
        
        if footer:
            lines.append("")
            lines.append(footer.center(width))
        
        # Create image
        font_size = 18
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        line_height = int(font_size * 1.3)
        img_height = (len(lines) * line_height) + 20
        
        img = Image.new('1', (self.YHK_WIDTH, img_height), color=0)
        draw = ImageDraw.Draw(img)
        
        y = 10
        for line in lines:
            draw.text((10, y), line, fill=1, font=font)
            y += line_height
        
        # Send to printer
        cmds = self._get_commands()
        self.connection.send(cmds.initialize())
        time.sleep(0.3)
        self.connection.send(cmds.start_print())
        time.sleep(0.3)
        self._send_image(img)
        time.sleep(0.5)
        self.connection.send(cmds.end_print())
        
        return True

    def cut_paper(self, full: bool = True) -> bool:
        """Cut the paper."""
        cmds = self._get_commands()
        return self.send(cmds.cut_paper(full))

    def partial_cut(self) -> bool:
        """Partially cut the paper."""
        cmds = self._get_commands()
        return self.send(cmds.partial_cut())

    def beep(self) -> bool:
        """Make a beep sound."""
        cmds = self._get_commands()
        return self.send(cmds.beep())

    def open_cash_drawer(self) -> bool:
        """Open cash drawer."""
        cmds = self._get_commands()
        return self.send(cmds.open_cash_drawer())

    def status(self) -> dict:
        """
        Get printer status.

        Returns:
            Dictionary with status information
        """
        return {
            "connected": self.is_connected(),
            "mac_address": self.mac_address,
            "channel": self.channel,
            "width": self.width
        }

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def print_banner(
    mac_address: str,
    text: str,
    channel: int = 1
) -> bool:
    """
    Print a simple banner.

    Args:
        mac_address: Printer MAC address
        text: Banner text
        channel: RFCOMM channel

    Returns:
        True if successful
    """
    with ThermalPrinter(mac_address, channel=channel) as printer:
        printer.initialize()
        printer.print_text(text, align=Alignment.CENTER, size=(2, 2))
        printer.print_lines(3)
        printer.cut_paper()
    return True


def print_receipt_simple(
    mac_address: str,
    items: List[dict],
    total: float,
    store_name: str = "Store",
    channel: int = 1
) -> bool:
    """
    Print a simple receipt.

    Args:
        mac_address: Printer MAC address
        items: List of items with 'name', 'price', 'qty'
        total: Total amount
        store_name: Store name
        channel: RFCOMM channel

    Returns:
        True if successful
    """
    import datetime

    with ThermalPrinter(mac_address, channel=channel) as printer:
        return printer.print_receipt(
            store_name=store_name,
            items=items,
            total=total,
            receipt_number="001",
            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            footer="Thank you for your purchase!"
        )
