import logging
import requests
import time
import werkzeug

from flask import Flask, jsonify
from operator import itemgetter

app = Flask(__name__)

def get_repos_by_topic(topic_name, query_limit):
    app.logger.debug('topic = {0}'.format(topic_name))
    app.logger.debug('query_limit = {0}'.format(query_limit))
    query_params = {'q': 'topic:{0}'.format(topic_name), 'per_page': 100}
    r = requests.get('https://api.github.com/search/repositories',
                     params=query_params)
    time.sleep(5)
    r.raise_for_status()

    results = r.json()['items']
    while (not query_limit or len(results) < query_limit) and r.links['next']:
        r = requests.get(r.links['next']['url'])
        time.sleep(5)
        r.raise_for_status()
        results += r.json()['items']

    app.logger.info('{0} repositories found'.format(len(results)))

    wanted_keys = ['id', 'name', 'full_name', 'html_url', 'language',
                   'updated_at', 'pushed_at', 'stargazers_count']
    filtered_results = []
    for result in results:
        filtered_results.append({k: result[k] for k in wanted_keys})
    return filtered_results

def sort_repos(repos, key):
    return sorted(repos, key=itemgetter(key))

@app.route("/api/kubernetes")
def kubernetes():
    repos = get_repos_by_topic('kubernetes', 500)
    return jsonify(repos)

@app.route("/api/popularity/kubernetes")
def popularity_kubernetes():
    repos = get_repos_by_topic('kubernetes', 500)
    sorted_repos = sort_repos(repos, 'stargazers_count')
    return jsonify(sorted_repos)

@app.errorhandler(werkzeug.exceptions.Forbidden)
def handle_forbidden_error(e):
    return 'Too many requests to GitHub API', 403

@app.errorhandler(werkzeug.exceptions.InternalServerError)
def handle_internal_server_error(e):
    return 'Internal Server Error!', 500
