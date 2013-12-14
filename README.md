paperbin
========

Creates printable PNGs that can be used to export data to a paper and later scanned in again.

The application reads from stdin and creates blocks of data. Every 2 blocks are XORed to create a 3rd block (if there is only one block remaining, it is duplicated twice). These blocks are then converted into base32 with some metadata.

All of the blocks are then sorted into 3 different groups.  Only data from any two groups for each set of blocks is needed to regenerate the original message.

Lastly, the barcodes in each group are converted to pages of barcodes.

These barcodes can then be scanned in and reässembled later to create the original message (Work in progress).

Example

    gpg --export-secret-key | python3 paperbin.py --name secret-key

