
class Data(object): #TODO
    def __init__(self, confirmed, deaths, recovered):
        self.recovered = recovered
        self.confirmed = confirmed
        self.deaths = deaths

class Infographic(object):
    def __init__(self, image, description, datetime = None):
        self.datetime = datetime
        self.image = image
        self.description = description