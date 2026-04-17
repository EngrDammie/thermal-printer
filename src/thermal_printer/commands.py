"""ESC/POS command constants and helpers."""

from enum import IntEnum
from typing import List


class ESCPOS:
    """ESC/POS command constants."""

    ESC = 0x1B
    GS = 0x1D
    DLE = 0x10
    DC1 = 0x11
    DC2 = 0x12
    DC3 = 0x13
    DC4 = 0x14
    FS = 0x1C
    SP = 0x20
    HT = 0x09
    LF = 0x0A
    CR = 0x0D
    VT = 0x0B
    FF = 0x0C


class Alignment(IntEnum):
    """Text alignment options."""
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class TextSize(IntEnum):
    """Text size options (width and height 1-8)."""
    NORMAL = 1
    DOUBLE_WIDTH = 2
    DOUBLE_HEIGHT = 2
    DOUBLE = 4
    QUADRUPLE = 8


class BarcodeType(IntEnum):
    """Barcode types."""
    UPC_A = 0
    UPC_E = 1
    EAN13 = 2
    EAN8 = 3
    CODE39 = 4
    ITF = 5
    CODABAR = 6
    CODE93 = 7
    CODE128 = 8


class QRErrorCorrection(IntEnum):
    """QR code error correction levels."""
    L = 0
    M = 1
    Q = 2
    H = 3


class PrinterModel:
    """Printer model types."""
    ESCPOS = "escpos"
    YHK_CAT = "yhk_cat"


