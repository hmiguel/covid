from flask import Flask, request, jsonify,  abort
from google.cloud import datastore
from covid import Covid

app = Flask(__name__)

@app.route('/health', methods=['GET']) 
def get_health():
    return 'ok'

@app.route('/stats/<country>/deaths', methods=['GET']) 
def get_country_stats_deaths(country):
    covid = Covid()
    confirmed = covid.get_country_deaths(country)
    return confirmed

@app.route('/stats/<country>/confirmed', methods=['GET']) 
def get_country_stats_confirmed(country):
    covid = Covid()
    confirmed = covid.get_country_confirmed(country)
    return confirmed

@app.route('/hook/stats/<country>/confirmed', methods=['POST']) 
def post_hook_stats(country):
    from messenger import Messenger
    # parse request data
    data = request.json
    group_id = data.get('group_id')
    # get covid data
    covid = covid.Covid()
    confirmed = covid.get_country_confirmed(country)
    # post message
    messenger = Messenger()
    messenger.send(group_id, confirmed)
    return 'sent'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)