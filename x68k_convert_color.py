# Convert a X68000 15 bits color into a new color range.
# By Franck "hitchhikr" Charlet.

from pathlib import Path
import sys

def main():
    print('x68k_convert_color by Franck "hitchhikr" Charlet.')
    if len(sys.argv) < 3:
        print("Usage: x68k_convert_color <x68000 color in hexadecimal> <new range>")
        return
    if(int(sys.argv[2]) > 255):
        print("Range to high (max. 255)")
        return
    color = int(sys.argv[1], 16)
    blue = int(float((color & 0x3e) >> 1) * float(sys.argv[2]) / 31.0)
    red = int(float((color & 0x7c0) >> 6) * float(sys.argv[2]) / 31.0)
    green = int(float((color & 0xf800) >> 11) * float(sys.argv[2]) / 31.0)
    shift = bin(int(sys.argv[2]))
    shift = shift.count('1')
    old_shift = shift
    if (shift < 4): shift = 4
    color = ((red & int(sys.argv[2])) << (shift * 2)) | ((green & int(sys.argv[2])) << shift) | (blue & int(sys.argv[2]))
    print("Corresponding color in", old_shift, "bits:", hex(color))

if __name__ == "__main__":
    main()