class ESCPOSCommands:
    """ESC/POS command builder."""

    @staticmethod
    def initialize() -> bytes:
        """Initialize printer."""
        return bytes([ESCPOS.ESC, 0x40])

    @staticmethod
    def line_feed(lines: int = 1) -> bytes:
        """Feed lines."""
        return bytes([ESCPOS.LF] * lines)

    @staticmethod
    def carriage_return() -> bytes:
        """Carriage return."""
        return bytes([ESCPOS.CR])

    @staticmethod
    def cut_paper(full_cut: bool = True) -> bytes:
        """Cut paper."""
        if full_cut:
            return bytes([ESCPOS.GS, 0x56, 0x00])
        else:
            return bytes([ESCPOS.GS, 0x56, 0x01])

    @staticmethod
    def partial_cut() -> bytes:
        """Partial cut paper."""
        return bytes([ESCPOS.GS, 0x56, 0x01])

    @staticmethod
    def set_alignment(align: Alignment) -> bytes:
        """Set text alignment."""
        return bytes([ESCPOS.ESC, 0x61, align])

    @staticmethod
    def set_text_size(width: int, height: int) -> bytes:
        """
        Set text size.

        Args:
            width: 0-7 (0 = normal, 7 = double width)
            height: 0-7 (0 = normal, 7 = double height)
        """
        size = ((width & 0x07) << 4) | (height & 0x07)
        return bytes([ESCPOS.GS, 0x21, size])

    @staticmethod
    def bold_on() -> bytes:
        """Turn bold on."""
        return bytes([ESCPOS.ESC, 0x45, 0x01])

    @staticmethod
    def bold_off() -> bytes:
        """Turn bold off."""
        return bytes([ESCPOS.ESC, 0x45, 0x00])

    @staticmethod
    def underline_on() -> bytes:
        """Turn underline on."""
        return bytes([ESCPOS.ESC, 0x2D, 0x01])

    @staticmethod
    def underline_off() -> bytes:
        """Turn underline off."""
        return bytes([ESCPOS.ESC, 0x2D, 0x00])

    @staticmethod
    def underline_double() -> bytes:
        """Double underline."""
        return bytes([ESCPOS.ESC, 0x2D, 0x02])

    @staticmethod
    def set_text_color_normal() -> bytes:
        """Set text color normal (usually black)."""
        return bytes([ESCPOS.ESC, 0x72, 0x00])

    @staticmethod
    def set_text_color_red() -> bytes:
        """Set text color red (if supported)."""
        return bytes([ESCPOS.ESC, 0x72, 0x01])

    @staticmethod
    def set_line_spacing(lines: int = 30) -> bytes:
        """Set line spacing in dots."""
        return bytes([ESCPOS.ESC, 0x33, lines])

    @staticmethod
    def set_default_line_spacing() -> bytes:
        """Set default line spacing."""
        return bytes([ESCPOS.ESC, 0x32])

    @staticmethod
    def horizontal_tab() -> bytes:
        """Horizontal tab."""
        return bytes([ESCPOS.HT])

    @staticmethod
    def set_left_margin(dots: int) -> bytes:
        """Set left margin in dots."""
        return bytes([ESCPOS.ESC, 0x6C, dots])

    @staticmethod
    def set_print_width(dots: int) -> bytes:
        """Set print width in dots."""
        return bytes([ESCPOS.GS, 0x57, dots & 0xFF, (dots >> 8) & 0xFF])

    @staticmethod
    def feed_paper(dots: int) -> bytes:
        """Feed paper by dots."""
        return bytes([ESCPOS.ESC, 0x4A, dots])

    @staticmethod
    def beep() -> bytes:
        """Beep/buzzer (if supported)."""
        return bytes([ESCPOS.ESC, 0x42, 0x05, 0x09])

    @staticmethod
    def open_cash_drawer() -> bytes:
        """Open cash drawer (if connected)."""
        return bytes([ESCPOS.ESC, 0x70, 0x00, 0x19, 0xFA])

    @staticmethod
    def kick_drawer_pin2() -> bytes:
        """Kick drawer pin 2."""
        return bytes([ESCPOS.ESC, 0x70, 0x00, 0x19, 0x00])

    @staticmethod
    def kick_drawer_pin5() -> bytes:
        """Kick drawer pin 5."""
        return bytes([ESCPOS.ESC, 0x70, 0x01, 0x19, 0x00])

    @staticmethod
    def initialize_code_page(codepage: str = "cp437") -> bytes:
        """Initialize code page (legacy)."""
        codepages = {
            "cp437": 0,
            "katakana": 1,
            "cp850": 2,
            "cp860": 3,
            "cp863": 4,
            "cp865": 5,
            "west_euro": 6,
            "cp1252": 17,
            "cp866": 18,
            "cp936": 255,
        }
        cp = codepages.get(codepage, 0)
        return bytes([ESCPOS.FS, 0x2D, 0x00, cp])

    @staticmethod
    def set_code_page(codepage: str = "cp437") -> bytes:
        """Set code page."""
        codepages = {
            "cp437": 0,
            "katakana": 1,
            "cp850": 2,
            "cp860": 3,
            "cp863": 4,
            "cp865": 5,
            "west_euro": 6,
            "cp1252": 17,
            "cp866": 18,
            "cp936": 255,
        }
        cp = codepages.get(codepage, 0)
        return bytes([ESCPOS.ESC, 0x74, cp])

    @staticmethod
    def print_barcode(
        data: str,
        barcode_type: BarcodeType,
        height: int = 80,
        width: int = 2,
        text_position: int = 2
    ) -> bytes:
        """
        Print barcode.

        Args:
            data: Barcode data
            barcode_type: Barcode type
            height: Barcode height in dots
            width: Barcode width (2-6)
            text_position: Text position (0=none, 1=above, 2=below, 3=both)
        """
        cmd = bytes([
            ESCPOS.GS, 0x68, height,
            ESCPOS.GS, 0x77, width,
            ESCPOS.GS, 0x48, text_position,
            ESCPOS.GS, 0x6B, barcode_type
        ])
        data_bytes = data.encode('ascii') + bytes([0])
        return cmd + data_bytes

    @staticmethod
    def print_qr(
        data: str,
        size: int = 6,
        error_correction: QRErrorCorrection = QRErrorCorrection.M
    ) -> bytes:
        """
        Print QR code.

        Args:
            data: QR code data
            size: QR code size (1-16)
            error_correction: Error correction level
        """
        data_bytes = data.encode('utf-8')
        length = len(data_bytes) + 3

        cmd = bytes([
            ESCPOS.GS, 0x28, 0x6B, 0x04, 0x00, 0x31, 0x41,
            error_correction, 0x00
        ])
        cmd += bytes([
            ESCPOS.GS, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x43, size
        ])
        cmd += bytes([
            ESCPOS.GS, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x45, 0x00
        ])
        cmd += bytes([
            ESCPOS.GS, 0x28, 0x6B, length & 0xFF, (length >> 8) & 0xFF,
            0x31, 0x50, 0x30
        ])
        cmd += data_bytes
        cmd += bytes([ESCPOS.GS, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x51, 0x00])

        return cmd

    @staticmethod
    def print_bit_image(
        image_data: bytes,
        width: int,
        height: int,
        mode: int = 0
    ) -> bytes:
        """
        Print bitmap image.

        Args:
            image_data: Image data (1-bit per pixel, row by row)
            width: Image width in pixels
            height: Image height in pixels
            mode: 0 = normal, 1 = double width, 2 = double height, 3 = double both
        """
        n = (width + 7) // 8
        cmd = bytes([
            ESCPOS.ESC, 0x2A, mode,
            n & 0xFF, (n >> 8) & 0xFF,
            height & 0xFF, (height >> 8) & 0xFF
        ])
        return cmd + image_data


