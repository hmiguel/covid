from flask import Flask, request, jsonify,  abort
from covid import Covid
from messenger import Messenger
import os 

app = Flask(__name__)
messenger = Messenger()
covid = Covid()

@app.route('/health', methods=['GET']) 
def get_health():
    health = { 'version' : f"{os.environ.get('CURRENT_VERSION_ID', 'unknown')}", 'status' : 'ok' } 
    return jsonify(health)

@app.route('/stats/<country>/<situation>', methods=['GET']) 
def get_country_stats_confirmed(country, situation):
    info = covid.get_country_situation(country, situation)
    return jsonify({'text' : info })

@app.route('/hooks/<group_id>', methods=['POST']) 
def post_messenger(group_id):
    text = request.json.get('text')
    if text is None: abort(404)
    messenger.send(group_id, text)
    return '', 204

@app.route('/hooks/stats/<country>/<situation>', methods=['POST']) 
def post_hook_stats(country, situation):
    # parse request data
    data = request.json
    im = data.get('im')
    group_id = data.get('group_id')
    # get covid data
    text = covid.get_country_situation(country, situation)
    # post message
    messenger.send(group_id, text)
    return '', 204

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)