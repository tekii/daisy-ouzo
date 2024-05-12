import os
import logging

# from contextvars import ContextVar
# from werkzeug.local import LocalProxy
from flask import Flask, request, abort, jsonify
from party_catalog import *

app = Flask(__name__)
catalog = ThePartyCatalog()


@app.errorhandler(401)
def unauthorized(e):
    error = str(e)
    logging.debug(error)
    return jsonify(error=error), 401


@app.route("/", methods=["GET"])
def home_get():

    some = catalog.lookup("x")
    text = ""
    resp = jsonify({"text": text})
    return resp


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

elif __name__ == "__test__":
    pass
