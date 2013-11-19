#!/usr/bin/env python3

import sys
import base64
import ctypes

passcnt = 0
block = None
lastblock = None;

DATA = '-'
XOR  = '%'
DUP  = '+'

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

BLOCKSIZE = 7

barcodes = []

with open('/dev/stdin', 'rb') as bindat:
    block = bindat.read(BLOCKSIZE)
    while len(block) != 0:
        padding = BLOCKSIZE - len(block) + 1
        block = block + bytes([padding for i in range(padding)])
        passcnt += 1
        barcodes.append(make_barcode(passcnt, DATA, block))
        if passcnt % 2 == 0:
            block = sxor(block, lastblock)
            barcodes.append(make_barcode(passcnt, XOR, block))
        else:
            lastblock = block
        block = bindat.read(BLOCKSIZE)
if passcnt % 2 == 1:
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
