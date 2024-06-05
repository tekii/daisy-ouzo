"""SymbolProcessor"""

import re

__all__ = ["parse"]

_RE = re.compile(r"^01(0?\d{13})21([^+]{1,20})\+?17((?:1[1-9]|2[0-9])(?:0[1-9]|1[012])(?:[012]\d|30|31))10(.{1,20})$|^(.{1,20})$")
# _EXSA___RE = re.compile(r"^01(0?\d{13})21([^+]{1,20})\+?17((?:1[1-9]|2[0-9])(?:0[1-9]|1[012])(?:[012]\d|30|31))10(.{1,20})$")
# _TUTEUR_RE = re.compile(r"^(.{1,20})$")


def parse(serial_w_id: str, actor=None, batch=None, lab=None, gtin=None):

    symbol = {
        "serial": None,  # symbol.serial,
        "rawSerial": serial_w_id,  # symbol.raw,
        "expire": None,  # symbol.expiration ? vencimiento : null,
        "gln": None,  # symbol.gln ? symbol.gln.toString() : null,
        "gtin": None,  # symbol.gtin ? symbol.gtin.toString() : null,
        "batch": None,  # symbol.lote ? symbol.lote.toString() : null
    }

    match = _RE.match(serial_w_id)
    if match:

        if match[5]:
            symbol["serial"] = match[0]

        else:
            symbol["gtin"] = match[1]
            symbol["serial"] = match[2]
            symbol["expire"] = match[3]
            symbol["batch"] = match[4]

        return symbol

    else:
        return None
