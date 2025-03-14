import os
import re
from datetime import datetime, timezone
import logging
import logging.handlers

from flask import Flask, request, abort, jsonify
import gs1
from party_catalog import ThePartyCatalog, MultipleResults
from event_lookup import event_lookup
from tkerror import TkError
import row_uuid
import symbol_processor

app = Flask(__name__)

_logger = logging.getLogger("OUZO")

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
    # _logger.error(msg=f"MARGARITA-{e.errorCode}")
    msg = e.errorArgs["message"] if "message" in e.errorArgs else "No message"
    _logger.log(level=e.level, msg=f"MARGARITA-{e.errorCode} - {msg}")
    error = {
        "errorType": "MARGARITA",
        "errorCode": e.errorCode,
        "errorArgs": e.errorArgs,
        "errorTimeStamp": datetime.now(timezone.utc).isoformat(),
    }
    return jsonify([error]), e.code


_cuit_pattern = re.compile(r"[0-9]{11}")
_catalog = ThePartyCatalog()


@app.route("/search/<gln>/<cuit>")
@app.route("/search/<gln>/null")
@app.route("/search/null/<cuit>")
@app.route("/search/null/null")
def party_lookup(gln=None, cuit=None):

    # if gln is not None and _gln_pattern.fullmatch(gln) is None:
    if gln is not None:
        try:
            valid_gln = gs1.GLN(gln)
            valid_gln.verify()
        except ValueError as e:
            raise TkError(
                errorCode=TkError.MAR.GLN_FORMATO_INVALIDO,
                errorArgs={
                    "gln": [gln],
                    "origen": ["PartyLookup"],
                    "message": [f"PartyLookup -{gln}- is either invalid or malformed GLN resource"],
                },
            ) from e

    if cuit is not None and _cuit_pattern.fullmatch(cuit) is None:
        raise TkError(
            errorCode=TkError.MAR.CUIT_FORMATO_INVALIDO,
            errorArgs={
                "cuit": [cuit],
                "origen": ["PartyLookup"],
                "message": [f"PartyLookup -{cuit}- is either invalid or malformed CUIT resource"],
            },
        )

    try:

        result = _catalog.lookup(gln=gln, cuit=cuit) if gln is not None or cuit is not None else None

    except MultipleResults as e:
        raise TkError(
            errorCode=TkError.MAR.RESULTADOS_MULTIPLES,
            errorArgs={
                "origen": ["PartyLookup"],
                "message": [e.msg],
            },
        ) from e

    if result is None:
        # abort(404, f"PartyLookup -{gln}-{cuit}- Not Found in PartyCatalog")
        raise TkError(
            errorCode=TkError.MAR.ERROR_NULO,
            errorArgs={
                "origen": ["PartyLookup"],
                "message": [f"PartyLookup -{gln}-{cuit}- Not Found in PartyCatalog"],
            },
            code=404,
            level=logging.ERROR,
        )

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
                "message": [f"TradeItemLookup -{gtin}- id invalid or malformed GTIN resource"],
            },
            level=logging.WARNING,
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
