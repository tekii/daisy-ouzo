import pytest

import gs1


def test_01():
    for s in [
        "07793397051573",
        "07793397035238",
        "7798140310006",
        "7798120570000",
        "7793397000236",
        "7793397010020",
        "9990001200008",
        "9991277200006",
    ]:
        gtin = gs1.GTIN(s)
        assert gtin.verify()
        a = str(gtin)
        assert len(a) == 14


def test_02():
    for s in [
        "7798140310006",
        "7798120570000",
        "7793397000236",
        "7793397010020",
        "9990001200008",
        "9991277200006",
    ]:
        gtin = gs1.GLN(s)
        assert gtin.verify()
        a = str(gtin)
        assert len(a) == 13


def test_03():
    with pytest.raises(ValueError) as e:
        gln = gs1.GLN("07793397051573")
    assert e.type == ValueError


def test_04():
    with pytest.raises(ValueError) as e:
        gln = gs1.GLN("7798140310005")
        gln.verify()
    assert e.type == ValueError
