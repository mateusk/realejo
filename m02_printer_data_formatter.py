# Based on https://github.com/vivier/phomemo-tools

# This script is used to convert an image to a format that can be printed
# by the Phomemo M02 printer.

#! /usr/bin/python3

"""
Modules:
    getopt
    sys
    os
    PIL.Image
"""

import getopt
import os
import sys

from PIL import Image

def print_header():
    """Print the header of the image."""
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        stdout.write(b'\x1b\x40\x1b\x61\x01\x1f\x11\x02\x04')

def print_marker(_lines=0x100):
    """Print the marker of the image."""
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        stdout.write(0x761d.to_bytes(2, 'little'))
        stdout.write(0x0030.to_bytes(2, 'little'))
        stdout.write(0x0030.to_bytes(2, 'little'))
        stdout.write((_lines - 1).to_bytes(2, 'little'))

def print_footer():
    """Print the footer of the image."""
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        stdout.write(b'\x1b\x64\x02')
        stdout.write(b'\x1b\x64\x02')
        stdout.write(b'\x1f\x11\x08')
        stdout.write(b'\x1f\x11\x0e')
        stdout.write(b'\x1f\x11\x07')
        stdout.write(b'\x1f\x11\x09')

def print_line(_image, _line):
    """Print a line of the image."""
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        for x in range(int(_image.width / 8)):
            byte = 0
            for bit in range(8):
                if _image.getpixel((x * 8 + bit, _line)) == 0:
                    byte |= 1 << (7 - bit)
            # 0x0a breaks the rendering
            # 0x0a alone is processed like LineFeed by the printer
            if byte == 0x0a:
                byte = 0x14
            stdout.write(byte.to_bytes(1, 'little'))

def usage():
    """Print the usage of the script."""
    print("%s [-h|--help] filename" % (sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
except getopt.error as err:
    print (str(err))
    usage()
    sys.exit(1)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        usage()
        sys.exit()

try:
    name = sys.argv[1]
except IndexError:
    print("Missing filename")
    usage()
    sys.exit(1)

try:
    image = Image.open(name)
except IOError as e:
    print("Error opening file:",(e))
    usage()
    sys.exit(2)

if image.width > image.height:
    image = image.rotate(90, expand=True)

# width 384 dots
image = image.resize(size=(384, int(image.height * 384 / image.width)))

# black&white printer: dithering
image = image.convert(mode='1')

remaining = image.height
line = 0
print_header()
while remaining > 0:
    lines = remaining
    lines = min(lines, 256)
    print_marker(lines)
    remaining -= lines
    while lines > 0:
        print_line(image, line)
        lines -= 1
        line += 1
print_footer()
