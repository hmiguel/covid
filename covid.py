import requests, data, lxml.html
import datetime, utils, io
from database import Database
from models import Data, Infographic

class Source(object):
    def __init__(self):
        self.groups = { 'EU' : data.europe, 'WD' : data.countries }
        self.countries = {'ZZ': self.__get_generic_country_data, 'PT' : self.__get_pt_data, 'EU' : self.__get_sum_data, 'WD': self.__get_sum_data}
        self.db = Database()

    def get_country_data(self, country, infographic = None, report_datetime = None):
        return self.countries.get(country, self.countries.get('ZZ'))(country, infographic, report_datetime)

    def get_pdf_infographic(self, url, description = None):
        url = requests.head(url, allow_redirects=True).url
        infographic = utils.get_url_image(self.db.get_utils("pdf2image")+utils.get_base64(url))
        return Infographic(infographic, f'Report {infographic.datetime.strftime("%d/%m/%Y, %H:%M:%S")}' if not description else description, infographic.datetime)

    def __get_value(self, text):
        n = text.strip().replace(',', '')
        return n if n else 0

    def __get_worldometers_data__(self, country):
        url = "https://www.worldometers.info/coronavirus/#countries"
        tree = lxml.html.fromstring(requests.get(url).content)
        country = data.wc_countries.get(country)   
        result = [x for x in tree.xpath(f"//table[@id='main_table_countries_today']/tbody[1]/tr[td[1] = '{country}']")].pop(0)
        return dict(zip(data.wc_headers, [ self.__get_value(x.text_content()) for x in result.getchildren()]))

    def __get_generic_country_data(self, country, infographic, report_datetime):
        return Data(self.__get_worldometers_data__(country), infographic = infographic, datetime=report_datetime)

    def __get_sum_data(self, group, infographic, report_datetime):
        url = "https://www.worldometers.info/coronavirus/#countries"
        tree = lxml.html.fromstring(requests.get(url).content)
        out = [0,0,0,0,0,0,0]
        for code in self.groups.get(group):
            if (code not in data.wc_countries): continue
            row = tree.xpath(f"//table[@id='main_table_countries_today']/tbody[1]/tr[contains(td[1], '{data.wc_countries.get(code)}')]") or None
            if row is None: continue
            row = [self.__get_value(x.text_content()) for x in row.pop().getchildren()][1:8]   
            row = [int(x.lstrip('+')) if '+' in str(x) else int(x) for x in row]
            out = [x + y for x, y in zip(out, row)]
        out = dict(zip(data.wc_headers[1:-2], out))
        print(out)
        out['country'] = data.wc_countries.get(group)
        out['new_deaths'], out['new_confirmed'] = f"+{out['new_deaths']}" if out['new_deaths'] else '0', f"+{out['new_confirmed']}" if out['new_confirmed'] else '0'
        return Data(out, infographic = infographic, datetime=report_datetime)

    def __get_pt_data(self, ignore, infographic, report_datetime):
        infographic = self.__get_pt_infographic() if infographic is not None else None
        return Data(self.__get_worldometers_data__('PT'), infographic = infographic, datetime=report_datetime)

    def __get_pt_infographic(self):
        today = datetime.datetime.utcnow()
        contents = lxml.html.fromstring(requests.get('https://covid19.min-saude.pt/relatorio-de-situacao/').content)
        report = (contents.xpath(f"//ul/li") or [None]).pop(0)
        url, description = report.getchildren().pop(0).attrib['href'], ''.join(report.itertext())
        if today.strftime("%d/%m/%Y") not in description or not url.endswith('pdf'): return None
        return self.get_pdf_infographic(url, description)

class Covid(object):
    def __init__(self):
        self.source = Source()
        self.situations = {'confirmed' : self.__get_country_confirmed__, 'deaths':  
        self.__get_country_deaths__, 'summary' : self.__get_country_summary__, 'recovered' : self.__get_country_recovered__}
    
    def get_country_situation(self, country, situation, infographic = False, report_datetime = None):
        report_datetime = report_datetime if report_datetime else datetime.datetime.utcnow()
        data = self.situations.get(situation)(country, report_datetime = report_datetime) if not infographic else self.situations.get(situation)(country, infographic, report_datetime)
        return data

    def __get_country_summary__(self, country, infographic = None, report_datetime = None):
        info = self.source.get_country_data(country, infographic = infographic, report_datetime = report_datetime)
        diff_deaths = f" ({info.data.get('new_deaths')}/{ utils.get_increase_percent(int(info.data.get('deaths')), int(info.data.get('new_deaths').replace('+','')))}%)" if info.data.get('new_deaths') else ''
        diff_cases = f" ({info.data.get('new_confirmed')}/{ utils.get_increase_percent(int(info.data.get('confirmed')), int(info.data.get('new_confirmed').replace('+','')))}%)" if info.data.get('new_confirmed') else ''
        info.text = f"{data.countries.get(country).title()}: {info.data.get('confirmed')}{diff_cases} confirmados 😷, {info.data.get('deaths')}{diff_deaths} mortes 💀, {info.data.get('critical')} em estado crítico 😵 e {info.data.get('recovered')} recuperados 😊."
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
    import data
    #print(data.wc_countries.get('EU'))
    covid = Covid()
    #br = covid.get_country_situation('BR', 'recovered')
    wd = covid.get_country_situation('WD', 'summary')
    pt = covid.get_country_situation('PT', 'summary')
    eu = covid.get_country_situation('EU', 'summary')
    #it = covid.get_country_situation('IT', 'deaths')
    
    # print(br.text, br.data, br.datetime)
    # print(it.text, it.data, it.datetime)
    print(eu.text, eu.data, eu.datetime)
    print(pt.text, pt.data, pt.datetime)
    print(wd.text, wd.data, wd.datetime)
    #pt_info = covid.get_country_situation('PT', 'summary', infographic = True) # infographic
    #print(type(pt_info.infographic))
