# Convert X68000 16 bits (65536 colors) true colors pictures files into png pictures.
# By Franck "hitchhikr" Charlet.

from pathlib import Path
import sys
import os
import png
import numpy

def convert_picture(png_name, pic_name, width, height, off_pic):
    pict = bytearray(int(width) * int(height) * 2)
    pict = numpy.array(pict).reshape(int(height), int(width) * 2)
    with open(pic_name, "rb") as f:
        pict = bytearray()
        f.seek(off_pic, 0)
        print("Reading picture file...")
        pict = f.read(int(width) * int(height) * 2)
    final_pict = bytearray(int(width) * int(height) * 4)
    final_pict = numpy.array(final_pict).reshape(int(height), int(width) * 4)
    print("Converting picture to RGBA...")
    pos_in_pic = 0
    for j in range(int(height)):
        for i in range(int(width)):
            color = (pict[(j * int(int(width) * 2)) + (i * 2) + 1])
            color |= (pict[(j * int(int(width) * 2)) + (i * 2)] << 8)
            intensity = ((pict[(j * int(int(width) * 2)) + (i * 2) + 1]) & 1) << 1
            if intensity == 0:
                intensity = 0.9
            else:
                intensity = 0.95
            blue = (float((color & 0x3e) >> 1) * 255.0 / 31.0) * intensity
            red = (float((color & 0x7c0) >> 6) * 255.0 / 31.0) * intensity
            green = (float((color & 0xf800) >> 11) * 255.0 / 31.0) * intensity
            final_pict[j][(i * 4)] = int(red)
            final_pict[j][(i * 4) + 1] = int(green)
            final_pict[j][(i * 4) + 2] = int(blue)
            final_pict[j][(i * 4) + 3] = 0xff;
            if (i & 1):
                pos_in_pic += 2
    print("Saving PNG picture...")
    png.from_array(final_pict, 'RGBA').save(png_name)
    print("Done.")
    return

def main():
    print('x68k_16bits_true_colors_to_png by Franck "hitchhikr" Charlet.')
    if len(sys.argv) < 5:
        print("Usage: x68k_16bits_true_colors_to_png <png picture file> <picture file> <width> <height> [offset in pic file]")
        return
    if len(sys.argv) < 6:
        offset_pic = 0
    else:
        offset_pic = int(sys.argv[5])
    convert_picture(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], offset_pic)

if __name__ == "__main__":
    main()