class ReceiptFormatter:
    """Helper for formatting receipt data."""

    WIDTH_58MM = 32
    WIDTH_80MM = 48

    def __init__(self, width: int = WIDTH_58MM):
        self.width = width

    def center_text(self, text: str) -> str:
        """Center text."""
        padding = (self.width - len(text)) // 2
        return " " * padding + text

    def left_right_text(self, left: str, right: str) -> str:
        """Left and right text on same line."""
        if len(left) + len(right) > self.width:
            left = left[:self.width - len(right)]
        padding = self.width - len(left) - len(right)
        return left + " " * padding + right

    def double_dash_line(self) -> str:
        """Double dashed line."""
        return "=" * self.width

    def single_dash_line(self) -> str:
        """Single dashed line."""
        return "-" * self.width

    def format_currency(self, amount: float) -> str:
        """Format currency."""
        return f"${amount:.2f}"

    def format_item(self, name: str, price: float, qty: int = 1) -> str:
        """Format item line."""
        total = price * qty
        price_str = self.format_currency(total)
        name = name[:self.width - len(price_str) - 4]
        return f"{name} x{qty}{' ' * (self.width - len(name) - len(price_str) - 4)}{price_str}"


def create_receipt(
    store_name: str,
    items: List[dict],
    total: float,
    width: int = 32,
    footer: str = None,
    receipt_number: str = None,
    date: str = None
) -> bytes:
    """
    Create a formatted receipt.

    Args:
        store_name: Store name
        items: List of dicts with 'name', 'price', 'qty'
        total: Total amount
        width: Receipt width
        footer: Footer text
        receipt_number: Receipt number
        date: Date string

    Returns:
        ESC/POS commands to print receipt
    """
    fmt = ReceiptFormatter(width)
    cmds = ESCPOSCommands()

    data = cmds.initialize()
    data += cmds.set_default_line_spacing()
    data += cmds.set_alignment(Alignment.CENTER)

    data += cmds.set_text_size(2, 2)
    data += f"{store_name}\n".encode('utf-8')

    data += cmds.set_default_line_spacing()
    data += cmds.set_alignment(Alignment.LEFT)
    data += fmt.single_dash_line().encode('utf-8') + b'\n'

    if receipt_number:
        data += f"Receipt: {receipt_number}\n".encode('utf-8')
    if date:
        data += f"Date: {date}\n".encode('utf-8')

    data += fmt.single_dash_line().encode('utf-8') + b'\n'

    for item in items:
        line = fmt.format_item(item['name'], item['price'], item.get('qty', 1))
        data += line.encode('utf-8') + b'\n'

    data += fmt.single_dash_line().encode('utf-8') + b'\n'

    data += fmt.left_right_text("TOTAL", fmt.format_currency(total)).encode('utf-8')
    data += b'\n'

    data += cmds.line_feed(2)

    if footer:
        data += cmds.set_alignment(Alignment.CENTER)
        data += footer.encode('utf-8')
        data += b'\n'

    data += cmds.line_feed(3)
    data += cmds.cut_paper()

    return data


