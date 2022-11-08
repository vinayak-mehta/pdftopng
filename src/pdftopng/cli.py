# -*- coding: utf-8 -*-

import click

from . import pdftopng
from . import __version__


@click.command("pdftopng")
@click.version_option(version=__version__)
@click.argument("pdf_path", type=click.Path(exists=True))
@click.argument("png_path", required=False)
@click.pass_context
def cli(ctx, *args, **kwargs):
    """A PDF to PNG conversion tool (based on `pdftoppm` from `poppler`)"""

    pdf_path = kwargs["pdf_path"]
    png_path = kwargs["png_path"]

    # If no png path is given, use pdf path and replace extension.
    if png_path is None:
        png_path = pdf_path.rsplit(".", 1)[0] + '.png'

    pdftopng.convert(pdf_path=pdf_path, png_path=png_path)
