import requests, data, lxml.html
import datetime, utils, io
from database import Database
from models import Data, Infographic

class Source(object):
    def __init__(self):
        self.countries = {'generic': self.__get_generic_country_data__, 'PT' : self.__get_pt_data__}
        self.daily_report_times = {'PT' : '12h00', 'IT' : '18h00' } #TODO move to db
        self.db = Database()

    def get_country_data(self, country, infographic = False, report_datetime = None, is_cron = False):
        return self.countries.get(country, 'generic')(country, infographic, report_datetime, is_cron)

    def __get_ninja_data__(self, country):
        url = f"https://corona.lmao.ninja/countries/{data.countries.get(country)}"
        response = requests.get(url).json()
        return { "confirmed" : response.get('cases') , "deaths" : response.get('deaths'), 
                "recovered" : response.get('recovered')}

    def __get_worldometers_data__(self, country_name):
        url = f"https://www.worldometers.info/coronavirus/country/{country_name}/"
        tree = lxml.html.fromstring(requests.get(url).content)
        return { 'confirmed' if 'cases' in b.text.lower() else 'deaths' 
                if 'deaths' in b.text.lower() else 'recovered' 
                : b.getnext().xpath('span').pop().text.strip().replace(',','') for b in tree.xpath('//div[@id="maincounter-wrap"]/h1') }

    def __get_generic_country_data__(self, country, infographic, report_datetime, is_cron):
        return Data(self.__get_ninja_data__(country), infographic = infographic, datetime=report_datetime)

    def __get_pt_data__(self, ignore, infographic, report_datetime, is_cron):
        infographic = self.__get_pt_infographic__(is_cron) if infographic else None
        return Data(self.__get_worldometers_data__('portugal'), infographic = infographic, datetime=report_datetime)

    def __get_pt_infographic__(self, is_cron):
        today, yesterday = datetime.datetime.utcnow(), datetime.datetime.utcnow()-datetime.timedelta(days=1)
        contents = lxml.html.fromstring(requests.get('https://covid19.min-saude.pt/relatorio-de-situacao/').content)
        today_report = contents.xpath(f'//a[contains(text(),\'{today.strftime("%d/%m/%Y")}\')]')
        yesterday_report = contents.xpath(f'//a[contains(text(),\'{yesterday.strftime("%d/%m/%Y")}\')]')
        report = yesterday_report.pop() if not today_report and not is_cron else today_report.pop() if today_report else None
        if report is None: return None
        infographic = utils.get_url_image(self.db.get_utils("pdf2image")+utils.get_base64(report.attrib['href']))
        return Infographic(infographic, report.text, today if today_report else yesterday)

class Covid(object):
    def __init__(self):
        self.source = Source()
        self.situations = {'confirmed' : self.__get_country_confirmed__, 'deaths':  
        self.__get_country_deaths__, 'summary' : self.__get_country_summary__, 'recovered' : self.__get_country_recovered__}
    
    def get_country_situation(self, country, situation, infographic = False, report_datetime = None, is_cron = False):
        report_datetime = report_datetime if report_datetime else datetime.datetime.utcnow()
        data = self.situations.get(situation)(country, report_datetime) if not infographic else self.situations.get(situation)(country, infographic, report_datetime, is_cron)
        return data

    def __get_next_update__(self, country):
        hours, minutes = self.source.daily_report_times.get(country, '00h00').split('h')
        today_report_datetime = utils.get_datetime_midnight(datetime.datetime.utcnow()) + datetime.timedelta(hours=int(hours), minutes=int(minutes))
        return today_report_datetime if today_report_datetime > datetime.datetime.utcnow() else today_report_datetime + datetime.timedelta(days=1)

    def __get_country_summary__(self, country, infographic = None, report_datetime = None, is_cron = False):
        info = self.source.get_country_data(country, infographic, report_datetime, is_cron)
        info.text = f"Portugal: {info.data.get('confirmed')} confirmados 😷, {info.data.get('deaths')} mortes 💀 and {info.data.get('recovered')} recuperados 😊."
        return info

    def __get_country_confirmed__(self, country, report_datetime):
        info = self.source.get_country_data(country, report_datetime = report_datetime)
        info.text = f"O número total de infectados em {data.countries.get(country).capitalize()} é de {info.data.get('confirmed')} pessoas. 😷"
        info.data = { key : info.data.get(key) for key in info.data if key == "confirmed" }
        return info

    def __get_country_deaths__(self, country, report_datetime):
        info = self.source.get_country_data(country, report_datetime = report_datetime)
        info.text = f"O número total de mortos em {data.countries.get(country).capitalize()} é de {info.data.get('deaths')} pessoas. 💀"
        info.data = { key : info.data.get(key) for key in info.data if key == "deaths" }
        return info

    def __get_country_recovered__(self, country, report_datetime):
        info = self.source.get_country_data(country, report_datetime = report_datetime)
        info.text = f"O número total de recuperados em {data.countries.get(country).capitalize()} é de {info.data.get('recovered')} pessoas. 😊"
        info.data = { key : info.data.get(key) for key in info.data if key == "recovered" }
        return info

if __name__ == "__main__":
    covid = Covid()
    br = covid.get_country_situation('BR', 'recovered')
    pt = covid.get_country_situation('PT', 'confirmed')
    it = covid.get_country_situation('IT', 'deaths')
    
    print(br.text, br.data, br.datetime)
    print(it.text, it.data, it.datetime)
    print(pt.text, pt.data, pt.datetime)
   
    pt_info = covid.get_country_situation('PT', 'summary', infographic = True) # infographic
    print(type(pt_info.infographic))