from database import Database
from covid import Source
import sys, utils

class Bot(object):
    def __init__(self, app, key):
        self.db = Database()
        self.bot = self._get_bot_instance(app, key)

    def _get_bot_instance(self, app, key):
        db = self.db.get_bot(app.lower())
        if db is None or db.get('key') != key: return None
        instance = getattr(sys.modules[__name__], app.title())
        return instance() if instance else None

class Whatsapp(object):
    def process(self, request, messenger):
        content = request.values
        if int(content.get('NumMedia', 0)) != 1: return ('', 202) 
        url, media = content.get('MediaUrl0'), content.get('MediaContentType0')
        if media != "application/pdf": return ('', 202) 
        source = Source()
        infographic = source.get_pdf_infographic(url = url)
        # get messenger groups
        groups = messenger.get_all_groups()
        groups = { g.key.id_or_name : utils.get_report_id(g.key.id_or_name, 'PT', 'summary', infographic.datetime) for g in groups if g }
        groups = { key : groups[key] for key in groups if not messenger.get_report(groups[key]) }
        mids = []
        for group_id in groups:
            mid = messenger.send_image(group_id, infographic) if infographic else messenger.send(group_id, data.text)
            if mid: messenger.create_report(group_id, groups[group_id])
            mids.append(mid)
        return ('', 204) if [m for m in mids if m] else ('', 202)

class Messenger(object):
    def process(self, request):
        return ('', 200)  

class Twitter(object):
    def process(self, request):
        return ('', 200)

if __name__ == "__main__":
    pass