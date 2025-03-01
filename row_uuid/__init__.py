"""RowUUID"""

from datetime import datetime
from urllib.parse import unquote
from pathlib import Path
from hashlib import md5
from tkerror import TkError


__all__ = ["calculate"]


def calculate(actor, row, encoded_path):
    """ "calculates the rowid"""
    try:
        unquoted = unquote(encoded_path, encoding="utf-8")
        path = Path(unquoted)
        date, time, name = path.parts[-3:]
        datetime.strptime(date + time, "%Y%m%d%H%M")
        stem = actor + name + date + time + str(row)
        hash_ = md5()
        hash_.update(stem.encode("utf-8"))
        return hash_.hexdigest()

    except Exception as e:
        raise TkError(
            errorCode=TkError.MAR.ERROR_NULO,
            errorArgs={
                "origen": [__name__],
                "argumentos": ["actor", "row", "date", "time", "name"],
                "valores": [actor, row, date, time, name],
                "message": [str(e)],
            },
        ) from e
