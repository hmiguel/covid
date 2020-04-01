import hashlib, base64, io, requests
from PIL import Image
import pytz
from datetime import date
from datetime import datetime

def get_url_image(url):
    r = requests.get(url, stream = True)
    img = Image.open(r.raw)
    img.datetime = datetime.strptime(r.headers.get('Document-Date'), "%Y%m%dT%H%M%S") or None
    return img

def get_increase_percent(cur, inc): 
    return round((inc)/((cur-inc)*1.0)*100.0,2)

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