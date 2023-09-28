#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""test
"""
import os
import sys
import pathlib

test_dir = pathlib.Path(__file__).absolute().parent
root_dir = test_dir.parent
sys.path.insert(0, str(root_dir))

print("root_dir: ", root_dir)
print("test_dir: ", test_dir)


# using pytest
def test_main():
    from logo_qrcode.logo_qrcode import QRMaker

    qr_maker = QRMaker("http://www.google.com", 512)
    qr_maker.add_logo("logo.png")
    qr_maker.save_image("google.png")
    print(qr_maker.to_base64())


if __name__ == "__main__":
    os.chdir(test_dir)
    test_main()
