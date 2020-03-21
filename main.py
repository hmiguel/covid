from flask import Flask, request, jsonify,  abort
from google.cloud import datastore
from covid import Covid
import os 

app = Flask(__name__)

@app.route('/health', methods=['GET']) 
def get_health():
    #major_ver, minor_ver = os.environ.get('CURRENT_VERSION_ID').rsplit('.',1)
    #health = { 'version' : f'{major_ver.minor_ver}', 'status' : 'ok'  }
    health = {'status' : 'ok'}
    return jsonify(health)

@app.route('/stats/<country>/deaths', methods=['GET']) 
def get_country_stats_deaths(country):
    covid = Covid()
    info = covid.get_country_deaths(country)
    return jsonify({'text' : info })

@app.route('/stats/<country>/confirmed', methods=['GET']) 
def get_country_stats_confirmed(country):
    covid = Covid()
    info = covid.get_country_confirmed(country)
    return jsonify({'text' : info })

@app.route('/hook/stats/<country>/confirmed', methods=['POST']) 
def post_hook_stats(country):
    from messenger import Messenger
    # parse request data
    data = request.json
    group_id = data.get('group_id')
    # get covid data
    covid = Covid()
    confirmed = covid.get_country_confirmed(country)
    # post message
    messenger = Messenger()
    messenger.send(group_id, confirmed)
    return 'sent'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)