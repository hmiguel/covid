from fbchat import Client
from fbchat.models import *
from database import Database

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

    def send(self, group_id, message):
        group = self.db.get_fb_group(group_id)
        if group is None or not group.get('is_active'): raise Exception("group_id not allowed") 
        return self.client.send(Message(text=message), thread_id=group_id, thread_type=ThreadType.GROUP)

if __name__ == "__main__":
    messenger = Messenger()
    msg_id = messenger.send("2873403912742691", "test1")
    print(msg_id)