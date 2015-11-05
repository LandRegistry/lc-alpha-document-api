import os
import requests


url = os.getenv('DOCUMENT_API_URI', 'http://localhost:5014')
response = requests.delete(url + '/documents')
