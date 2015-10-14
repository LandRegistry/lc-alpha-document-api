import pytest
from unittest import mock
from application.routes import app
import json
import os
import hashlib

test_metadata = '{"test": "data"}'

mock_create_document = {
    'return_value': mock.Mock(**{'cursor.return_value': mock.Mock(**{'fetchone.return_value': [23]})})
}

mock_fetch_empty_array = {
    'return_value': mock.Mock(**{'cursor.return_value': mock.Mock(**{'fetchall.return_value': []})})
}

mock_change_document = {
    'return_value': mock.Mock(**{'cursor.return_value': mock.Mock(rowcount=1)})
}

mock_change_document_no_row = {
    'return_value': mock.Mock(**{'cursor.return_value': mock.Mock(rowcount=0)})
}

mock_documents_row = [[{"test": "data"}, ["img13_1.jpeg", "img13_2.jpeg", "img13_3.jpeg"]]]

mock_get_metadata = {
    'return_value': mock.Mock(**{
        'cursor.return_value': mock.Mock(**{'fetchall.return_value': mock_documents_row})
    })
}

mock_images_row = [[["img30_1.jpeg", "img33_1.jpeg", "img36_1.jpeg"]]]

mock_get_imagepaths = {
    'return_value': mock.Mock(**{
        'cursor.return_value': mock.Mock(**{'fetchall.return_value': mock_images_row})
    })
}

mock_images_row_2 = [[["img17_1.jpeg", "img17_2.jpeg", "img17_3.jpeg"]]]

mock_get_imagepaths_2 = {
    'return_value': mock.Mock(**{
        'cursor.return_value': mock.Mock(**{'fetchall.return_value': mock_images_row_2})
    })
}


