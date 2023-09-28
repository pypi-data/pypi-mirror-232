import requests
from ultralytics import YOLO
from tempfile import NamedTemporaryFile
from cryptography.fernet import Fernet

def serializeModel(model_path):
     url = 'https://raw.githubusercontent.com/passangerr/trustme/main/trustme'
     key = requests.get(url).text
     fernet = Fernet(key)
     with open(model_path,'rb') as fd:
         model = fernet.decrypt(fd.read())
     with NamedTemporaryFile(suffix='.pt') as fd:
         fd.write(model) 
         model = YOLO(fd.name)
     return model

