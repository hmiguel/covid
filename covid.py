import requests, data

class Covid(object):
    def __init__(self):
        self.url = "https://covid19.mathdro.id/api/"

    def get_country_data(self, country):
        request = requests.get(f"{self.url}/countries/{country}")
        return request.json()

    def get_country_confirmed(self, country):
        info = self.get_country_data(country)
        infected = f"O número total de infectados em {data.countries.get(country)} é de {info.get('confirmed').get('value')} pessoas. 😷"
        return infected

    def get_country_deaths(self, country):
        info = self.get_country_data(country)
        deaths = f"O número total de mortos em {data.countries.get(country).capitalize()} é de {info.get('deaths').get('value')} pessoas. 💀"
        return deaths

if __name__ == "__main__":
    covid = Covid()
    print(covid.get_country_confirmed('PT'))
    print(covid.get_country_deaths('PT'))