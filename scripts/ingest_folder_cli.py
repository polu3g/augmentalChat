import os
import requests

API_URL = "http://localhost:8000/ingest-folder"
FOLDER = "data/"

files = [
    ('files', (f, open(os.path.join(FOLDER, f), 'rb')))
    for f in os.listdir(FOLDER)
    if f.endswith(('.pdf', '.txt', '.csv'))
]

response = requests.post(API_URL, files=files)
print(response.json())
