import hashlib, base64, io, requests
from PIL import Image

def get_url_image(url):
    img = Image.open(requests.get(url, stream = True).raw)
    return img

def get_base64(string):
    return base64.urlsafe_b64encode(string.encode('utf-8')).decode('utf-8')

def get_id(string):  
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()

if __name__ == "__main__":
    pass