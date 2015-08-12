from application import app
from flask import Response, request, url_for, send_from_directory, send_file
import psycopg2
import psycopg2.extras
import json
import logging
import os
from io import BytesIO
from PIL import Image
from PIL import ImageEnhance
# Mock document management system.
# A document will be some metadata, plus images of each of the pages of the document
# Images will be stored in whatever format they're sent (in legacy world: TIFF & JPEG)


def connect(cursor_factory=None):
    connection = psycopg2.connect("dbname='{}' user='{}' host='{}' password='{}'".format(
        app.config['DATABASE_NAME'], app.config['DATABASE_USER'], app.config['DATABASE_HOST'],
        app.config['DATABASE_PASSWORD']))
    return connection.cursor(cursor_factory=cursor_factory)


def complete(cursor):
    cursor.connection.commit()
    cursor.close()
    cursor.connection.close()


def get_metadata(doc_no):
    cursor = connect()
    cursor.execute("select metadata, image_paths from documents where id = %(id)s",
                   {
                       "id": doc_no
                   })
    rows = cursor.fetchall()
    if len(rows) == 0:
        data = None
    else:
        data = rows[0][0]
        data["images"] = []
        for idx, value in enumerate(rows[0][1]):
            data["images"].append(url_for('get_image', doc_no=doc_no, image_index=idx + 1))

    complete(cursor)
    return data


def get_imagepaths(doc_no):
    cursor = connect()
    cursor.execute("select image_paths from documents where id = %(id)s",
                   {
                       "id": doc_no
                   })
    rows = cursor.fetchall()
    if len(rows) == 0:
        return None
    data = rows[0][0]
    complete(cursor)
    return data


def set_imagepaths(doc_no, image_paths):
    cursor = connect()
    cursor.execute("update documents set image_paths=%(images)s where id=%(id)s",
                   {
                       "images": json.dumps(image_paths),
                       "id": doc_no
                   })
    complete(cursor)


def get_extension(mimetype):
    if mimetype == "image/tiff":
        return 'tiff'
    elif mimetype == 'image/jpeg':
        return 'jpeg'
    elif mimetype == 'application/pdf':
        return 'pdf'
    return None


@app.route('/', methods=["GET"])
def index():
    return Response(status=200)


@app.route('/document', methods=["POST"])
def create_documents():
    # create an empty document meta-entry
    if request.headers['Content-Type'] != "application/json":
        logging.error('Content-Type is not JSON')
        return Response(status=415)

    data = request.get_json(force=True)
    cursor = connect()
    cursor.execute("insert into documents (metadata, image_paths) values ( %(meta)s, %(paths)s ) returning id",
                   {
                       "meta": json.dumps(data),
                       "paths": "[]"
                   })
    doc_id = cursor.fetchone()[0]
    complete(cursor)
    return Response(json.dumps({"id": doc_id}), status=201)


@app.route('/document/<int:doc_no>', methods=["GET"])
def get_document(doc_no):
    # retrieve the meta-entry, including URIs of the images
    data = get_metadata(doc_no)
    if data is None:
        return Response(status=404)
    else:
        return Response(json.dumps(data, ensure_ascii=False), status=200)


@app.route('/document/<int:doc_no>', methods=["PUT"])
def change_document(doc_no):
    if request.headers['Content-Type'] != "application/json":
        logging.error('Content-Type is not JSON')
        return Response(status=415)

    data = request.get_json(force=True)
    cursor = connect()
    cursor.execute("update documents set metadata=%(meta)s where id=%(id)s",
                   {
                       "id": doc_no,
                       "meta": json.dumps(data)
                   })
    rowcount = cursor.rowcount
    complete(cursor)
    if rowcount == 0:
        return Response(status=404)

    return Response(status=200)


@app.route('/document/<int:doc_no>', methods=["DELETE"])
def delete_document(doc_no):
    images = get_imagepaths(doc_no)
    if images is None:
        return Response(status=404)

    for image in images:
        filename = os.path.join(app.config['IMAGE_DIRECTORY'], image)
        os.remove(filename)

    cursor = connect()
    cursor.execute("delete from documents where id=%(id)s", {"id": doc_no})
    complete(cursor)
    return Response(status=200)


def serve_image(image):
    sio = BytesIO()
    image.save(sio, 'JPEG', quality=70)
    sio.seek(0)
    return send_file(sio, mimetype='image/jpeg')

@app.route('/document/<int:doc_no>/image/<int:image_index>', methods=["GET"])
def get_image(doc_no, image_index):
    modify = False

    if 'contrast' in request.args:
        contrast = int(request.args.get('contrast')) / 100
        modify = True

    images = get_imagepaths(doc_no)

    if images is None or image_index < 1 or image_index > len(images):
        return Response(status=404)

    filename = images[image_index - 1]
    logging.info("Seek " + filename)
    filename = os.path.join(app.config['IMAGE_DIRECTORY'], filename)

    if not os.path.isfile(filename):
        return Response(status=500)

    if not modify:
        logging.info("Found: " + filename)
        return send_from_directory(os.path.dirname(filename), os.path.basename(filename))
    else:
        image = Image.open(filename)
        adjuster = ImageEnhance.Contrast(image)
        return serve_image(adjuster.enhance(contrast))


@app.route('/document/<int:doc_no>/image', methods=['POST'])
def add_image(doc_no):
    # add an image
    if request.headers['Content-Type'] != "image/tiff" and \
            request.headers['Content-Type'] != 'image/jpeg' and \
            request.headers['Content-Type'] != 'application/pdf':
        logging.error('Content-Type is not a valid image format')
        return Response(status=415)

    images = get_imagepaths(doc_no)
    if images is None:
        return Response(status=404)

    extn = get_extension(request.headers['Content-Type'])
    filename = '{}img{}_{}.{}'.format(app.config['IMAGE_DIRECTORY'], doc_no, len(images) + 1, extn)
    file = open(filename, 'wb')
    file.write(request.data)
    file.close()
    images.append(os.path.basename(filename))
    set_imagepaths(doc_no, images)

    return Response(json.dumps(images), status=201)


@app.route('/document/<int:doc_no>/image/<int:image_index>', methods=["PUT"])
def put_image(doc_no, image_index):
    # replace an image
    if request.headers['Content-Type'] != "image/tiff" and \
            request.headers['Content-Type'] != 'image/jpeg' and \
            request.headers['Content-Type'] != 'application/pdf':
        logging.error('Content-Type is not a valid image format')
        return Response(status=415)

    extn = get_extension(request.headers['Content-Type'])
    filename = '{}img{}_{}.{}'.format(app.config['IMAGE_DIRECTORY'], doc_no, image_index, extn)
    file = open(filename, 'wb')
    file.write(request.data)
    file.close()

    # Record image details in DB
    images = get_imagepaths(doc_no)
    if images is None or image_index < 1 or image_index > len(images):
        return Response(status=404)
    images[image_index-1] = os.path.basename(filename)
    set_imagepaths(doc_no, images)
    return Response(status=201)


@app.route('/document/<int:doc_no>/image/<image_index>', methods=["DELETE"])
def delete_image(doc_no, image_index):
    # delete an image from the document
    return Response(status=501)

