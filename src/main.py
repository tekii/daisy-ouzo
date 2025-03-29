import os
import re
from datetime import datetime, timezone
import logging


from flask import Flask, request, jsonify
from werkzeug.routing import PathConverter

from tkerror import TkError
from tekii_margot_toolbox import gs1
from party_catalog import ThePartyCatalog
from event_lookup import event_lookup
import row_uuid
import symbol_processor


if __name__ != "__main__" and __name__ != "__test__":
    import google.cloud.logging

    labels = {"margot_service": "ouzo"}
    logging_client = google.cloud.logging.Client()
    logging_client.setup_logging(labels=labels)
    # gunicorn_error_logger = logging.getLogger("gunicorn.error")
    # level = gunicorn_error_logger.getEffectiveLevel()


app = Flask(__name__)  # the app is declare after the logger is setup


@app.errorhandler(500)
def handle_500(e):
    logging.exception(exc_info=e)
    error = str(e)
    return jsonify(error=error), 500


@app.errorhandler(404)
def handle_404(_):
    # error = str(e)
    error = f"URL {request.path} not found."
    logging.error(error)
    return jsonify(error=error), 404


@app.errorhandler(400)
def handle_400(e):
    error = str(e)
    logging.error(error)
    return jsonify(error=error), 400


@app.errorhandler(TkError)
def handle_tkerror(e):

    msg = e.errorArgs["message"][0] if "message" in e.errorArgs else e.errorArgs["mensaje"][0] if "mensaje" in e.errorArgs else "No message"
    error = {
        "errorType": "MARGARITA",
        "errorCode": e.errorCode,
        "errorArgs": e.errorArgs,
        "errorTimeStamp": datetime.now(timezone.utc).isoformat(),
    }
    labels = {"margarita_code": f"{e.errorCode}"}
    logging.log(
        level=e.level,
        msg=msg,
        extra={
            "labels": labels,
            "json_fields": error,
        },
    )
    return jsonify([error]), e.code


_cuit_pattern = re.compile(r"[0-9]{11}")
_catalog = ThePartyCatalog()


@app.route("/search/<gln>/<cuit>")
@app.route("/search/<gln>/null")
@app.route("/search/null/<cuit>")
@app.route("/search/null/null")
def party_lookup(gln=None, cuit=None):
    logging.debug(msg=f"party_lookup  in: {gln} {cuit}")

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
                level=logging.WARNING,
            ) from e

    if cuit is not None and _cuit_pattern.fullmatch(cuit) is None:
        raise TkError(
            errorCode=TkError.MAR.CUIT_FORMATO_INVALIDO,
            errorArgs={
                "cuit": [cuit],
                "origen": ["PartyLookup"],
                "message": [f"PartyLookup -{cuit}- is either invalid or malformed CUIT resource"],
            },
            level=logging.WARNING,
        )

    result = _catalog.lookup(gln=gln, cuit=cuit) if gln is not None or cuit is not None else None

    if result is None:
        raise TkError(
            errorCode=TkError.MAR.ERROR_NULO,
            errorArgs={
                "origen": ["PartyLookup"],
                "message": [f"PartyLookup -{gln}-{cuit}- Not Found in PartyCatalog"],
            },
            code=404,
            level=logging.INFO,
        )

    logging.debug(msg=f"party_lookup out: {result}")
    return jsonify(result)


@app.route("/gtin/<gtin>")
def lookup_gtin(gtin=None):
    logging.debug(msg=f"gtin_lookup  in: {gtin}")

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

    logging.debug(msg=f"gtin_lookup out: {str(valid_gtin)}")
    return jsonify({"gtin": str(valid_gtin)})


@app.route("/tuteur/<movimiento>/<file>")
def lookup_event(movimiento=None, file=None):
    logging.debug(f"lookup_event  in: {movimiento} {file}")

    result = event_lookup(movimiento, file)

    logging.debug(f"lookup_event out: {result}")
    return jsonify(result)


@app.route("/serialProcessor/<string:serial_w_id>")
def serial_processor(serial_w_id):
    logging.debug(f"serial_processor  in: {serial_w_id}")

    actor = request.args.get("actor", type=str)
    batch = request.args.get("batch", type=str)
    lab = request.args.get("lab", type=str)
    gtin = request.args.get("gtin", type=str)
    result = symbol_processor.parse(serial_w_id, actor, batch, lab, gtin)

    logging.debug(f"serial_processor out: {result}")
    return jsonify(result)


class ActorsConverter(PathConverter):
    regex = r"7793397000007|7798175150202"
    part_isolating = False
    # weight = 199


class EverythingConverter(PathConverter):
    regex = r".*?"
    part_isolating = False


app.url_map.converters["actors"] = ActorsConverter
app.url_map.converters["everything"] = EverythingConverter


@app.route("/<actors:actor>/<int:row>/<everything:encoded_path>")  # , merge_slashes=True)
def calculate_rowid(actor, row, encoded_path):
    logging.debug(msg=f"row_uuid  in: {actor} {row} {encoded_path}")

    result = row_uuid.calculate(actor=actor, row=row, encoded_path=encoded_path)

    logging.debug(msg=f"row_uuid out: {result}")
    return result, 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 12010)))