class YHKCommands:
    """YHK Cat thermal printer commands (similar to ESC/POS but requires start/end sequences)."""

    @staticmethod
    def initialize() -> bytes:
        """Initialize printer."""
        return bytes([0x1B, 0x40])

    @staticmethod
    def start_print() -> bytes:
        """Start print sequence (required before sending data)."""
        return bytes([0x1D, 0x49, 0xF0, 0x19])

    @staticmethod
    def end_print() -> bytes:
        """End print sequence (required after sending data)."""
        return bytes([0x0A, 0x0A, 0x0A, 0x0A])

    @staticmethod
    def line_feed(lines: int = 1) -> bytes:
        """Feed lines."""
        return bytes([0x0A] * lines)

    @staticmethod
    def cut_paper(full_cut: bool = True) -> bytes:
        """Cut paper - YHK uses end_print instead."""
        return YHKCommands.end_print()

    @staticmethod
    def partial_cut() -> bytes:
        """Partial cut paper."""
        return YHKCommands.end_print()

    @staticmethod
    def get_status() -> bytes:
        """Get printer status."""
        return bytes([0x1E, 0x47, 0x03])

    @staticmethod
    def get_serial() -> bytes:
        """Get printer serial number."""
        return bytes([0x1D, 0x67, 0x39])

    @staticmethod
    def get_product_info() -> bytes:
        """Get printer product info."""
        return bytes([0x1D, 0x67, 0x69])

    @staticmethod
    def set_alignment(align: Alignment) -> bytes:
        """Set text alignment."""
        return bytes([0x1B, 0x61, align])

    @staticmethod
    def set_text_size(width: int, height: int) -> bytes:
        """Set text size (width and height 1-8)."""
        size = ((height - 1) << 4) | (width - 1)
        return bytes([0x1D, 0x21, size])

    @staticmethod
    def set_text_color_normal() -> bytes:
        """Set normal text color."""
        return bytes([0x1B, 0x72, 0x00])

    @staticmethod
    def set_text_color_red() -> bytes:
        """Set red text color (if supported)."""
        return bytes([0x1B, 0x72, 0x01])

    @staticmethod
    def set_line_spacing(lines: int = 30) -> bytes:
        """Set line spacing in dots."""
        return bytes([0x1B, 0x33, lines])

    @staticmethod
    def set_default_line_spacing() -> bytes:
        """Set default line spacing."""
        return bytes([0x1B, 0x32])

    @staticmethod
    def set_left_margin(dots: int) -> bytes:
        """Set left margin in dots."""
        return bytes([0x1B, 0x6C, dots])

    @staticmethod
    def set_print_width(dots: int) -> bytes:
        """Set print width in dots."""
        return bytes([0x1D, 0x57, dots & 0xFF, (dots >> 8) & 0xFF])

    @staticmethod
    def bold_on() -> bytes:
        """Turn bold on."""
        return bytes([0x1B, 0x45, 0x01])

    @staticmethod
    def bold_off() -> bytes:
        """Turn bold off."""
        return bytes([0x1B, 0x45, 0x00])

    @staticmethod
    def underline_on() -> bytes:
        """Turn underline on."""
        return bytes([0x1B, 0x2D, 0x01])

    @staticmethod
    def underline_off() -> bytes:
        """Turn underline off."""
        return bytes([0x1B, 0x2D, 0x00])

    @staticmethod
    def beep() -> bytes:
        """Make beep sound."""
        return bytes([0x1B, 0x42, 0x05, 0x09])

    @staticmethod
    def open_cash_drawer() -> bytes:
        """Open cash drawer."""
        return bytes([0x1B, 0x70, 0x00, 0x19, 0xFA])


def is_yhk_printer(name: str) -> bool:
    """Check if printer is a YHK Cat type."""
    if not name:
        return False
    name_lower = name.lower()
    return "yhk" in name_lower or "cat" in name_lower or "rabbit" in name_lower
