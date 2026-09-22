#!/usr/bin/env python3
"""
Repack Header v4 boot.img with a new kernel Image / Image.gz
Preserves exact ramdisk, cmdline, header fields, and pads to original size.
"""

import sys
import os
import gzip
import math
import struct

PAGE_SIZE = 4096

def repack(original_boot, new_kernel, output_boot):
    if not os.path.exists(original_boot):
        print(f"Error: Original boot {original_boot} not found.")
        sys.exit(1)
    if not os.path.exists(new_kernel):
        print(f"Error: New kernel {new_kernel} not found.")
        sys.exit(1)

    with open(original_boot, 'rb') as f:
        orig_data = f.read()

    # Verify magic
    magic = orig_data[0:8]
    if not magic.startswith(b'ANDROID!'):
        print("Error: Invalid ANDROID! magic.")
        sys.exit(1)

    orig_kernel_size, orig_ramdisk_size, os_version, header_size = struct.unpack('<IIII', orig_data[8:24])
    header_version = struct.unpack('<I', orig_data[40:44])[0]
    cmdline = orig_data[44:44+1536]

    print(f"[+] Original Header Version: {header_version}")
    print(f"[+] Original Kernel Size: {orig_kernel_size} bytes")
    print(f"[+] Original Ramdisk Size: {orig_ramdisk_size} bytes")

    # Read new kernel data
    with open(new_kernel, 'rb') as kf:
        k_data = kf.read()

    # Check if new kernel needs GZIP compression
    if not k_data.startswith(b'\x1f\x8b'):
        print("[+] Compressing new kernel Image with GZIP...")
        k_data = gzip.compress(k_data, compresslevel=9)

    new_kernel_size = len(k_data)
    print(f"[+] New GZIP Kernel Size: {new_kernel_size} bytes")

    # Extract original ramdisk from original boot
    orig_kernel_pages = math.ceil(orig_kernel_size / PAGE_SIZE)
    ramdisk_offset = PAGE_SIZE * (1 + orig_kernel_pages)
    ramdisk_data = orig_data[ramdisk_offset:ramdisk_offset + orig_ramdisk_size]
    print(f"[+] Extracted original ramdisk ({len(ramdisk_data)} bytes)")

    orig_sig_offset = ramdisk_offset + math.ceil(orig_ramdisk_size / PAGE_SIZE) * PAGE_SIZE
    sig_and_avb = orig_data[orig_sig_offset:]
    signature_size = struct.unpack('<I', orig_data[1580:1584])[0] if len(orig_data) >= 1584 else 0
    print(f"[+] Extracted original signature & AVB0 ({len(sig_and_avb)} bytes, sig_size: {signature_size})")

    # Construct new header (v4)
    # Header size is 1584 bytes, padded to 4096
    hdr_buf = bytearray(PAGE_SIZE)
    hdr_buf[0:8] = b'ANDROID!'
    struct.pack_into('<IIII', hdr_buf, 8, new_kernel_size, orig_ramdisk_size, os_version, header_size)
    struct.pack_into('<I', hdr_buf, 40, header_version)
    hdr_buf[44:44+1536] = cmdline
    if signature_size > 0:
        struct.pack_into('<I', hdr_buf, 1580, signature_size)

    # Pad kernel to PAGE_SIZE
    new_kernel_padded = bytearray(k_data)
    rem_k = len(new_kernel_padded) % PAGE_SIZE
    if rem_k > 0:
        new_kernel_padded.extend(b'\x00' * (PAGE_SIZE - rem_k))

    # Pad ramdisk to PAGE_SIZE
    ramdisk_padded = bytearray(ramdisk_data)
    rem_r = len(ramdisk_padded) % PAGE_SIZE
    if rem_r > 0:
        ramdisk_padded.extend(b'\x00' * (PAGE_SIZE - rem_r))

    # Combine: Header + Kernel + Ramdisk + Signature/AVB0
    repacked = bytearray()
    repacked.extend(hdr_buf)
    repacked.extend(new_kernel_padded)
    repacked.extend(ramdisk_padded)
    repacked.extend(sig_and_avb)

    # Pad to total original boot image size if needed
    orig_total_size = len(orig_data)
    if len(repacked) < orig_total_size:
        repacked.extend(b'\x00' * (orig_total_size - len(repacked)))
    elif len(repacked) > orig_total_size:
        # Trim excess padding while preserving AVB0
        repacked = repacked[:orig_total_size]

    with open(output_boot, 'wb') as out_f:
        out_f.write(repacked)

    print(f"[+] Successfully repacked with AVB0 & Signature: {output_boot} ({len(repacked)} bytes)")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: repack_boot.py <original_boot.img> <new_kernel_Image> <output_boot.img>")
        sys.exit(1)
    repack(sys.argv[1], sys.argv[2], sys.argv[3])
