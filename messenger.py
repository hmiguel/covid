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

    def send(self, group_id, message):
        self.__auth_group__(group_id)
        return self.client.send(Message(text=message), thread_id=group_id, thread_type=ThreadType.GROUP)

    def send_image(self, group_id, image, message = ""):
        self.__auth_group__(group_id)
        temp = tempfile.NamedTemporaryFile(delete=False)
        try:
            temp.name = f'{temp.name}.png'
            image.save(temp.name)
            mid = self.client.sendLocalImage(temp.name, message=Message(text=message), thread_id=group_id, thread_type=ThreadType.GROUP)
            return mid
        finally:
            temp.close() 

if __name__ == "__main__":
    from covid import Covid
    from models import Infographic
    messenger = Messenger()
    msg_id = messenger.send("2873403912742691", "test1")
    c = Covid()
    print('getting covid information....')
    i = c.get_country_situation('PT', 'summary', True)
    print('sending message....')
    msg_id = messenger.send_image("683207628420443", i.image, i.description)