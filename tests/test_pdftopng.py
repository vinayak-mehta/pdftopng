# -*- coding: utf-8 -*-

import os

import pytest
from PIL import Image, ImageChops

from pdftopng import pdftopng

testdir = os.path.dirname(os.path.abspath(__file__))


def test_pdftopng():
    filename = os.path.join(testdir, "foo.pdf")

    pdftopng.convert(pdf_path=filename, png_path="/tmp/foo.png")

    im1 = Image.open(os.path.join(testdir, "foo.png"))
    im2 = Image.open("/tmp/foo.png")

    diff = ImageChops.difference(im1, im2)
    extrema = diff.getextrema()
    max_diff = max(max(channel) for channel in extrema)
    assert max_diff <= 5, f"Images differ by {max_diff} pixels"
