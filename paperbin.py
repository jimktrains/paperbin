#!/usr/bin/env python3

import sys
import base64
import ctypes
import argparse
import base58


import qrcode
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

passcnt = 0
block = None
lastblock = None;
barcode_texts = []


parser = argparse.ArgumentParser(description='Creates data and XOR-parity blocks suitable for human or barcode_text entry')
#parser.add_argument('--type', dest='type', action='store', default="QRCODE", help='Type of Barcode. Values maybe CODE39 or QRCODE')
parser.add_argument('--name', dest='name', action='store', default="page", help='Name of the input, to put on output pages')

args = parser.parse_args()


barcode = None
BLOCKSIZE = 25
DPI=72
data_name = args.name

DATA = '-'
XOR  = '%'
DUP  = '+'

# The barcode_text is of the form
# <base32(block number)><type><base32(block)>
def make_barcode_text(num, typesym, block):
    num = base64.b32encode(bytes(ctypes.c_uint16(num)))
    newblock = num.decode('ascii').replace('=','')
    newblock += typesym
    newblock += base58.b58encode_check(block)
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
        barcode_texts.append(make_barcode_text(passcnt, DATA, block))
        if passcnt % 2 == 0:
            block = sxor(block, lastblock)
            barcode_texts.append(make_barcode_text(passcnt, XOR, block))
        else:
            lastblock = block
        block = bindat.read(BLOCKSIZE-1)

# Simply duplicating the last block may not be an option
# if more than 3 groups are used.
if passcnt % 2 != 0:
    barcode_texts.append(make_barcode_text(passcnt, DUP, lastblock) )
    barcode_texts.append(make_barcode_text(passcnt, DUP, lastblock) )


# Cycle the Blocks across the pages
pages = []
PAGE_CNT = 3
pages = [[] for i in range(PAGE_CNT)]
offset = -1
for i in range(len(barcode_texts)):
    if i % PAGE_CNT == 0:
        offset = (offset + 1) % PAGE_CNT
    pages[ (i + offset) % PAGE_CNT ].append(barcode_texts[i])

page_size = (int(8.5*DPI), int(11*DPI))

font = ImageFont.load_default()
for page_i in range(len(pages)):
    background = None
    for bc_i in range(len(pages[page_i])):
        if bc_i % 70 == 0:
            if background is not None:
                fn = "%s-%d-%d.png" % (data_name, page_i, int( (bc_i - 70)/70))
                with open(fn, 'wb') as buf:
                    print("Wrote %s" % fn)
                    background.save(buf, format="PNG")
            background = Image.new('1', page_size, 255)
            d = ImageDraw.Draw(background)
            d.text((int(DPI/2), int(DPI/4)), "%s-%d-%d " % (data_name, page_i, int(bc_i/70)))
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=2
        )
        qr.add_data(pages[page_i][bc_i], optimize=0)
        qr.make(fit=True)
        img = qr.make_image()
        bc_i_adj = bc_i - (int(bc_i/70)*70)
        x = (int(bc_i_adj%7)*DPI) + int(DPI/2)
        y = (int(bc_i_adj/7)*DPI) + int(DPI/2)
        background.paste(img, (x,y))
    fn = "%s-%d-%d.png" % (data_name, page_i, int(len(pages[page_i])/70))
    with open(fn, 'wb') as buf:
        print("Wrote %s" % fn)
        background.save(buf, format="PNG")
