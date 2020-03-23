from google.cloud import datastore

class Database(object):
    def __init__(self):
        self.client = datastore.Client()

    def get_utils(self, keyword):
        key = self.client.key('Utils', keyword)
        return self.client.get(key).get(keyword)

    def get_fb_configurations(self):
        key = self.client.key('Facebook', 'facebook')
        return self.client.get(key)

    def set_fb_configurations(self, configurations):        
        key = self.client.key('Facebook', 'facebook')
        with self.client.transaction():            
            entity = datastore.Entity(key=key)
            entity.update(configurations)
            self.client.put(entity)

    def get_fb_group(self, group_id):
        key = self.client.key('FacebookGroup', str(group_id))     
        group = self.client.get(key)
        return group
