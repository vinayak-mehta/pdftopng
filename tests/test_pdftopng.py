# -*- coding: utf-8 -*-

import os

import pytest

from pdftopng import pdftopng
from PIL import Image, ImageChops


testdir = os.path.dirname(os.path.abspath(__file__))


def test_pdftopng():
    filename = os.path.join(testdir, "foo.pdf")

    pdftopng.convert(pdf_path=filename, png_path="/tmp/foo")

    im1 = Image.open(os.path.join(testdir, "foo.png"))
    im2 = Image.open("/tmp/foo.png")

    assert ImageChops.difference(im1, im2).getbbox() is None
