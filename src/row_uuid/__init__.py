"""RowUUID"""

from datetime import datetime
from hashlib import md5
from pathlib import Path
from urllib.parse import unquote

from tkerror import TkError

__all__ = ["calculate"]


def calculate(actor, row, encoded_path):
    """ "calculates the rowid"""
    try:
        unquoted = unquote(encoded_path, encoding="utf-8")
        path = Path(unquoted)
        a, b, c, d = path.parts[-4:]
        date, time, name = (a, b, d) if c == "corrected" else (b, c, d)
        # date, time, _, name = path.parts[-4:]
        datetime.strptime(date + time, "%Y%m%d%H%M")  # this validates the datetime or blows
        stem = actor + name + date + time + str(row)
        hash_ = md5()
        hash_.update(stem.encode("utf-8"))
        return hash_.hexdigest()

    except Exception as e:
        raise TkError(
            errorCode=TkError.MAR.SERVICIO_FALTAN_ARGUMENTOS,
            errorArgs={
                "origen": [__name__],
                "Errors": ["020", "030", "040"],
                "argumentos": ["actor", "row", "date", "time", "name"],
                "valores": [actor, row, date, time, name],
                "message": ["Some message"],
            },
        ) from e
