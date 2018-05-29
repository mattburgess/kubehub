import logging
import requests
from flask import Flask, jsonify

app = Flask(__name__)

def get_repos_by_topic(topic_name, query_limit):
    app.logger.debug('topic = {0}'.format(topic_name))
    app.logger.debug('query_limit = {0}'.format(query_limit))
    query_params = {'q': 'topic:{0}'.format(topic_name), 'per_page': 100}
    r = requests.get('https://api.github.com/search/repositories',
                     params=query_params)

    results = r.json()['items']
    while (not query_limit or len(results) < query_limit) and r.links['next']:
        r = requests.get(r.links['next']['url'])
        results += r.json()['items']

    app.logger.info('{0} repositories found'.format(len(results)))

    wanted_keys = ['id', 'name', 'full_name', 'html_url', 'language',
                   'updated_at', 'pushed_at', 'stargazers_count']
    filtered_results = []
    for result in results:
        filtered_results.append({k: result[k] for k in wanted_keys})
    return filtered_results

@app.route("/api/kubernetes")
def kubernetes():
    repos = get_repos_by_topic('kubernetes', 500)
    return jsonify(repos)
