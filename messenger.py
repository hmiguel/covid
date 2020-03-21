from fbchat import Client
from fbchat.models import *
from google.cloud import datastore

class Messenger(object):
    def __init__(self):
        self.db = datastore.Client()
        self.key = self.db.key('Facebook', 'facebook')     
        self.configurations = self.db.get(self.key)
        self.client = self.__get_client__()

    def __set_session__(self, session): 
        with self.db.transaction():
            self.configurations['session'] = session
            entity = datastore.Entity(key=self.key)
            entity.update(self.configurations)
            self.db.put(entity)

    def __get_client__(self):
        session = self.configurations.get('session')
        client = Client(self.configurations.get('email'), self.configurations.get('password'), session_cookies=session)
        self.__set_session__(client.getSession())
        return client

    def send(self, group_id, message):       
        self.client.send(Message(text=message), thread_id=group_id, thread_type=ThreadType.GROUP)

if __name__ == "__main__":
    messenger = Messenger()

