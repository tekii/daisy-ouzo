import pytest
import http.client
from flask import url_for


def test_calculate_rowid_a_2(client):

    encoded_path = "%2Fmnt%2Fv1%2Ftemp%2Ftuteur%2F4a4355d400f611f08890dbe26f81d24d%2F20241012%2F1232%2Fcorrected%2FTUTEUR1210241232.TXT"

    with client.application.test_request_context():
        url = url_for(
            "calculate_rowid_a",
            row="108",
            encoded_path=encoded_path,
            # encoded_path="/mnt/v1/temp/tuteur/4a4355d400f611f08890dbe26f81d24d/20241012/1232/corrected/TUTEUR1210241232.TXT",
        )

    response_1 = client.get(url)
    assert response_1.status_code == 200
    assert response_1.data == b"edacec7596bd0de837e9d91b4f17895f"

    url_2 = "/7793397000007/108/" + encoded_path
    connection = http.client.HTTPConnection(host="10.160.229.57", port=12020)
    connection.request("GET", url_2)
    response_2 = connection.getresponse()
    assert response_2.status == 200
    data_2 = response_2.read()
    assert data_2 == b"edacec7596bd0de837e9d91b4f17895f"

    assert data_2 == response_1.data

    #'{"errorType":"MARGARITA","errorCode":6001,"errorArgs":{"Errors":["030"]},"errorTimeStamp":"2025-03-15T02:02:12.294Z"}'
