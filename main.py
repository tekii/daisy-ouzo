import os
import re
import logging

from flask import Flask, request, abort, jsonify
from party_catalog import *

app = Flask(__name__)

_logger = logging.getLogger("ouzo")

if __name__ != "__main__" and __name__ != "__test__":
    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    logging.basicConfig(level=gunicorn_error_logger.getEffectiveLevel(), handlers=gunicorn_error_logger.handlers)
else:
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))


@app.errorhandler(500)
def unauthorized(e):
    _logger.exception(msg=">>>>>>>>>", exc_info=e)
    error = str(e)
    return jsonify(error=error), 500


@app.errorhandler(404)
def unauthorized(e):
    # error = str(e)
    error = f'URL "{request.url}" not found.'
    _logger.error(error)
    return jsonify(error=error), 404


@app.errorhandler(400)
def unauthorized(e):
    error = str(e)
    _logger.error(error)
    return jsonify(error=error), 400


_gln_pattern = re.compile("[0-9]{13,14}")

_catalog = ThePartyCatalog()


@app.route("/search/<gln>/<cuit>")
@app.route("/gln/<gln>")
def lookup_gln(gln=None, cuit=None):

    if gln is None or _gln_pattern.fullmatch(gln) is None:
        abort(400, "Undefined/malformed GLN resource")

    result = _catalog.lookup(gln)

    if result is None:
        abort(404, f"GLN {gln} not found.")

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 12010)))

elif __name__ == "__test__":
    pass
