import requests, data

class Source(object):
    def __init__(self):
        self.countries = {'PT' : self.get_pt_data}

    def get_country_data(self, country):
        url = "https://covid19.mathdro.id/api/"
        request = requests.get(f"{url}/countries/{country}")
        return request.json()

    def get_pt_data(self, ignore):
        url = "https://services.arcgis.com/CCZiGSEQbAxxFVh3/arcgis/rest/services/COVID19Portugal_UltimoRel/FeatureServer/0/query?f=json&where=1=1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outSR=102100&resultOffset=0&resultRecordCount=50&cacheHint=true"
        request = requests.get(url)
        data = request.json().get('features')[0].get('attributes')
        return { "confirmed" : {"value" : data.get('casosconfirmados') } , "deaths" : { "value" : data.get('nrobitos')}}

class Covid(object):
    def __init__(self):
        self.source = Source()
        self.general = "https://covid19.mathdro.id/api/"
        self.situations = {'confirmed' : self.get_country_confirmed, 'deaths':  self.get_country_deaths}
        
    def get_country_data(self, country):     
        return self.source.countries.get(country, self.source.get_country_data)(country)

    def get_country_situation(self, country, situation):
        return self.situations.get(situation)(country)

    def get_country_confirmed(self, country):
        info = self.get_country_data(country)
        infected = f"O número total de infectados em {data.countries.get(country).capitalize()} é de {info.get('confirmed').get('value')} pessoas. 😷"
        return infected

    def get_country_deaths(self, country):
        info = self.get_country_data(country)
        deaths = f"O número total de mortos em {data.countries.get(country).capitalize()} é de {info.get('deaths').get('value')} pessoas. 💀"
        return deaths

if __name__ == "__main__":
    covid = Covid()
    print(covid.get_country_situation('PT', 'confirmed'))
    print(covid.get_country_situation('IT', 'confirmed'))
   
    print(covid.get_country_situation('PT', 'deaths'))
    print(covid.get_country_situation('IT', 'deaths'))