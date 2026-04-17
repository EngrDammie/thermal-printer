# Thermal Printer CLI

Print receipts, EPINs, and more to your YHK Bluetooth thermal printer.

---

## What Can This App Print?

- **Receipts** - Shop receipts with items, prices, and totals
- **EPINs** - Mobile airtime vouchers (MTN, AIRTEL, GLO, 9MOBILE)
- **Plain text** - Any text you want to print
- **Images** - Photos and graphics
- **QR codes** - Scannable QR codes
- **Barcones** - Product barcodes

---

# STEP-BY-STEP: How to Connect Your Printer

Follow these steps exactly. Do them in order.

## Step 1: Turn On Your Printer

Make sure your thermal printer is:
- Turned ON
- Has paper loaded
- The LED light is green (not blinking red)

## Step 2: Find Your Printer's MAC Address

Every Bluetooth printer has a unique MAC address (like a phone number). You need to know yours.

### If you don't know the MAC address:

Don't worry! Your computer can find it for you. Here's how:

#### Option A: Ask the seller
Ask the person who sold you the printer, OR check the printer box/label.

#### Option B: Let your computer find it (Recommended!)

Your computer can scan for nearby printers. Here's what to do:

**Step 1:** Turn on your printer and make sure it's close to your computer.

**Step 2:** Run this command to start searching:
```bash
bluetoothctl scan on
```

**Step 3:** Wait about 10 seconds. You will see a list of devices appear. Look for one that says "YHK" - that's your printer!

**Step 4:** Copy the MAC address (it looks like `24:00:44:00:46:20`). That's your printer's unique number.

**Step 5:** Pair your computer with the printer:
```bash
bluetoothctl pair THE_MAC_ADDRESS_YOU_FOUND
```
Replace `THE_MAC_ADDRESS_YOU_FOUND` with the number you copied (like `24:00:44:00:46:20`).

**Step 6:** Now connect to the printer using the bind command (see Step 3 below).

Typical YHK printers use one of these:
- `98:B2:6A:F7:AD:50`
- `24:00:43:00:00:77`
- `24:00:44:00:09:8F` (older model)
- `24:00:44:00:46:20` (newer model)

### To verify the printer is on and ready:

Run this command:
```bash
rfcomm
```

If you see something like `/dev/rfcomm0: 24:00:44:00:09:8F channel 1 connected`, your printer is already connected!

## Step 3: Connect (Bind) the Printer

**This is the most important step!**

Run this command IN YOUR TERMINAL (not here):
```bash
sudo rfcomm bind /dev/rfcomm0 YOUR_MAC_ADDRESS_HERE 2
```

Replace `YOUR_MAC_ADDRESS_HERE` with your printer's MAC address.

Example:
```bash
sudo rfcomm bind /dev/rfcomm0 24:00:44:00:09:8F 2
```

It will ask for your computer password. Type it and press Enter.

**You need to do this every time you restart your computer or turn off the printer!**

---

# STEP-BY-STEP: How to Print

After connecting your printer (Step 3 above), you're ready to print!

## Printing a Receipt

This is the most common task - printing a receipt for a customer.

### Command:
```bash
python3 print.py --receipt "YOUR COMPANY NAME" "ITEM NAME" PRICE QUANTITY
```

### Examples:

**Example 1: One item**
```bash
python3 print.py --receipt "DAMMIE OPTIMUS SOLUTIONS" "Bluetooth Printer" 37000 1
```
This prints a receipt for 1 Bluetooth Printer costing ₦37,000.

**Example 2: Multiple items**
```bash
python3 print.py --receipt "My Shop" "Coffee" 350 2 "Cake" 500 1
```
This prints:
- 2 Coffee at ₦350 each
- 1 Cake at ₦500 each
- Total: ₦1,200

The app automatically calculates the total!

---

## Printing EPINs (Airtime Vouchers)

### Step 1: Create an EPIN text file

Create a new file called `epins.txt` (or any name).

Add each EPIN on a new line in this format:
```
EPIN_NUMBER NETWORK AMOUNT
```

### Example epins.txt:
```
1234567890123456 AIRTEL 500
2345678901234567 MTN 1000
3456789012345678 GLO 200
4567890123456789 9MOBILE 500
```

**Supported networks:** MTN, AIRTEL, GLO, 9MOBILE
**Supported amounts:** 100, 200, 500, 1000, 2000, 5000

### Step 2: Print the EPINs

```bash
python3 print.py --epin epins.txt
```

**To add your company name:**
```bash
python3 print.py --epin epins.txt -c "DAMMIE OPTIMUS SOLUTIONS"
```

**To change separator dashes (default 16):**
```bash
python3 print.py --epin epins.txt -d 20
```

---

## Printing Plain Text

```bash
python3 print.py "Hello World"
```

The text will automatically wrap to fit the paper.

---

## Printing Images

```bash
python3 print.py --image /path/to/your/image.jpg
```

Replace `/path/to/your/image.jpg` with the actual file path.

---

# Common Problems and Solutions

## Problem: "Host is down" Error

**Error:**
```
OSError: [Errno 112] Host is down
```

**Cause:** The printer is not connected.

**Solution:**
1. Make sure printer is turned ON
2. Run the bind command again:
```bash
sudo rfcomm bind /dev/rfcomm0 YOUR_MAC_ADDRESS 2
```

---

## Problem: Nothing prints

**Check:**
1. Is the printer turned ON?
2. Is there paper in the printer?
3. Is the LED light green?

---

## Problem: "Device or resource busy"

**Cause:** The printer is already connected by another program.

**Solution:**
```bash
sudo rfcomm release /dev/rfcomm0
```
Then connect again:
```bash
sudo rfcomm bind /dev/rfcomm0 YOUR_MAC_ADDRESS 2
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Connect printer | `sudo rfcomm bind /dev/rfcomm0 MAC_ADDRESS 2` |
| Check connection | `rfcomm` |
| Print receipt | `python3 print.py --receipt "Company" "Item" Price Qty` |
| Print EPINs | `python3 print.py --epin epins.txt` |
| Print text | `python3 print.py "Hello"` |
| Print image | `python3 print.py --image file.jpg` |

---

# Need Help?

If you're still having trouble:
1. Make sure your printer is turned ON
2. Check that you have paper
3. Try turning the printer off and on again
4. Ask for help with the bind command

---

*Last updated: April 2026*