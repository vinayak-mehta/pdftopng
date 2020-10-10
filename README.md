 # poppler-utils

Precompiled command-line utilities (based on Poppler) for manipulating PDF files and converting them to other formats.

## Installation

```
$ pip install .
```

## Usage

```
>>> from poppler_utils import pdftopng
>>> pdftopng.convert(pdf_path="foo.pdf", png_path="foo")
>>>
```
