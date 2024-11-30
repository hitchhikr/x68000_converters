# Convert X68000 4 bits (16 colors) paletted planar pictures files into png pictures.
# By Franck "hitchhikr" Charlet.

from pathlib import Path
import sys
import os
import png
import numpy

def convert_picture(png_name, pic_name, pal_name, width, height, depth, repeat, off_pic, off_pal):

    with open(pic_name, "rb") as f:
        pict = bytearray()
        f.seek(off_pic, 0)
        print("Reading picture file...")
        pict = f.read(int(width / 8) * height * depth * repeat)
    with open(pal_name, "rb") as f:
        pal = bytearray()
        f.seek(off_pal, 0)
        print("Reading palette file...")
        pal += f.read((1 << depth) * 2)
    red = bytearray((1 << depth))
    green = bytearray((1 << depth))
    blue = bytearray((1 << depth))
    print("Converting palette...")
    for i in range((1 << depth)):
        color = ((pal[(i * 2)] << 8) + pal[(i * 2) + 1])
        blue[i] = int(float((color & 0x3e) >> 1) * 255.0 / 31.0)
        red[i] = int(float((color & 0x7c0) >> 6) * 255.0 / 31.0)
        green[i] = int(float((color & 0xf800) >> 11) * 255.0 / 31.0)
    final_pict = bytearray(width * height * 4 * repeat)
    final_pict = numpy.array(final_pict).reshape(height * repeat, width * 4)
    print("Converting picture to RGBA...")
    for r in range(repeat):
        for y in range(height):
            for x in range(int(width / 8)):
                for bit in range(8):
                    index = 0
                    for i in range(depth):
                        index |= ((pict[(y * int(width / 8)) + (i * int(width / 8) * height) + x + (r * int(width / 8) * height * depth)] & (0x80 >> bit)) >> (7 - bit)) << i
                    final_pict[y + (r * height)][(bit * 4) + (x * 8 * 4)] = red[index]
                    final_pict[y + (r * height)][(bit * 4) + (x * 8 * 4) + 1] = green[index]
                    final_pict[y + (r * height)][(bit * 4) + (x * 8 * 4) + 2] = blue[index]
                    final_pict[y + (r * height)][(bit * 4) + (x * 8 * 4) + 3] = 0xff
    print("Saving PNG picture...")
    png.from_array(final_pict, 'RGBA').save(png_name)
    print("Done.")
    return

def main():
    print('x68k_planar_to_png by Franck "hitchhikr" Charlet.')
    if len(sys.argv) < 7:
        print("Usage: x68k_planar_to_png <png picture file> <picture file> <palette file> <width> <height> <depth> [repeat] [offset in pic file] [offset in pal file]")
        return
    if len(sys.argv) < 8:
        repeat = 1
    else:
        repeat = int(sys.argv[7])
    if len(sys.argv) < 9:
        offset_pic = 0
    else:
        offset_pic = int(sys.argv[8])
    if len(sys.argv) < 10:
        offset_pal = 0
    else:
        offset_pal = int(sys.argv[9])
    convert_picture(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), repeat, offset_pic, offset_pal)

if __name__ == "__main__":
    main()
