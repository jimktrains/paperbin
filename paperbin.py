#!/usr/bin/env python3

import sys
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import base64
from ctypes import c_uint32

CODE39 = barcode.get_barcode_class('code39')
passcnt = 0
block = None
lastblock = None;

DATA = '-'
XOR  = '%'
DUP  = '+'

def make_barcode(num, typesym, block, name):
    block = block + (b'\0' * (BLOCKSIZE - len(block)))
    block = base64.b32encode(bytes(c_uint32(num))).decode('ascii').replace('=','') + typesym + base64.b32encode(block).decode('ascii').replace('=','')
    bc = CODE39(block, writer=ImageWriter())
    print(bc.save(name))
def sxor(s1,s2):    
    if len(s1) != len(s2):
        raise Exception("Lengths must be equal to xor")
    return bytes(a ^ b for a,b in zip(s1,s2))

BLOCKSIZE = 8

with open('/dev/stdin', 'rb') as bindat:
    block = bindat.read(BLOCKSIZE)
    while len(block) != 0:
        passcnt += 1
        make_barcode(passcnt, DATA, block, "test-%d" % passcnt)
        if passcnt % 2 == 0:
            print(len(block))
            print(len(lastblock))
            block = sxor(block, lastblock)
            print(len(block))
            make_barcode(passcnt, XOR, block, "test-%dp%d" % (passcnt - 1, passcnt))
        else:
            lastblock = block
        block = bindat.read(BLOCKSIZE)
if passcnt % 2 == 1:
    make_barcode(passcnt, DUP, block, "test-%dp%d" % (passcnt, passcnt) )
