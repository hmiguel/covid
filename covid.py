import requests, data, lxml.html
import datetime, utils, io
from database import Database
from models import Infographic

class Source(object):
    def __init__(self):
        self.countries = {'PT' : self.get_pt_data}
        self.db = Database()

    def get_country_data(self, country, infographic):
        url = f"https://corona.lmao.ninja/countries/{data.countries.get(country)}"
        request = requests.get(url)
        response = request.json()
        return {
                "confirmed" : response.get('cases') , 
                "deaths" : response.get('deaths'), 
                "recovered" : response.get('recovered')
                }

    def get_pt_infographic(self, report_datetime):
        report_datetime = report_datetime.strftime("%d/%m/%Y") if report_datetime else (datetime.datetime.now()-datetime.timedelta(hours=12)).strftime("%d/%m/%Y")
        html = requests.get('https://covid19.min-saude.pt/relatorio-de-situacao/')
        doc = lxml.html.fromstring(html.content)
        daily_report = doc.xpath(f"//a[contains(text(),'{report_datetime}')]").pop()
        infographic = utils.get_url_image(self.db.get_utils("pdf2image")+utils.get_base64(daily_report.attrib['href']))
        return Infographic(infographic, daily_report.text, report_datetime)

    def get_pt_data(self, ignore, infographic, datetime):
        if infographic: return self.get_pt_infographic(datetime)
        url = "https://services.arcgis.com/CCZiGSEQbAxxFVh3/arcgis/rest/services/COVID19Portugal_UltimoRel/FeatureServer/0/query?f=json&where=1=1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outSR=102100&resultOffset=0&resultRecordCount=50&cacheHint=true"
        request = requests.get(url)
        response = request.json().get('features')[0].get('attributes')
        return {    
                "confirmed" : response.get('casosconfirmados'), 
                "deaths" : response.get('nrobitos'), 
                "recovered" : response.get('recuperados')
                }

class Covid(object):
    def __init__(self):
        self.source = Source()
        self.situations = {'confirmed' : self.get_country_confirmed, 'deaths':  self.get_country_deaths, 'summary' : self.get_country_summary}
        
    def get_country_data(self, country, infographic = False, datetime = False):     
        return self.source.countries.get(country, self.source.get_country_data)(country, infographic, datetime)

    def get_country_situation(self, country, situation, infographic = None, datetime = None):
        return self.situations.get(situation)(country) if not infographic else self.situations.get(situation)(country, infographic, datetime)

    def get_country_summary(self, country, infographic = None, datetime = None):
        return self.get_country_data(country, infographic, datetime)

    def get_country_confirmed(self, country):
        info = self.get_country_data(country)
        cases = f"O número total de infectados em {data.countries.get(country).capitalize()} é de {info.get('confirmed')} pessoas. 😷"
        return cases

    def get_country_deaths(self, country):
        info = self.get_country_data(country)
        deaths = f"O número total de mortos em {data.countries.get(country).capitalize()} é de {info.get('deaths')} pessoas. 💀"
        return deaths

if __name__ == "__main__":
    
    #covid = Covid()
    # print(covid.get_country_situation('PT', 'confirmed'))
    # print(covid.get_country_situation('IT', 'confirmed'))
   
    # print(covid.get_country_situation('PT', 'deaths'))
    # print(covid.get_country_situation('IT', 'deaths'))

    #info = covid.get_country_situation('PT', 'summary', True) # infographic
    pass


