# Convert a X68000 15 bits palette file into another palette file with a new color range.
# By Franck "hitchhikr" Charlet.

from pathlib import Path
import sys
import os
import numpy

def convert_palette(new_name, pal_name, cols, range, off_pal):
    with open(pal_name, "rb") as f:
        pal = bytearray()
        f.seek(off_pal, 0)
        print("Reading palette file...")
        pal += f.read(cols * 2)
    print("Converting palette...")
    color = bytearray(4)
    shift = bin(range)
    shift = shift.count('1')
    with open(new_name, "wb") as f:
        i = 0
        if (shift < 4): shift = 4
        while(cols != 0):
            curr_col = ((pal[(i * 2)] << 8) + pal[(i * 2) + 1])
            blue = int(float((curr_col & 0x3e) >> 1) * float(range) / 31.0)
            red = int(float((curr_col & 0x7c0) >> 6) * float(range) / 31.0)
            green = int(float((curr_col & 0xf800) >> 11) * float(range) / 31.0)
            curr_col = ((red & range) << (shift * 2)) | ((green & range) << shift) | (blue & range)
            all_shift = int((shift * 4) / 8)
            color[0] = 0
            if(all_shift > 0):
                while(all_shift > 0):
                    color[int(all_shift) - 1] = curr_col & 0xff
                    curr_col = curr_col >> 8
                    all_shift = all_shift - 1
                j = 0
                while(j < int((shift * 4) / 8)):
                    f.write(color[j].to_bytes(1, "little"))
                    j = j + 1
            cols = cols - 1
            i = i + 1
    print("Done.")
    return

def main():
    print('x68k_convert_palette by Franck "hitchhikr" Charlet.')
    if len(sys.argv) < 5:
        print("Usage: x68k_convert_palette <New palette file> <X68000 palette file> <number of colors> <new range> [offset in X68000 pal file]")
        return
    if len(sys.argv) < 6:
        offset_pal = 0
    else:
        offset_pal = int(sys.argv[5])
    if(int(sys.argv[2]) > 255):
        print("Range to high (max. 255)")
        return
    convert_palette(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), offset_pal)

if __name__ == "__main__":
    main()

