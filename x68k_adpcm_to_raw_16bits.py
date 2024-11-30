# Convert X68000 adpcm samples files into raw 16 bits (signed, little endian) files.
# By Franck "hitchhikr" Charlet.

from pathlib import Path
import sys
import os

step_adjust_table = [ -1, -1, -1, -1, 2, 4, 6, 8, -1, -1, -1, -1, 2, 4, 6, 8 ]

step_size_table = [  16,  17,  19,  21,  23,  25,  28,  31,  34,  37,  41,  45,   50,   55,   60,   66,
                     73,  80,  88,  97, 107, 118, 130, 143, 157, 173, 190, 209,  230,  253,  279,  307,
                    337, 371, 408, 449, 494, 544, 598, 658, 724, 796, 876, 963, 1060, 1166, 1282, 1411, 1552 ]

history = 0
step_hist = 0
raw_samples = 0
scale = 0

def oki_step(step):
    global history
    global step_hist
    step_size = step_size_table[step_hist]
    delta = step_size >> 3
    if(step & 1):
        delta += step_size >> 2
    if(step & 2):
        delta += step_size >> 1
    if(step & 4):
        delta += step_size
    if(step & 8):
        delta = -delta
    out = history + delta
    history = out = max(-2048, min(out, 2047))
    adjusted_step = step_hist + step_adjust_table[step & 7]
    step_hist = max(0, min(adjusted_step, 48))
    return out

def decode(buffer, outbuffer, len):
    global history
    global step_hist
    global raw_samples
    global scale
    nibble = 4
    pos_buffer = 0
    history = 0
    step_hist = 0

    for i in range(len):
        step = buffer[pos_buffer] << nibble
        step >>= 4
        if(nibble == 0):
            pos_buffer += 1
        nibble ^= 4
        data = int((oki_step(step) << 4))
        abs_data = abs(data)
        if(abs_data > scale):
            scale = abs_data
        raw_samples[i * 2] = (data & 0xff)
        raw_samples[(i * 2) + 1] = (data & 0xff00) >> 8
    return

def convert_adpcm(raw_name, adpcm_name, size, off_adpcm):
    with open(adpcm_name, "rb") as f:
        adpcm_samples = bytearray()
        f.seek(off_adpcm, 0)
        print("Reading adpcm file...")
        adpcm_samples = f.read(int(size))
    global raw_samples
    global scale
    raw_samples = bytearray(int(size) * 4)
    print("Converting samples...")
    decode(adpcm_samples, raw_samples, int(size) * 2)
    with open(raw_name, "wb") as f:
        print("Writing raw data...")
        scale = (scale / 32767.0)
        for i in range(int(size) * 2):
            data = (int(raw_samples[i * 2] | (raw_samples[(i * 2) + 1] << 8)))
            if(data & 0x8000): data = (data & 0x7fff) - 32767
            data = ((data / 32767.0) / scale) * 32767.0
            data = max(-32767, min(data, 32768))
            data = int(data) & 0xffff
            raw_samples[i * 2] = (data & 0xff)
            raw_samples[(i * 2) + 1] = (data & 0xff00) >> 8
            f.write(raw_samples[(i * 2)].to_bytes(1, "little"))
            f.write(raw_samples[(i * 2) + 1].to_bytes(1, "little"))
    print("Done.")
    return

def main():
    print('x68k_adpcm_to_raw_16bits by Franck "hitchhikr" Charlet.')
    if len(sys.argv) < 3:
        print("Usage: x68k_adpcm_to_raw_16bits <raw16 file> <adpcm file> [adpcm size] [offset in adpcm file]")
        return
    if len(sys.argv) < 5:
        offset_adpcm = 0
    else:
        offset_adpcm = int(sys.argv[4])
    if len(sys.argv) < 4:
        size_adpcm = os.path.getsize(sys.argv[2])
    else:
        size_adpcm = int(sys.argv[3])
    convert_adpcm(sys.argv[1], sys.argv[2], size_adpcm, offset_adpcm)

if __name__ == "__main__":
    main()
