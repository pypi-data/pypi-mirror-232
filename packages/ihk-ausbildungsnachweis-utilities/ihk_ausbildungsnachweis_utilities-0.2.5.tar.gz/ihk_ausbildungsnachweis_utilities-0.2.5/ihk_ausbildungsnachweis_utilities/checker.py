# Copyright (C) 2023 twyleg
from pathlib import Path


def check_ausbildungsnachweis_pdf_for_signature(ausbildungsnachweis_pdf_filepath: Path) -> bool:
    with open(ausbildungsnachweis_pdf_filepath, "rb") as file:
        data = file.read()
        n = data.find(b"/ByteRange")
        if n == -1:
            return False
        start = data.find(b"[", n)
        stop = data.find(b"]", start)
        if start == -1 or stop == -1:
            return False
        return True
