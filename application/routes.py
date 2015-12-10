from application import app
from flask import Response, request, url_for, send_from_directory, send_file, redirect
import psycopg2
import psycopg2.extras
import json
import logging
import os
import requests
from io import BytesIO
from PIL import Image
from PIL import ImageEnhance
from application.ocr import recognise
# Mock document management system.
# A document will be some metadata, plus images of each of the pages of the document
# Images will be stored in whatever format they're sent (in legacy world: TIFF & JPEG)


def connect(cursor_factory=None):
    connection = psycopg2.connect("dbname='{}' user='{}' host='{}' password='{}'".format(
        app.config['DATABASE_NAME'], app.config['DATABASE_USER'], app.config['DATABASE_HOST'],
        app.config['DATABASE_PASSWORD']))

    print(psycopg2.connect)
    print(connection)
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
        for item in enumerate(rows[0][1]):
            data["images"].append(url_for('get_image', doc_no=doc_no, image_index=item[0] + 1))

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


def get_mimetype(extension):
    if extension == '.tiff':
        return "image/tiff"
    elif extension == '.jpeg':
        return 'image/jpeg'
    elif extension == '.pdf':
        return 'application/pdf'
    else:
        return None


def check_legacy_health():
    return requests.get(app.config['LEGACY_ADAPTER_URI'] + '/health')


application_dependencies = [
    {
        "name": "legacy-adapter",
        "check": check_legacy_health
    }
]


@app.route('/', methods=["GET"])
def index():
    return Response(status=200)


@app.route('/health', methods=['GET'])
def health():
    result = {
        'status': 'OK',
        'dependencies': {}
    }

    status = 200
    for dependency in application_dependencies:
        response = dependency["check"]()
        if response.status_code != 200:
            status = 500
        result['dependencies'][dependency['name']] = str(response.status_code) + ' ' + response.reason
        data = json.loads(response.content.decode('utf-8'))
        for key in data['dependencies']:
            result['dependencies'][key] = data['dependencies'][key]

    return Response(json.dumps(result), status=status, mimetype='application/json')


@app.route('/forms', methods=["POST"])
def create_documents():
    # create an empty document meta-entry
    if request.headers['Content-Type'] != "application/json":
        logging.error('Content-Type is not JSON')
        return Response(status=415)

    data = request.get_json(force=True)
    cursor = connect()
    print(cursor)
    cursor.execute("insert into documents (metadata, image_paths) values ( %(meta)s, %(paths)s ) returning id",
                   {
                       "meta": json.dumps(data),
                       "paths": "[]"
                   })
    res = cursor.fetchone()
    print(res)
    doc_id = res[0]
    complete(cursor)
    return Response(json.dumps({"id": doc_id}), status=201)


@app.route('/forms/<int:doc_no>', methods=["GET"])
def get_document(doc_no):
    # retrieve the meta-entry, including URIs of the images
    data = get_metadata(doc_no)
    if data is None:
        return Response(status=404)
    else:
        return Response(json.dumps(data, ensure_ascii=False), status=200)


@app.route('/forms/<int:doc_no>', methods=["PUT"])
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
    print("RC")
    print(rowcount)
    if rowcount == 0:
        return Response(status=404)

    return Response(status=200)


@app.route('/forms/<int:doc_no>', methods=["DELETE"])
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


@app.route('/forms', methods=['GET'])
def get_all_documents():
    cursor = connect()
    cursor.execute('select id, metadata, image_paths from documents')
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "metadata": row[1],
            "images_paths": row[2]
        })
    return Response(json.dumps(result), status=200)


@app.route('/forms/<int:doc_no>/images/<int:image_index>', methods=["GET"])
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


@app.route('/forms/<int:doc_no>/images', methods=['POST'])
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


@app.route('/forms/<int:doc_no>/images/<int:image_index>', methods=["PUT"])
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
    if images is None or image_index < 1 or image_index >= len(images):
        return Response(status=404)
    images[image_index - 1] = os.path.basename(filename)
    set_imagepaths(doc_no, images)
    return Response(json.dumps(images), status=201)


