# Convert X68000 4 bits (16 colors) paletted chunky pictures files into png pictures.
# By Franck "hitchhikr" Charlet.

from pathlib import Path
import sys
import os
import png
import numpy

def convert_picture(png_name, pic_name, pal_name, width, height, off_pic, off_pal):
    with open(pic_name, "rb") as f:
        pict = bytearray()
        f.seek(off_pic, 0)
        print("Reading picture file...")
        pict = f.read(int(width) * int(height))
    with open(pal_name, "rb") as f:
        pal = bytearray()
        f.seek(off_pal, 0)
        print("Reading palette file...")
        pal += f.read(32)
    red = bytearray(16)
    green = bytearray(16)
    blue = bytearray(16)
    print("Converting palette...")
    for i in range(16):
        color = ((pal[(i * 2)] << 8) + pal[(i * 2) + 1])
        blue[i] = int(float((color & 0x3e) >> 1) * 255.0 / 31.0)
        red[i] = int(float((color & 0x7c0) >> 6) * 255.0 / 31.0)
        green[i] = int(float((color & 0xf800) >> 11) * 255.0 / 31.0)
    final_pict = bytearray(int(width) * int(height) * 4)
    final_pict = numpy.array(final_pict).reshape(int(height), int(width) * 4)
    print("Converting picture to RGBA...")
    for j in range(int(height)):
        for i in range(int(int(width) / 2)):
            byte = (pict[(j * int(int(width) / 2)) + i] >> 4) & 0xf
            final_pict[j][(i * 8)] = red[byte]
            final_pict[j][(i * 8) + 1] = green[byte]
            final_pict[j][(i * 8) + 2] = blue[byte]
            final_pict[j][(i * 8) + 3] = 0xff;
            byte = pict[(j * int(int(width) / 2)) + i] & 0xf
            final_pict[j][(i * 8) + 4] = red[byte]
            final_pict[j][(i * 8) + 5] = green[byte]
            final_pict[j][(i * 8) + 6] = blue[byte]
            final_pict[j][(i * 8) + 7] = 0xff;
    print("Saving PNG picture...")
    png.from_array(final_pict, 'RGBA').save(png_name)
    print("Done.")
    return

def main():
    print('x68k_4bits_chunky_to_png by Franck "hitchhikr" Charlet.')
    if len(sys.argv) < 6:
        print("Usage: x68k_4bits_chunky_to_png <png picture file> <picture file> <palette file> <width> <height> [offset in pic file] [offset in pal file]")
        return
    if len(sys.argv) < 7:
        offset_pic = 0
    else:
        offset_pic = int(sys.argv[6])
    if len(sys.argv) < 8:
        offset_pal = 0
    else:
        offset_pal = int(sys.argv[7])
    convert_picture(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], offset_pic, offset_pal)

if __name__ == "__main__":
    main()
