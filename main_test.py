import json
import pathlib
import pytest
from typing import Any


@pytest.fixture()
def client():
    from importlib.util import spec_from_file_location, module_from_spec

    source = pathlib.Path(__file__).resolve().parent / "main.py"
    spec = spec_from_file_location("__test__", str(source))
    main = module_from_spec(spec)
    spec.loader.exec_module(main)
    yield main.app.test_client()
    # purge the cache object here
    the_catalog = main.__dict__["catalog"]
    the_catalog.purge()
    # del the_catalog.__class__._the_instance
    delattr(the_catalog.__class__, "_the_instance")


def test_01(client):
    response = client.get("/")
    assert response.status_code == 200
    # assert response.data == b'{"text":"Thanks for adding me to a DM, Human One!"}\n'


def test_02(client):
    response = client.get("/")
    assert response.status_code == 200
