# -*- coding: utf-8 -*-

import click

from . import pdftopng
from . import __version__


@click.command("pdftopng")
@click.version_option(version=__version__)
@click.argument("pdf_path", type=click.Path(exists=True))
@click.argument("png_path")
@click.pass_context
def cli(ctx, *args, **kwargs):
    """A PDF to PNG conversion tool (based on `pdftoppm` from `poppler`)"""

    pdf_path = kwargs["pdf_path"]
    png_path = kwargs["png_path"]

    pdftopng.convert(pdf_path=pdf_path, png_path=png_path)
