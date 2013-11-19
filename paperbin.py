#!/usr/bin/env python3

import sys
import barcode
import base64
import ctypes

passcnt = 0
block = None
lastblock = None;

DATA = '-'
XOR  = '%'
DUP  = '+'

def make_barcode(num, typesym, block, name):
    block = base64.b32encode(bytes(ctypes.c_uint16(num))).decode('ascii').replace('=','') + typesym + base64.b32encode(block).decode('ascii').replace('=','')
    print(block)
    return block

def sxor(s1,s2):    
    if len(s1) != len(s2):
        raise Exception("Lengths must be equal to xor")
    return bytes(a ^ b for a,b in zip(s1,s2))

BLOCKSIZE = 8

with open('/dev/stdin', 'rb') as bindat:
    block = bindat.read(BLOCKSIZE)
    while len(block) != 0:
        block = block + (b'\0' * (BLOCKSIZE - len(block)))
        passcnt += 1
        make_barcode(passcnt, DATA, block, "test-%d" % passcnt)
        if passcnt % 2 == 0:
            block = sxor(block, lastblock)
            make_barcode(passcnt, XOR, block, "test-%dp%d" % (passcnt - 1, passcnt))
        else:
            lastblock = block
        block = bindat.read(BLOCKSIZE)
if passcnt % 2 == 1:
    make_barcode(passcnt, DUP, lastblock, "test-%dp%d" % (passcnt, passcnt) )
