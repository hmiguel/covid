
class Data(object):
    def __init__(self, data = None, datetime = None, infographic = None):      
        self.data = data
        self.datetime = datetime    
        self.infographic = infographic

class Infographic(object):
    def __init__(self, image, description, datetime):
        self.image = image
        self.description = description
        self.datetime = datetime