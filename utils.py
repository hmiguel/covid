import hashlib, base64, io, requests
from PIL import Image
import pytz
from datetime import date
from datetime import datetime

def get_url_image(url):
    img = Image.open(requests.get(url, stream = True).raw)
    return img

def get_base64(string):
    return base64.urlsafe_b64encode(string.encode('utf-8')).decode('utf-8')

def get_hash(string):  
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()

def get_datetime_midnight(dt):
    dt = dt if dt else datetime.utcnow()
    return datetime.combine(dt.today(), datetime.min.time())

def get_dt_utc_tz(dt):
    return dt.replace(tzinfo=pytz.timezone('UTC'))

def get_report_id(group_id, country, report, report_datetime):
    return get_hash(f'{group_id}{country.upper()}{report}{report_datetime.date().isoformat()}')

if __name__ == "__main__":
    pass