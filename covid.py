import requests, data, lxml.html
import datetime, utils, io
from database import Database
from models import Data, Infographic

class Source(object):
    def __init__(self, is_cron):
        self.countries = {'ZZ': self.__get_generic_country_data__, 'PT' : self.__get_pt_data__}
        self.daily_report_times = {'PT' : '12h00', 'IT' : '18h00' } #TODO move to db
        self.db = Database()
        self.is_cron = bool(is_cron)

    def get_country_data(self, country, infographic = None, report_datetime = None):

        return self.countries.get(country, self.countries.get('ZZ'))(country, infographic, report_datetime)

    def __get_ninja_data__(self, country):
        url = f"https://corona.lmao.ninja/countries/{data.countries.get(country)}"
        response = requests.get(url).json()
        return {"confirmed" : response.get('cases', 0) , "deaths" : response.get('deaths', 0), 
                "recovered" : response.get('recovered', 0)}

    def __get_value__(self, text):
        n = text.strip().replace(',', '')
        return n if n else 0

    def __get_worldometers_data__(self, country):
        url = "https://www.worldometers.info/coronavirus/#countries"
        tree = lxml.html.fromstring(requests.get(url).content)
        headers = ["country", "confirmed", "new_confirmed", "deaths", "new_deaths", "recovered", "active", "critical", "confirmed_per_1M", "deaths_per_1M"]
        today = tree.xpath(f"//table[@id='main_table_countries_today']/tbody[1]/tr[contains(td[1], '{data.wc_countries.get(country)}')]").pop()
        return dict(zip(headers, [ self.__get_value__(x.text_content()) for x in today.getchildren()]))

    def __get_generic_country_data__(self, country, infographic, report_datetime):
        return Data(self.__get_worldometers_data__(country), infographic = infographic, datetime=report_datetime)

    def __get_pt_data__(self, ignore, infographic, report_datetime):
        infographic = self.__get_pt_infographic__() if infographic is not None else None
        return Data(self.__get_worldometers_data__('PT'), infographic = infographic, datetime=report_datetime)

    def __get_pt_infographic__(self):
        today = datetime.datetime.utcnow()
        contents = lxml.html.fromstring(requests.get('https://covid19.min-saude.pt/relatorio-de-situacao/').content)
        report = (contents.xpath(f'//a[contains(text(),\'{today.strftime("%d/%m/")}\')]') or [None]).pop()
        if report is None: return None
        description = ''.join([t.text for t in report.getparent().getchildren() if report is not None]) 
        if description is None: return None
        infographic = utils.get_url_image(self.db.get_utils("pdf2image")+utils.get_base64(report.attrib['href']))
        return Infographic(infographic, description, today)

class Covid(object):
    def __init__(self, is_cron = False):
        self.source = Source(is_cron)
        self.situations = {'confirmed' : self.__get_country_confirmed__, 'deaths':  
        self.__get_country_deaths__, 'summary' : self.__get_country_summary__, 'recovered' : self.__get_country_recovered__}
    
    def get_country_situation(self, country, situation, infographic = False, report_datetime = None):
        report_datetime = report_datetime if report_datetime else datetime.datetime.utcnow()
        data = self.situations.get(situation)(country, report_datetime = report_datetime) if not infographic else self.situations.get(situation)(country, infographic, report_datetime)
        return data

    def __get_next_update__(self, country):
        hours, minutes = self.source.daily_report_times.get(country, '00h00').split('h')
        today_report_datetime = utils.get_datetime_midnight(datetime.datetime.utcnow()) + datetime.timedelta(hours=int(hours), minutes=int(minutes))
        return today_report_datetime if today_report_datetime > datetime.datetime.utcnow() else today_report_datetime + datetime.timedelta(days=1)

    def __get_country_summary__(self, country, infographic = None, report_datetime = None):
        info = self.source.get_country_data(country, infographic = infographic, report_datetime = report_datetime)
        diff_deaths = f" ({info.data.get('new_deaths')})" if info.data.get('new_deaths') else ''
        diff_cases = f" ({info.data.get('new_confirmed')})" if info.data.get('new_confirmed') else ''
        info.text = f"{data.countries.get(country).title()}: {info.data.get('confirmed')}{diff_cases} confirmados 😷, {info.data.get('deaths')}{diff_deaths} mortes 💀 e {info.data.get('recovered')} recuperados 😊."
        return info

    def __get_country_confirmed__(self, country, report_datetime):
        info = self.source.get_country_data(country, report_datetime = report_datetime)
        diff_yt = f" ({info.data.get('new_confirmed')})" if info.data.get('new_confirmed') else ''
        info.text = f"O número total de infectados em {data.countries.get(country).capitalize()} é de {info.data.get('confirmed')}{diff_yt} pessoas. 😷"
        info.data = { key : info.data.get(key) for key in info.data if key == "confirmed" }
        return info

    def __get_country_deaths__(self, country, report_datetime):
        info = self.source.get_country_data(country, report_datetime = report_datetime)
        diff_yt = f" ({info.data.get('new_deaths')})" if info.data.get('new_deaths') else ''
        info.text = f"O número total de mortos em {data.countries.get(country).capitalize()} é de {info.data.get('deaths')}{diff_yt} pessoas. 💀"
        info.data = { key : info.data.get(key) for key in info.data if key == "deaths" }
        return info

    def __get_country_recovered__(self, country, report_datetime):
        info = self.source.get_country_data(country, report_datetime = report_datetime)
        info.text = f"O número total de recuperados em {data.countries.get(country).capitalize()} é de {info.data.get('recovered')} pessoas. 😊"
        info.data = { key : info.data.get(key) for key in info.data if key == "recovered" }
        return info

if __name__ == "__main__":
    covid = Covid()
    #br = covid.get_country_situation('BR', 'recovered')
    pt = covid.get_country_situation('US', 'summary')
    #it = covid.get_country_situation('IT', 'deaths')
    
    # print(br.text, br.data, br.datetime)
    # print(it.text, it.data, it.datetime)
    print(pt.text, pt.data, pt.datetime)
   
    #pt_info = covid.get_country_situation('PT', 'summary', infographic = True) # infographic
    #print(type(pt_info.infographic))