@app.route('/forms/<int:doc_no>/images/<int:image_index>', methods=["DELETE"])
def delete_image(doc_no, image_index):
    # delete an image from the document
    images = get_imagepaths(doc_no)
    if images is None or image_index < 1 or image_index >= len(images):
        return Response(status=404)

    filename = os.path.join(app.config['IMAGE_DIRECTORY'], images[image_index - 1])
    os.remove(filename)
    del images[image_index - 1]
    set_imagepaths(doc_no, images)
    return Response(json.dumps(images), status=200)


@app.route('/forms/<int:doc_no>/images/<int:image_index>/formtype', methods=["GET"])
def recognise_form(doc_no, image_index):
    images = get_imagepaths(doc_no)
    print(images)
    if images is None or image_index < 1 or image_index > len(images):
        return Response(status=404)

    filename = images[image_index - 1]
    filename = os.path.join(app.config['IMAGE_DIRECTORY'], filename)
    formtype = recognise(filename)

    return Response(json.dumps({"type": formtype}), status=200, mimetype='application/json')


@app.route('/archive/<date>/<regn_no>/<image_index>', methods=['GET'])
def get_from_archive(date, regn_no, image_index):
    uri = "{}/images/{}/{}/{}".format(app.config['LEGACY_ADAPTER_URI'], date, regn_no, image_index)
    return redirect(uri)


@app.route('/archive/<date>/<regn_no>', methods=['POST'])
def archive_document(date, regn_no):
    data = request.get_json(force=True)
    doc_id = data['document_id']

    # need to post each image...
    images = get_imagepaths(doc_id)
    img_index = 0
    responses = []
    all_ok = True
    for image in images:
        img_index += 1
        fn = os.path.join(app.config['IMAGE_DIRECTORY'], image)
        file = open(fn, 'rb')
        mimetype = get_mimetype(os.path.splitext(image)[-1])
        uri = "{}/images/{}/{}/{}".format(app.config['LEGACY_ADAPTER_URI'], date, regn_no, img_index)
        response = requests.put(uri, data=file, headers={'Content-Type': mimetype})
        if response.status_code != 201:
            all_ok = False
        responses.append({
            'uri': uri,
            'result': response.status_code
        })

    if all_ok:
        return Response(json.dumps(responses), status=200, mimetype='application/json')
    else:
        return Response(json.dumps(responses), status=500, mimetype='application/json')


@app.route('/archive/<date>/<regn_no>/<image_index>', methods=['PUT'])
def replace_in_archive(date, regn_no, image_index):
    uri = "{}/images/{}/{}/{}".format(app.config['LEGACY_ADAPTER_URI'], date, regn_no, image_index)
    header = request.headers['Content-Type']
    data = request.data
    response = requests.put(uri, data=data, headers={'Content-Type': header})
    return Response(status=response.status_code)


@app.route('/archive/<date>/<regn_no>/<image_index>', methods=['DELETE'])
def delete_from_archive(date, regn_no, image_index):
    uri = "{}/images/{}/{}/{}".format(app.config['LEGACY_ADAPTER_URI'], date, regn_no, image_index)
    response = requests.delete(uri)
    return Response(status=response.status_code)


# ============== DEV ROUTES ================

@app.route('/forms', methods=['DELETE'])
def delete():
    if not app.config['ALLOW_DEV_ROUTES']:
        return Response(status=403)
    cursor = connect()
    cursor.execute("DELETE FROM documents")
    complete(cursor)
    return Response(status=200, mimetype='application/json')


@app.route('/forms/bulk', methods=['POST'])
def bulk_load():
    if not app.config['ALLOW_DEV_ROUTES']:
        return Response(status=403)

    data = request.get_json(force=True)
    cursor = connect()
    for item in data:
        cursor.execute("INSERT INTO documents (id, metadata, image_paths) "
                       "VALUES ( %(id)s, %(meta)s, %(image)s )",
                       {
                           'id': item['id'],
                           'meta': json.dumps(item['metadata']),
                           'image': json.dumps(item['image_paths'])
                       })
    cursor.execute("SELECT setval('documents_id_seq', (SELECT MAX(id) FROM documents)+1);")

    complete(cursor)
    return Response(status=200, mimetype='application/json')