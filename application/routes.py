from application import app
from flask import Response, request

# Mock document management system.
# A document will be some metadata, plus images of each of the pages of the document
# Images will be stored in whatever format they're sent (in legacy world: TIFF & JPEG)


@app.route('/', methods=["GET"])
def index():
    return Response(status=200)


@app.route('/document', methods=["POST"])
def create_documents():
    # create an empty document meta-entry
    pass


@app.route('/document/<int:doc_no>', methods=["GET"])
def get_document(doc_no):
    # retrieve the meta-entry, including URIs of the images
    pass


@app.route('/document/<int:doc_no>', methods=["PUT"])
def change_document(doc_no):
    # set new meta-data for a document
    pass


@app.route('/document/<int:doc_no>', methods=["DELETE"])
def delete_document(doc_no):
    # delete an entire document and its associated images
    pass


@app.route('/document/<int:doc_no>/image/<int:index>', methods=["GET"])
def get_image(doc_no, index):
    # get an image
    pass


@app.route('/document/<int:doc_no>/image/<int:index>', methods=["PUT"])
def put_image(doc_no, index):
    # set or replace an image
    pass


@app.route('/document/<int:doc_no>/image/<int:index>', methods=["DELETE"])
def delete_image(doc_no, index):
    # delete an image from the document
    pass

