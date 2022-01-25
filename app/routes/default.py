import os
import time
import werkzeug
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import session
from flask import render_template
from flask import current_app
from flask import abort
from flask import json
from app.utils import render_markdown
from datetime import datetime
from base64 import b64encode
import jinja2

bp = Blueprint("index", __name__)


@bp.route("/")
@bp.route("/<path:path>")
def handle_posts(*args, **kwgs):
    if request.path in current_app.pages.registered:
        return render_markdown("page.html", session=session)

    abort(404)


@bp.route("/techstack")
def techstack(*args, **kwgs):

    return render_markdown(
        "page.html", file="techstack.md", session=session, time=datetime.now()
    )

    abort(404)


@bp.before_request
def before_request():
    if session.get("expiry"):
        if time.time() > session.get("expiry"):
            # @url_param {string} code
            # @url_param {string} status
            UAA_TOKEN_URI = current_app.config["UAA_TOKEN_URI"]

            data = {
                "grant_type": "refresh_token",
                "refresh_token": session.get("refresh_token"),
                "client_id": current_app.config["CLIENT_ID"],
                "client_secret": current_app.config["CLIENT_SECRET"],
            }

            response = requests.post(UAA_TOKEN_URI, data=data).json()

            token = response["access_token"]
            header = jwt.get_unverified_header(token)

            session["claims"] = jwt.decode(
                token, header["alg"], options={"verify_signature": False}
            )
            session["expiry"] = time.time() + (response["expires_in"] * 1000)
            session["refresh_token"] = response["refresh_token"]
            session["authenticated"] = True


@bp.after_request
def after_request(response):
    return response


def handle_exception(e):
    print(dir(e))
    try:
        e.code
    except Exception:
        e.code = 500
        e.name = "Internal Server Error: {}".format(type(e).__name__)
        e.description = "{}".format(b64encode(str(e).encode("ascii")).decode("utf-8"))
    return render_template("error.html", error=e)
