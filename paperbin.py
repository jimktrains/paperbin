#!/usr/bin/env python3

import sys
import base64
import ctypes
import argparse

passcnt = 0
block = None
lastblock = None;
barcodes = []


parser = argparse.ArgumentParser(description='Creates data and XOR-parity blocks suitable for human or barcode entry')
parser.add_argument('--type', dest='type', action='store', default="CODE39", help='Type of Barcode. Values maybe CODE39 or QRCODE')

args = parser.parse_args()
print(args)

if args.type not in ('CODE39', 'QRCODE'):
    parser.print_help()
    sys.exit(1)

BLOCKSIZE = None

if args.type == 'CODE39':
    BLOCKSIZE = 8
elif args.type == 'QRCODE':
    BLOCKSIZE = 128

DATA = '-'
XOR  = '%'
DUP  = '+'

# The barcode is of the form
# <base32(block number)><type><base32(block)>
def make_barcode(num, typesym, block):
    num = base64.b32encode(bytes(ctypes.c_uint16(num)))
    newblock = num.decode('ascii').replace('=','')
    newblock += typesym
    newblock += base64.b32encode(block).decode('ascii').replace('=','')
    return newblock

def sxor(s1,s2):    
    if len(s1) != len(s2):
        raise Exception("Lengths must be equal to xor")
    return bytes(a ^ b for a,b in zip(s1,s2))

with open('/dev/stdin', 'rb') as bindat:
    # Minus 1 so the padding will fit
    block = bindat.read(BLOCKSIZE-1)
    while len(block) != 0:
        padding = BLOCKSIZE - len(block)
        block = block + bytes([padding for i in range(padding)])
        passcnt += 1
        barcodes.append(make_barcode(passcnt, DATA, block))
        if passcnt % 2 == 0:
            block = sxor(block, lastblock)
            barcodes.append(make_barcode(passcnt, XOR, block))
        else:
            lastblock = block
        block = bindat.read(BLOCKSIZE-1)

# Simply duplicating the last block may not be an option
# if more than 3 groups are used.
if passcnt % 2 != 0:
    barcodes.append(make_barcode(passcnt, DUP, lastblock) )
    barcodes.append(make_barcode(passcnt, DUP, lastblock) )


print(barcodes)

# Cycle the Blocks across the pages
pages = []
PAGE_CNT = 3
pages = [[] for i in range(PAGE_CNT)]
offset = -1
for i in range(len(barcodes)):
    if i % PAGE_CNT == 0:
        offset = (offset + 1) % PAGE_CNT
    pages[ (i + offset) % PAGE_CNT ].append(barcodes[i])

print(pages)
