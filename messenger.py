from fbchat import Client
from fbchat.models import *
from database import Database
import tempfile

class Messenger(object):
    def __init__(self):
        self.db = Database()
        self.client = self.__get_client__()

    def __get_client__(self):
        configurations = self.db.get_fb_configurations()
        session = configurations.get('session')
        client = Client(configurations.get('email'), configurations.get('password'), session_cookies=session)
        configurations["session"] = client.getSession()
        self.db.set_fb_configurations(configurations)
        return client

    def __auth_group__(self, group_id):
        group = self.db.get_fb_group(group_id)
        if group is None or not group.get('is_active'): raise Exception("group_id not allowed") 

    def get_group(self, group_id):
        self.__auth_group__(group_id)
        return self.db.get_fb_group(group_id)

    def get_report(self, report_id):
        return self.db.get_fb_report(report_id)

    def create_report(self, group_id, report_id):
        return self.db.create_fb_report(group_id, report_id)

    def send(self, group_id, message):
        self.__auth_group__(group_id)
        return self.client.send(Message(text=message), thread_id=group_id, thread_type=ThreadType.GROUP)

    def send_image(self, group_id, infographic):
        if infographic is None: return None
        self.__auth_group__(group_id)
        temp = tempfile.NamedTemporaryFile(delete=False)
        try:
            temp.name = f'{temp.name}.png'
            infographic.image.save(temp.name)
            mid = self.client.sendLocalImage(temp.name, message=Message(text=infographic.description), thread_id=group_id, thread_type=ThreadType.GROUP)
            return mid
        finally:
            temp.close() 

if __name__ == "__main__":
    pass