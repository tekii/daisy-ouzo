import pytest
import json
from flask import url_for


def test_04_lookup_gtin(client):

    with client.application.test_request_context():
        url = url_for("lookup_gtin", gtin="7793397051573")

    response = client.get(url)
    assert response.status_code == 200
    assert response.data == b'{"gtin":"07793397051573"}\n'


def test_04_lookup_gtin_MARGARITA_4003(client):

    with client.application.test_request_context():
        url = url_for("lookup_gtin", gtin="7793397051570")

    response = client.get(url)
    assert response.status_code == 400
    errors = json.loads(response.data)
    assert len(errors) == 1
    assert errors[0]["errorType"] == "MARGARITA"
    assert errors[0]["errorCode"] == 4003


def test_05(client):

    with client.application.test_request_context():
        url = url_for("lookup_event", movimiento="07", file="TUTEUR0000.TXT")

    response = client.get(url)
    assert response.status_code == 200
    # assert response.data == b'{"gtin":"07793397051573"}\n'


@pytest.mark.skip("the url can´t be built")
def test_06_lookup_event_MARGARITA_6001(client):

    with client.application.test_request_context():
        url = url_for("lookup_event", movimiento="", file="TUTEUR0000.TXT")

    response = client.get(url)
    assert response.status_code == 400
    errors = json.loads(response.data)
    assert len(errors) == 1
    assert errors[0]["errorType"] == "MARGARITA"
    assert errors[0]["errorCode"] == 6001
    assert errors[0]["errorArgs"]["origen"] == ["event-lookup-service"]
    assert errors[0]["errorArgs"]["argumentos"] == ["actor", "file"]
    assert errors[0]["errorArgs"]["valores"] == ["TUTEUR", "TUTEUR0000.TXT"]
    assert errors[0]["errorArgs"]["mandatorios"] == ["movimiento"]


def test_06_lookup_event_MARGARITA_6002(client):

    with client.application.test_request_context():
        url = url_for("lookup_event", movimiento="00", file="TUTEUR0000.TXT")

    response = client.get(url)
    assert response.status_code == 400
    errors = json.loads(response.data)
    assert len(errors) == 1
    assert errors[0]["errorType"] == "MARGARITA"
    assert errors[0]["errorCode"] == 6002
    assert errors[0]["errorArgs"]["origen"] == ["event-lookup-service"]
    assert errors[0]["errorArgs"]["argumentos"] == ["actor", "file"]
    assert errors[0]["errorArgs"]["valores"] == ["TUTEUR", "TUTEUR0000.TXT"]
    assert errors[0]["errorArgs"]["movimiento"] == ["00"]


def test_06_lookup_event_MARGARITA_7001(client):

    with client.application.test_request_context():
        url = url_for("lookup_event", movimiento="28", file="TUTEUR0000.TXT")

    response = client.get(url)
    assert response.status_code == 400
    errors = json.loads(response.data)
    assert len(errors) == 1
    assert errors[0]["errorType"] == "MARGARITA"
    assert errors[0]["errorCode"] == 7001
    assert errors[0]["errorArgs"]["origen"] == ["event-lookup-service"]
    assert errors[0]["errorArgs"]["actor"] == ["TUTEUR"]
    assert errors[0]["errorArgs"]["motivo"] == ["movimiento", "28"]


def test_calculate_rowid_a_1(client):

    with client.application.test_request_context():
        url = url_for(
            "calculate_rowid",
            actor="7793397000007",
            row="1",
            encoded_path="%2Fmnt%2Faux%2Fdfs%2Fmails%2Fafms%2F20120816%2F1200%2Fremitos.csv",
        )

    response = client.get(url)
    assert response.status_code == 200
    assert response.data == b"fcbdda10f1e63863ae0c52345b626009"


def test_calculate_rowid_a_2(client):

    with client.application.test_request_context():
        url = url_for(
            "calculate_rowid",
            actor="7793397000007",
            row="109",
            encoded_path="%2Fmnt%2Fv1%2Ftemp%2Ftuteur%2F4a4355d400f611f08890dbe26f81d24d%2F20241012"
            "%2F1232%2Fcorrected%2FTUTEUR1210241232.TXT",
        )

    response = client.get(url)
    assert response.status_code == 200
    assert response.data == b"a4ca3d5a1c9a0ce2722af147efbea6f7"


def test_08(client):

    with client.application.test_request_context():
        url = url_for("serial_processor", serial_w_id="00010000", actor="7793397000007")

    response = client.get(url)
    assert response.status_code == 200


def test_09(client):

    with client.application.test_request_context():
        url = url_for(
            "serial_processor", serial_w_id="01080540830151632110000042624017260216101207642"
        )

    response = client.get(url)
    assert response.status_code == 200