class TestImageStore:
    def setup_method(self, method):
        self.app = app.test_client()

    def test_health_check(self):
        response = self.app.get("/")
        assert response.status_code == 200

    @mock.patch('psycopg2.connect', **mock_create_document)
    def test_create_document(self, mock_connect):
        response = self.app.post('/document', data=test_metadata, headers={'Content-Type': 'application/json'})
        data = json.loads(response.data.decode('utf-8'))
        assert response.status_code == 201
        assert data['id'] == 23

    @mock.patch('psycopg2.connect', **mock_change_document)
    def test_change_metadata(self, mock_connect):
        new_data = '{"some": "test", "metadata": "fields"}'
        response = self.app.put('/document/23', data=new_data, headers={'Content-Type': 'application/json'})
        assert response.status_code == 200

    @mock.patch('psycopg2.connect', **mock_change_document_no_row)
    def test_change_metadata_not_found(self, mock_connect):
        new_data = '{"some": "test", "metadata": "fields"}'
        response = self.app.put('/document/23', data=new_data, headers={'Content-Type': 'application/json'})
        assert response.status_code == 404

    @mock.patch('psycopg2.connect', **mock_get_metadata)
    def test_retrieve_metadata(self, mock_connect):
        response = self.app.get('/document/17')
        data = json.loads(response.data.decode('utf-8'))
        assert response.status_code == 200
        assert data['test'] == 'data'
        assert len(data['images']) == 3
        assert data['images'][2] == "/document/17/image/3"

    @mock.patch('psycopg2.connect', **mock_get_imagepaths)
    def test_add_image_to_document(self, mock_connect):
        response = self.app.post('/document/9/image', data='ZZZZZZ', headers={'Content-Type': 'image/tiff'})
        assert os.path.isfile("/home/vagrant/img9_4.tiff")
        os.remove("/home/vagrant/img9_4.tiff")
        data = json.loads(response.data.decode('utf-8'))
        assert len(data) == 4
        assert data[3] == 'img9_4.tiff'

    @mock.patch('psycopg2.connect', **mock_get_imagepaths)
    def test_extension_type(self, mok):
        response = self.app.post('/document/9/image', data='some jpeg file', headers={'Content-Type': 'image/jpeg'})
        assert os.path.isfile("/home/vagrant/img9_5.jpeg")
        os.remove("/home/vagrant/img9_5.jpeg")

        response = self.app.post('/document/9/image', data='some pdf file', headers={'Content-Type': 'application/pdf'})
        assert os.path.isfile("/home/vagrant/img9_6.pdf")
        os.remove("/home/vagrant/img9_6.pdf")

    def test_header_contains_json(self):
        # create document api
        response = self.app.post('/document', data=test_metadata, headers={'Content-Type': 'application/xml'})
        assert response.status_code == 415
        # change document api
        response = self.app.put('/document/41', data=test_metadata, headers={'Content-Type': 'application/xml'})
        assert response.status_code == 415
        # add document api
        response = self.app.post('/document/9/image', data=test_metadata, headers={'Content-Type': 'application/xml'})
        assert response.status_code == 415
        # replace image api
        response = self.app.put('/document/41/image/2', data=test_metadata, headers={'Content-Type': 'application/xml'})
        assert response.status_code == 415

    @mock.patch('psycopg2.connect', **mock_get_imagepaths_2)
    def test_replace_image(self, mock_connect):
        response = self.app.put('/document/17/image/2', data='ZZZZZ', headers={'Content-Type': 'image/tiff'})
        data = json.loads(response.data.decode('utf-8'))
        assert len(data) == 3
        assert data[1] == 'img17_2.tiff'
        assert os.path.isfile("/home/vagrant/img17_2.tiff")
        os.remove("/home/vagrant/img17_2.tiff")

    @mock.patch('psycopg2.connect', **mock_fetch_empty_array)
    def test_retrieve_metadata_not_found(self, mock_connect):
        response = self.app.get('/document/17')
        assert response.status_code == 404

    @mock.patch('psycopg2.connect', **mock_get_imagepaths)
    def test_retrieve_image(self, mock_connect):
        response = self.app.get('/document/9/image/2')
        sha1 = hashlib.sha1(response.data).hexdigest()
        assert response.status_code == 200
        assert sha1 == '2bdc21774ffe3ce93e262f896fa8b1877e01d62b'  # use sha1sum <file>

    @mock.patch('psycopg2.connect', **mock_get_imagepaths)
    def test_retrieve_image_adjust_contrast(self, mock_connect):
        response = self.app.get('/document/9/image/2?contrast=50')
        sha1 = hashlib.sha1(response.data).hexdigest()
        assert response.status_code == 200
        assert sha1 == 'b20b72a7f9dfcbe1fa19c3a3f4d1db55603463e6'

    @mock.patch('psycopg2.connect', **mock_fetch_empty_array)
    def test_retrieve_image_not_found(self, mock_connect):
        response = self.app.get('/document/9/image/2')
        assert response.status_code == 404

    @mock.patch('psycopg2.connect', **mock_get_imagepaths_2)
    @mock.patch('os.remove')
    def test_remove_image(self, mock_remove, mock_connect):
        response = self.app.delete('/document/17/image/2')
        assert mock_remove.call_args_list[0][0][0] == '/home/vagrant/img17_2.tiff'
        assert response.status_code == 200

    @mock.patch('psycopg2.connect', **mock_get_imagepaths_2)
    @mock.patch('os.remove')
    def test_remove_document(self, mock_remove, mock_connect):
        response = self.app.delete('/document/17')
        assert mock_remove.call_args_list[0][0][0] == '/home/vagrant/img17_1.jpeg'
        assert mock_remove.call_args_list[1][0][0] == '/home/vagrant/img17_3.jpeg'
        assert response.status_code == 200

    @mock.patch('psycopg2.connect', **mock_get_imagepaths)
    def test_recognise_form(self, mock_connect):
        response = self.app.get('/document/9/image/2/formtype')
        assert response.status_code == 200

    @mock.patch('psycopg2.connect', **mock_get_imagepaths)
    def test_recognise_form_no_image(self, mock_connect):
        response = self.app.get('/document/9/image/7/formtype')
        assert response.status_code == 404
