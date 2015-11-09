import requests
import os
import json
import shutil

standard_data = [
    {"metadata": {}, "id": 2, "image_paths": ["img2_1.jpeg"]},
    {"metadata": {}, "id": 3, "image_paths": ["img3_1.jpeg"]},
    {"metadata": {}, "id": 4, "image_paths": ["img4_1.jpeg"]},
    {"metadata": {}, "id": 5, "image_paths": ["img5_1.jpeg"]},
    {"metadata": {}, "id": 6, "image_paths": ["img6_1.jpeg"]},
    {"metadata": {}, "id": 7, "image_paths": ["img7_1.jpeg"]},
    {"metadata": {}, "id": 8, "image_paths": ["img8_1.jpeg"]},
    {"metadata": {}, "id": 9, "image_paths": ["img9_1.jpeg"]},
    {"metadata": {}, "id": 10, "image_paths": ["img10_1.jpeg"]},
    {"metadata": {}, "id": 11, "image_paths": ["img11_1.jpeg"]},
    {"metadata": {}, "id": 12, "image_paths": ["img12_1.jpeg"]},
    {"metadata": {}, "id": 13, "image_paths": ["img13_1.jpeg"]},
    {"metadata": {}, "id": 14, "image_paths": ["img14_1.jpeg"]},
    {"metadata": {}, "id": 15, "image_paths": ["img15_1.jpeg"]},
    {"metadata": {}, "id": 16, "image_paths": ["img16_1.jpeg"]},
    {"metadata": {}, "id": 17, "image_paths": ["img17_1.jpeg"]},
    {"metadata": {}, "id": 18, "image_paths": ["img18_1.jpeg"]},
    {"metadata": {}, "id": 19, "image_paths": ["img19_1.jpeg"]},
    {"metadata": {}, "id": 20, "image_paths": ["img20_1.jpeg"]},
    {"metadata": {}, "id": 21, "image_paths": ["img21_1.jpeg"]},
    {"metadata": {}, "id": 22, "image_paths": ["img22_1.jpeg"]},
    {"metadata": {}, "id": 23, "image_paths": ["img23_1.jpeg"]},
    {"metadata": {}, "id": 24, "image_paths": ["img24_1.jpeg"]},
    {"metadata": {}, "id": 25, "image_paths": ["img25_1.jpeg"]},
    {"metadata": {}, "id": 26, "image_paths": ["img26_1.jpeg"]},
    {"metadata": {}, "id": 27, "image_paths": ["img27_1.jpeg"]},
    {"metadata": {}, "id": 28, "image_paths": ["img28_1.jpeg"]},
    {"metadata": {}, "id": 29, "image_paths": ["img29_1.jpeg"]},
    {"metadata": {}, "id": 30, "image_paths": ["img30_1.jpeg"]},
    {"metadata": {}, "id": 31, "image_paths": ["img31_1.jpeg", "img31_2.jpeg"]},
    {"metadata": {}, "id": 32, "image_paths": ["img32_1.jpeg"]},
    {"metadata": {}, "id": 33, "image_paths": ["img33_1.jpeg", "img33_2.jpeg"]},
    {"metadata": {}, "id": 34, "image_paths": ["img34_1.jpeg"]},
    {"metadata": {}, "id": 35, "image_paths": ["img35_1.jpeg", "img35_2.jpeg"]},
    {"metadata": {}, "id": 36, "image_paths": ["img36_1.jpeg"]},
    {"metadata": {}, "id": 37, "image_paths": ["img37_1.jpeg", "img37_2.jpeg"]},
    {"metadata": {}, "id": 38, "image_paths": ["img38_1.jpeg"]},
    {"metadata": {}, "id": 39, "image_paths": ["img39_1.jpeg", "img39_2.jpeg"]},
    {"metadata": {}, "id": 40, "image_paths": ["img40_1.jpeg"]},
    {"metadata": {}, "id": 41, "image_paths": ["img41_1.jpeg", "img41_2.jpeg"]},
    {"metadata": {}, "id": 42, "image_paths": ["img42_1.jpeg"]},
    {"metadata": {}, "id": 43, "image_paths": ["img43_1.jpeg"]},
    {"metadata": {}, "id": 44, "image_paths": ["img44_1.jpeg"]},
    {"metadata": {}, "id": 45, "image_paths": ["img45_1.jpeg"]},
    {"metadata": {}, "id": 46, "image_paths": ["img46_1.jpeg"]},
    {"metadata": {}, "id": 47, "image_paths": ["img47_1.jpeg"]},
    {"metadata": {}, "id": 48, "image_paths": ["img48_1.jpeg"]},
    {"metadata": {}, "id": 49, "image_paths": ["img49_1.jpeg"]},
    {"metadata": {}, "id": 50, "image_paths": ["img50_1.jpeg", "img50_2.jpeg"]},
    {"metadata": {}, "id": 51, "image_paths": ["img51_1.jpeg"]},
    {"metadata": {}, "id": 52, "image_paths": ["img52_1.jpeg"]},
    {"metadata": {}, "id": 53, "image_paths": ["img53_1.jpeg"]},
    {"metadata": {}, "id": 54, "image_paths": ["img54_1.jpeg"]},
    {"metadata": {}, "id": 55, "image_paths": ["img55_1.jpeg"]},
    {"metadata": {}, "id": 56, "image_paths": ["img56_1.jpeg", "img56_2.jpeg"]},
    {"metadata": {}, "id": 57, "image_paths": ["img57_1.jpeg"]},
    {"metadata": {}, "id": 58, "image_paths": ["img58_1.jpeg"]},
    {"metadata": {}, "id": 59, "image_paths": ["img59_1.jpeg"]},
    {"metadata": {}, "id": 60, "image_paths": ["img60_1.jpeg"]},
    {"metadata": {}, "id": 61, "image_paths": ["img61_1.jpeg"]},
    {"metadata": {}, "id": 62, "image_paths": ["img62_1.jpeg"]},
    {"metadata": {}, "id": 63, "image_paths": ["img63_1.jpeg"]},
    {"metadata": {}, "id": 64, "image_paths": ["img64_1.jpeg"]},
    {"metadata": {}, "id": 65, "image_paths": ["img65_1.jpeg"]},
    {"metadata": {}, "id": 66, "image_paths": ["img66_1.jpeg"]}
]

url = os.getenv('DOCUMENT_API_URI', 'http://localhost:5014')
response = requests.post(url + '/documents/bulk',
                         data=json.dumps(standard_data),
                         headers={'Content-Type': 'application/json'})
print(response.status_code)

here = os.path.dirname(os.path.realpath(__file__))
for item in standard_data:
    for image in item['image_paths']:
        shutil.copy(here + '/images/' + image, '/home/vagrant/' + image)
