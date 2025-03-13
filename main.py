import os
import re
from datetime import datetime, timezone
import logging
import logging.handlers

from flask import Flask, request, abort, jsonify
import gs1
from party_catalog import ThePartyCatalog
from event_lookup import event_lookup
from tkerror import TkError
import row_uuid
import symbol_processor

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
def handle_404(_):
    # error = str(e)
    error = f"URL {request.path} not found."
    _logger.error(error)
    return jsonify(error=error), 404


@app.errorhandler(400)
def handle_400(e):
    error = str(e)
    _logger.error(error)
    return jsonify(error=error), 400


@app.errorhandler(TkError)
def handle_tkerror(e):
    _logger.error(msg=f"MARGARITA-{e.errorCode}")
    error = {
        "errorType": "MARGARITA",
        "errorCode": e.errorCode,
        "errorArgs": e.erroArgs,
        "errorTimeStamp": datetime.now(timezone.utc).isoformat(),
    }
    return jsonify([error]), e.code


_gln_pattern = re.compile("[0-9]{13,14}")

_catalog = ThePartyCatalog()


@app.route("/search/<gln>/<cuit>")
@app.route("/gln/<gln>")
def lookup_gln(gln=None, cuit=None):

    if gln is None or _gln_pattern.fullmatch(gln) is None:
        raise TkError(
            errorCode=TkError.MAR.GLN_FORMATO_INVALIDO,
            errorArgs={
                "gln": [gln],
                "origen": ["PartyLookup"],
                "message": [f"-{gln}- is either undefined or malformed GLN resource"],
            },
        )

    result = _catalog.lookup(gln)

    if result is None:
        abort(404, f"GLN -{gln}- Not Found.")

    return jsonify(result)


@app.route("/gtin/<gtin>")
def lookup_gtin(gtin=None):
    _logger.debug("/gtin/%s", gtin)
    try:
        valid_gtin = gs1.GTIN(gtin)
        valid_gtin.verify()

    except ValueError as e:
        raise TkError(
            errorCode=TkError.MAR.GTIN_FORMATO_INVALIDO,
            errorArgs={
                "gtin": [gtin],
                "origen": ["TradeItemLookup"],
                "message": ["Invalid GTIN format."],
            },
        ) from e

    return jsonify({"gtin": str(valid_gtin)})


@app.route("/tuteur/<movimiento>/<file>")
def lookup_event(movimiento=None, file=None):
    _logger.debug("/tuteur/%s/%s", movimiento, file)
    result = event_lookup(movimiento, file)
    return jsonify(result)


@app.route("/serialProcessor/<string:serial_w_id>")
def serial_processor(serial_w_id):
    _logger.debug("/serialProcessor/%s", serial_w_id)
    actor = request.args.get("actor", type=str)
    batch = request.args.get("batch", type=str)
    lab = request.args.get("lab", type=str)
    gtin = request.args.get("gtin", type=str)
    result = symbol_processor.parse(serial_w_id, actor, batch, lab, gtin)
    return jsonify(result)


@app.route("/<string:actor>/<int:row>/<path:encoded_path>")
def calculate_rowid(actor, row, encoded_path):
    _logger.debug("/%s/%d/%s", actor, row, encoded_path)
    result = row_uuid.calculate(actor, row, encoded_path)
    return result, 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 12010)))

elif __name__ == "__test__":
    pass
