# Thermal Printer Setup - Full Chat History

## Overview
This document contains the complete setup process for connecting a Linux PC to a YHK thermal printer (model: YHK-TNN00000).

---

## Printer Information
- **Model:** YHK-TNN00000
- **MAC Address:** 98:B2:6A:F7:AD:50
- **RFCOMM Channel:** 2 (IMPORTANT - not the default channel 1)
- **Width:** 384 pixels (58mm paper)

---

## Key Discovery
This YHK "cat/rabbit" style printer uses a **special protocol** - it requires text to be converted to images first (unlike standard ESC/POS printers). The normal ESC/POS text commands don't work.

**Important commands discovered:**
- Initialize: `\x1b\x40` (ESC @)
- Start print sequence: `\x1d\x49\xf0\x19`
- End print sequence: `\x0a\x0a\x0a\x0a`

---

## Connection Steps

### Every Time You Want to Print:

1. **First, bind the RFCOMM channel:**
```bash
sudo rfcomm bind /dev/rfcomm0 98:B2:6A:F7:AD:50 2
```

2. **Then run print commands:**
```bash
python3 print.py "Your text"
```

---

## Print.py Features

### 1. Print Simple Text
```bash
python3 print.py "Hello World"
```
- Auto-wraps long text to new lines

### 2. Print Receipt
```bash
python3 print.py --receipt "Store Name" Item1 price qty Item2 price qty
```
Example:
```bash
python3 print.py --receipt "My Coffee Shop" Coffee 350 2 Cake 500 1
```
- Uses ₦ (Naira) currency
- Auto-calculates total
- Formats nicely with borders

### 3. Print Image
```bash
python3 print.py --image /path/to/image.jpg
```
- Auto-converts to black and white
- Auto-resizes to fit printer width

### 4. Print EPINs (Recharge Cards)
```bash
python3 print.py --epin epins.txt
python3 print.py --epin epins.txt -c "Company Name"
python3 print.py --epin epins.txt -c "Company Name" -d 20
```

**Input file format:**
```
EPIN NETWORK amount
Example:
5673829777748902 AIRTEL 500
73964135796488741 MTN 100
```

**Features:**
- Auto-detects network (AIRTEL, MTN, GLO, 9MOBILE)
- Auto-detects amount (100, 200, 500, etc.)
- Formats EPIN with dashes (4-4-4-4)
- Groups same network/amount together
- Adds *311*PIN# to each EPIN
- Prints in batches (5 per batch) to avoid cutting off

---

## Complete print.py Code

The main script is `print.py` in this folder. It includes:
- Text printing with wrapping
- Receipt printing
- Image printing
- EPIN printing with formatting

---

## Troubleshooting

### Printer not responding?
1. Make sure printer is turned ON
2. Run the connection command again:
   ```bash
   sudo rfcomm bind /dev/rfcomm0 98:B2:6A:F7:AD:50 2
   ```

### "Device already in use" error?
The printer is already connected. Just try printing.

### Nothing prints?
- Check that paper is loaded correctly
- Make sure the printer LED is green (not blinking red)

### EPINs getting cut off?
The batching is set to 5 per batch. This is intentional to avoid the printer cutting off the content.

---

## Files in This Folder

- `print.py` - Main print script
- `README.md` - Quick reference guide
- `epin_formatter_process.md` - Original requirements for EPIN formatting

---

## Session Notes

### What didn't work:
- Standard ESC/POS text commands (this printer needs image conversion)
- Direct RFCOMM without binding
- Large batches (caused cut-off)
- Font sizes too large

### What worked:
- YHK-specific protocol with start/end print sequences
- Converting text to bitmap images
- Smaller batches (5 EPINs per batch)
- Font size 18 for EPINs
- Adding Serial Port service: `sudo sdptool add --channel=2 SP`

---

*Last updated: Session complete*
