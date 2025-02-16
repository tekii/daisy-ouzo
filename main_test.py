import json
import pathlib
import pytest
from typing import Any
from flask import url_for

import google.auth
from google.oauth2 import service_account


def _default(scopes: Any | None = ["https://www.googleapis.com/auth/cloud-platform"]):
    """Replaces the current default credentials w/ de test-runner ones."""
    credentials = service_account.Credentials.from_service_account_file(
        "../.secrets/mock_credentials.json",
        scopes=scopes,
    )
    return credentials, "daisy-dev01"


@pytest.fixture(autouse=False)
def test_runner_service_account_credentials(monkeypatch):
    # replace curent default w/ the service account JWT
    monkeypatch.setattr(google.auth, "default", _default)


@pytest.fixture()
def client():
    from importlib.util import spec_from_file_location, module_from_spec

    source = pathlib.Path(__file__).resolve().parent / "main.py"
    spec = spec_from_file_location("__test__", str(source))
    main = module_from_spec(spec)
    spec.loader.exec_module(main)
    yield main.app.test_client()
    # purge the cache object here
    the_catalog = main.__dict__["_catalog"]
    the_catalog.purge()
    # del the_catalog.__class__._the_instance
    delattr(the_catalog.__class__, "_the_instance")


def test_01(test_runner_service_account_credentials, client):

    with client.application.test_request_context():
        url_1 = url_for("lookup_gln", gln="")
        url_2 = url_for("lookup_gln", gln="0")

    response = client.get(url_1)
    assert response.status_code == 404

    response = client.get(url_2)
    assert response.status_code == 400


def test_02(test_runner_service_account_credentials, client):

    with client.application.test_request_context():
        url = url_for("lookup_gln", gln="7798165540006")

    response = client.get(url)
    assert response.status_code == 200
    assert response.data == b'{"cached":false,"cuit":"30710261551","gln":"7798165540006","idTipoAgente":4,"nombreTipoAgente":"DROGUERIA"}\n'

    response = client.get(url)
    assert response.status_code == 200
    assert response.data == b'{"cuit":"30710261551","gln":"7798165540006","idTipoAgente":4,"nombreTipoAgente":"DROGUERIA"}\n'


def test_03(test_runner_service_account_credentials, client):

    with client.application.test_request_context():
        url_1 = url_for("lookup_gln", gln="8888888888888")

    response = client.get(url_1)
    assert response.status_code == 404


def test_04(client):

    with client.application.test_request_context():
        url = url_for("lookup_gtin", gtin="7793397051573")

    response = client.get(url)
    assert response.status_code == 200
    assert response.data == b'{"gtin":"07793397051573"}\n'


def test_05(client):

    with client.application.test_request_context():
        url = url_for("lookup_event", movimiento="07", file="TUTEUR0000.TXT")

    response = client.get(url)
    assert response.status_code == 200
    # assert response.data == b'{"gtin":"07793397051573"}\n'


def test_06(client):

    with client.application.test_request_context():
        url = url_for("lookup_event", movimiento="00", file="TUTEUR0000.TXT")

    response = client.get(url)
    assert response.status_code == 400
    # assert response.data == b'{"gtin":"07793397051573"}\n'


def test_07(client):

    with client.application.test_request_context():
        url = url_for(
            "calculate_rowid",
            actor="7793397000007",
            row="1",
            encoded_path="mnt%2Faux%2Fdfs%2Fmails%2Fafms%2F20120816%2F1200%2Fremitos.csv",
        )

    # url = "/7793397000007/1/mnt%2Faux%2Fdfs%2Fmails%2Fafms%2F20120816%2F1200%2Fremitos.csv"
    response = client.get(url)
    assert response.status_code == 200
    assert response.data == b"fcbdda10f1e63863ae0c52345b626009"


def test_08(client):

    with client.application.test_request_context():
        url = url_for("serial_processor", serial_w_id="00010000", actor="7793397000007")

    response = client.get(url)
    assert response.status_code == 200


def test_09(client):

    with client.application.test_request_context():
        url = url_for("serial_processor", serial_w_id="01080540830151632110000042624017260216101207642")

    response = client.get(url)
    assert response.status_code == 200
