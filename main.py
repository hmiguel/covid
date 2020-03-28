from flask import Flask, request, jsonify,  abort
from covid import Covid, Source
import pytz, os, utils, requests
from datetime import datetime
from messenger import Messenger

app = Flask(__name__)
messenger = Messenger()

@app.route('/health', methods=['GET']) 
def get_health():
    health = { 'version' : f"{os.environ.get('CURRENT_VERSION_ID', 'unknown')}", 'status' : 'ok' } 
    return jsonify(health)

@app.route('/stats/<country>/<situation>', methods=['GET']) 
def get_country_stats(country, situation):
    covid = Covid()
    info = covid.get_country_situation(country.upper(), situation)
    return jsonify({'text' : info.text, 'data' : info.data })

@app.route('/hooks/<group_id>', methods=['POST']) 
def post_messenger(group_id):
    text = request.json.get('text')
    if text is None: abort(404)
    messenger.send(group_id, text)
    return '', 204

@app.route('/bot', methods=['POST']) 
def post_bot():
    key = request.args.get('key') # TODO verify bot key
    if messenger.get_config().get('key') != key: return ('', 401) 
    content = request.values
    if int(content.get('NumMedia', 0)) != 1: return ('', 202) 
    url, media = content.get('MediaUrl0'), content.get('MediaContentType0')
    if media != "application/pdf": return ('', 202) 
    source = Source()
    infographic = source.get_pdf_infographic(url = url)
    # get groups
    groups = messenger.get_all_groups()
    groups = { g.key.id_or_name : utils.get_report_id(g.key.id_or_name, 'PT', 'summary', infographic.datetime) for g in groups if g }
    groups = { key : groups[key] for key in groups if not messenger.get_report(groups[key]) }
    mids = []
    for group_id in groups:
        mid = messenger.send_image(group_id, infographic) if infographic else messenger.send(group_id, data.text)
        if mid: messenger.create_report(group_id, groups[group_id])
        mids.append(mid)
    return ('', 204) if [m for m in mids if m] else ('', 202)

@app.route('/hooks/stats/<country>/<situation>', methods=['POST']) 
def post_hook_stats(country, situation):
    # parse request data
    data = request.json
    infographic = data.get('infographic', False)
    group_ids = data.get('group_ids') or [data.get('group_id')]
    is_cron = bool(data.get('is_cron', False))
    # check groups
    groups = [ messenger.get_group(group_id) for group_id in group_ids ]
    groups = { g.key.id_or_name : utils.get_report_id(g.key.id_or_name, country, situation, datetime.utcnow()) for g in groups if g }
    groups = { key : groups[key] for key in groups if not is_cron or (is_cron and not messenger.get_report(groups[key]))}
    # return if nothing to do
    if not groups: return ('Nothing to sent.', 202)  
    # get covid data
    covid = Covid()
    data = covid.get_country_situation(country.upper(), situation, infographic)
    mids = []
    for group_id in groups:
        mid = messenger.send_image(group_id, data.infographic) if infographic else messenger.send(group_id, data.text)
        if mid and is_cron: messenger.create_report(group_id, groups[group_id])
        mids.append(mid)
    return ('', 204) if [m for m in mids if m] else ('Nothing was sent.', 202) 

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)