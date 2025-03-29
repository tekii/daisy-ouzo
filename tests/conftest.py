import pytest
from typing import Any
import pathlib


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
