from google.cloud import datastore
import datetime
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

    def get_fb_groups(self):
        query = self.client.query(kind='FacebookGroup')
        return list(query.fetch())

    def get_fb_group(self, group_id):
        key = self.client.key('FacebookGroup', str(group_id))     
        return self.client.get(key)

    def get_fb_report(self, report_id):
        key = self.client.key('FacebookReport', str(report_id))     
        return self.client.get(key)

    def create_fb_report(self, group_id, report_id):     
        with self.client.transaction():
            key = self.client.key('FacebookReport', report_id)  
            report = datastore.Entity(key=key)
            report.update({'group_id' : group_id, 'execution_date' : datetime.datetime.utcnow()})
            self.client.put(report)