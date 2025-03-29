import pytest
from typing import Any
import pathlib
import google.auth
from google.oauth2 import service_account


def _default(scopes: Any | None = ["https://www.googleapis.com/auth/cloud-platform"]):
    """Replaces the current default credentials w/ de test-runner ones."""
    credentials = service_account.Credentials.from_service_account_file(
        "../.secrets/test-runner-credentials.json",
        scopes=scopes,
    )
    # TODO: get the project id from somewhere, the account file is a possible source.
    return credentials, "daisy-dev01"


@pytest.fixture(autouse=False)
def test_runner_service_account_credentials(monkeypatch):
    # replace curent default w/ the service account JWT
    monkeypatch.setattr(google.auth, "default", _default)


@pytest.fixture(autouse=False)
def client():
    from importlib.util import spec_from_file_location, module_from_spec

    source = pathlib.Path(__file__).resolve().parent / ".." / "src" / "main.py"
    spec = spec_from_file_location("__test__", str(source))
    main = module_from_spec(spec)
    spec.loader.exec_module(main)
    yield main.app.test_client()
    # purge the cache object here
    the_catalog = main.__dict__["_catalog"]
    the_catalog.purge()
    # del the_catalog.__class__._the_instance
    delattr(the_catalog.__class__, "_the_instance")
