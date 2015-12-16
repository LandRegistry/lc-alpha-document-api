from application import app
from flask import Response, request, url_for, send_from_directory, send_file, redirect
import psycopg2
import psycopg2.extras
import json
import logging
import os
import requests
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
