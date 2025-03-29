import pytest
import json
from flask import url_for


def test_party_lookup_null_null(test_runner_service_account_credentials, client):

    with client.application.test_request_context():
        url = url_for("party_lookup", gln=None, cuit=None)

    response = client.get(url)
    assert response.status_code == 404


def test_party_lookup_malformed_gln_null(test_runner_service_account_credentials, client):

    with client.application.test_request_context():
        url = url_for("party_lookup", gln="0779339700000", cuit=None)  # remove the last digit (7) and add 0

    response = client.get(url)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data[0]["errorType"] == "MARGARITA"
    assert data[0]["errorCode"] == 4002


def test_party_lookup_null_gln_malformed_cuit(test_runner_service_account_credentials, client):

    with client.application.test_request_context():
        url = url_for("party_lookup", gln=None, cuit="0")  # remove the last digit (7) and add 0

    response = client.get(url)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data[0]["errorType"] == "MARGARITA"
    assert data[0]["errorCode"] == 4004


def test_party_lookup_valid_gln_null_cuit(test_runner_service_account_credentials, client):

    with client.application.test_request_context():
        url = url_for("party_lookup", gln="7793397000007", cuit=None)

    response = client.get(url)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 5
    assert data["cached"] == False
    assert data["gln"] == "7793397000007"
    response = client.get(url)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 4
    assert "cached" not in data
    assert data["gln"] == "7793397000007"


def test_party_lookup_null_gln_valid_cuit(test_runner_service_account_credentials, client):
    """THIS TEST MULTIPLE RESULT BECAUSE CUIT IS NOT UNIVOQUE ENOUGH"""
    with client.application.test_request_context():
        url = url_for("party_lookup", gln=None, cuit="30710261551")

    response = client.get(url)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]["errorType"] == "MARGARITA"
    assert data[0]["errorCode"] == 9006


def test_party_lookup_valid_gln_valid_cuit(test_runner_service_account_credentials, client):

    with client.application.test_request_context():
        url = url_for("party_lookup", gln="7793397000007", cuit="30589864642")

    response = client.get(url)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 5
    assert data["cached"] == False
    assert data["gln"] == "7793397000007"
    assert data["cuit"] == "30589864642"
