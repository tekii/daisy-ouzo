import logging.handlers
import os
import re
from datetime import datetime, timezone
import logging

from flask import Flask, request, abort, jsonify
import gs1
from party_catalog import *
from event_lookup import event_lookup
from tkerror import TkError

app = Flask(__name__)

_logger = logging.getLogger("ouzo")

if __name__ != "__main__" and __name__ != "__test__":
    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    logging.basicConfig(level=gunicorn_error_logger.getEffectiveLevel(), handlers=gunicorn_error_logger.handlers)
    app.logger.setLevel(gunicorn_error_logger.getEffectiveLevel())
    app.logger.handlers = gunicorn_error_logger.handlers
else:
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
    # logging.handlers = app.logger.handlers


@app.errorhandler(500)
def handle_500(e):
    _logger.exception(msg=">>>>>>>>>", exc_info=e)
    error = str(e)
    return jsonify(error=error), 500


@app.errorhandler(404)
def handle_404(e):
    # error = str(e)
    error = f"URL {request.path} not found."
    _logger.error(error)
    return jsonify(error=error), 404


@app.errorhandler(400)
def handle_400(e):
    error = str(e)
    _logger.error(error)
    return jsonify(error=error), 400


_gln_pattern = re.compile("[0-9]{13,14}")

_catalog = ThePartyCatalog()


@app.route("/search/<gln>/<cuit>")
@app.route("/gln/<gln>")
def lookup_gln(gln=None, cuit=None):

    if gln is None or _gln_pattern.fullmatch(gln) is None:
        abort(400, f"{gln} is either undefined or malformed GLN resource")

    result = _catalog.lookup(gln)

    if result is None:
        abort(404, f"GLN {gln} not found.")

    return jsonify(result)


@app.route("/gtin/<gtin>")
def lookup_gtin(gtin=None):
    _logger.debug("/gtin/%s", gtin)
    try:
        valid_gtin = gs1.GTIN(gtin)
        valid_gtin.verify()

    except ValueError:
        _logger.error("gtin %s invalid.", gtin)
        error = {
            "errorType": "MARGARITA",
            "errorCode": 4003,
            "errorArgs": {"gtin": [gtin], "origen": ["TradeItemLookup"], "message": ["Some error message."]},
            "errorTimeStamp": datetime.now(timezone.utc).isoformat(),
        }
        return jsonify(error), 400

    return jsonify({"gtin": str(valid_gtin)})


@app.route("/tuteur/<movimiento>/<file>")
def lookup_event(movimiento=None, file=None):
    _logger.debug("/tuteur/%s/%s", movimiento, file)
    try:
        result = event_lookup(movimiento, file)
        return jsonify(result)
    except TkError as e:
        _logger.error(msg=f"MARGARITA-{e.errorCode}")
        error = {
            "errorType": "MARGARITA",
            "errorCode": e.errorCode,
            "errorArgs": e.erroArgs,
            "errorTimeStamp": datetime.now(timezone.utc).isoformat(),
        }
        return jsonify(error), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 12010)))

elif __name__ == "__test__":
    pass
