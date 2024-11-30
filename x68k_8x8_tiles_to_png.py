# Convert X68000 8x8 tiles pictures files into png pictures.
# By Franck "hitchhikr" Charlet.

from pathlib import Path
import sys
import os
import png
import numpy

def convert_tiles(png_name, pic_name, pal_name, sprites, off_pic, off_pal):
    with open(pic_name, "rb") as f:
        pict = bytearray()
        f.seek(off_pic, 0)
        print("Reading picture file...")
        pict = f.read(int(sprites) * 32)
    with open(pal_name, "rb") as f:
        pal = bytearray()
        f.seek(off_pal, 0)
        print("Reading palette file...")
        pal += f.read(512)
    red = bytearray(256)
    green = bytearray(256)
    blue = bytearray(256)
    print("Converting palette...")
    for i in range(256):
        color = ((pal[(i * 2)] << 8) + pal[(i * 2) + 1])
        blue[i] = int(float((color & 0x3e) >> 1) * 255.0 / 31.0)
        red[i] = int(float((color & 0x7c0) >> 6) * 255.0 / 31.0)
        green[i] = int(float((color & 0xf800) >> 11) * 255.0 / 31.0)
    final_pict = bytearray(int(sprites) * 8 * (8 * 16 * 4))
    final_pict = numpy.array(final_pict).reshape(8 * int(sprites),  (8 * 16 * 4))
    print("Converting tiles to RGBA...")
    for palette in range(16):
        off = 0
        for j in range(int(sprites)):
            for k in range(8):
                for i in range(2):
                    pixels = ((pict[(k * 4) + (i * 2) + off] << 8) + pict[(k * 4) + (i * 2) + 1 + off])
                    pixel1 = (pixels & 0xf000) >> 12
                    pixel2 = (pixels & 0x0f00) >> 8
                    pixel3 = (pixels & 0x00f0) >> 4
                    pixel4 = (pixels & 0x000f)
                    final_pict[k + (j * 8)][(i * 16) + (palette * 32)] = red[pixel1 + (palette * 16)]
                    final_pict[k + (j * 8)][(i * 16) + 1 + (palette * 32)] = green[pixel1 + (palette * 16)]
                    final_pict[k + (j * 8)][(i * 16) + 2 + (palette * 32)] = blue[pixel1 + (palette * 16)]
                    final_pict[k + (j * 8)][(i * 16) + 3 + (palette * 32)] = 0xff;
                    final_pict[k + (j * 8)][(i * 16) + 4 + (palette * 32)] = red[pixel2 + (palette * 16)]
                    final_pict[k + (j * 8)][(i * 16) + 5 + (palette * 32)] = green[pixel2 + (palette * 16)]
                    final_pict[k + (j * 8)][(i * 16) + 6 + (palette * 32)] = blue[pixel2 + (palette * 16)]
                    final_pict[k + (j * 8)][(i * 16) + 7 + (palette * 32)] = 0xff;
                    final_pict[k + (j * 8)][(i * 16) + 8 + (palette * 32)] = red[pixel3 + (palette * 16)]
                    final_pict[k + (j * 8)][(i * 16) + 9 + (palette * 32)] = green[pixel3 + (palette * 16)]
                    final_pict[k + (j * 8)][(i * 16) + 10 + (palette * 32)] = blue[pixel3 + (palette * 16)]
                    final_pict[k + (j * 8)][(i * 16) + 11 + (palette * 32)] = 0xff;
                    final_pict[k + (j * 8)][(i * 16) + 12 + (palette * 32)] = red[pixel4 + (palette * 16)]
                    final_pict[k + (j * 8)][(i * 16) + 13 + (palette * 32)] = green[pixel4 + (palette * 16)]
                    final_pict[k + (j * 8)][(i * 16) + 14 + (palette * 32)] = blue[pixel4 + (palette * 16)]
                    final_pict[k + (j * 8)][(i * 16) + 15 + (palette * 32)] = 0xff;
            off += 0x20
    print("Saving PNG picture...")
    png.from_array(final_pict, 'RGBA').save(png_name)
    print("Done.")
    return

def main():
    print('x68k_8x8_tiles_to_png by Franck "hitchhikr" Charlet.')
    if len(sys.argv) < 5:
        print("Usage: x68k_8x8_tiles_to_png <png picture file> <tiles file> <palette file> <number of tiles> [offset in pic file] [offset in pal file]")
        return
    if len(sys.argv) < 6:
        offset_pic = 0
    else:
        offset_pic = int(sys.argv[5])
    if len(sys.argv) < 7:
        offset_pal = 0
    else:
        offset_pal = int(sys.argv[6])
    convert_tiles(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], offset_pic, offset_pal)

if __name__ == "__main__":
    main()
