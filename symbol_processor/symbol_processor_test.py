import pytest
import symbol_processor
from tkerror import TkError


def test_exsa_01():
    # pass
    # 7793397000007
    # "/serialProcessor/00001234?actor=&batch=&lab=&gtin="
    # 01 08054083015163 21 100000426240 17 260216 10 1207642
    symbol_processor.parse("01080540830151632110000042624017260216101207642")
    pass


def test_tuteur_02():
    symbol_processor.parse("00001000")
    pass


def test_exsa_03():
    with pytest.raises(TkError) as e:
        symbol_processor.parse("")
    assert e.type == TkError
