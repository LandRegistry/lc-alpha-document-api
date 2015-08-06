from application import app
from flask import Response, request


@app.route('/', methods=["GET"])
def index():
    return Response(status=200)

