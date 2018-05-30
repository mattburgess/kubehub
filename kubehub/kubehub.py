import logging
import redis
import requests
import time
import werkzeug

from flask import Flask, jsonify
from operator import itemgetter

app = Flask(__name__)

r_cache = redis.StrictRedis(host='localhost', port=6379, db=0,
                            decode_responses=True)


def get_repos_from_cache():
    try:
        repos = []
        for key in r_cache.scan_iter("*"):
            repos.append(r_cache.hgetall(key))
    except redis.exceptions.ConnectionError as e:
        raise
    return repos


def get_repos_by_topic(topic_name, qry_limit):
    repos = get_repos_from_cache()

    if not repos:
        app.logger.debug('topic = {0}'.format(topic_name))
        app.logger.debug('query_limit = {0}'.format(qry_limit))
        query_params = {'q': 'topic:{0}'.format(topic_name), 'per_page': 100}
        r = requests.get('https://api.github.com/search/repositories',
                         params=query_params)
        time.sleep(5)
        r.raise_for_status()

        results = r.json()['items']
        while (not qry_limit or len(results) < qry_limit) and r.links['next']:
            r = requests.get(r.links['next']['url'])
            time.sleep(5)
            r.raise_for_status()
            results += r.json()['items']

        wanted_keys = ['name', 'full_name', 'html_url', 'language',
                       'updated_at', 'pushed_at', 'stargazers_count']
        for result in results:
            repo = {k: result[k] for k in wanted_keys}
            r_cache.hmset(result['id'], repo)
            r_cache.pexpire(result['id'], 60*60*1000)
        repos = get_repos_from_cache()
    return repos


def sort_repos(repos, key, reverse):
    return sorted(repos, key=itemgetter(key), reverse=reverse)


@app.route("/api/kubernetes")
def kubernetes():
    repos = get_repos_by_topic('kubernetes', 500)
    return jsonify(repos)


@app.route("/api/popularity/kubernetes")
def popularity_kubernetes():
    repos = get_repos_by_topic('kubernetes', 500)
    sorted_repos = sort_repos(repos, 'stargazers_count', reverse=True)
    return jsonify(sorted_repos)


@app.route("/api/activity/kubernetes")
def activity_kubernetes():
    repos = get_repos_by_topic('kubernetes', 500)
    sorted_repos = sort_repos(repos, 'updated_at', reverse=True)
    return jsonify(sorted_repos)


@app.errorhandler(werkzeug.exceptions.Forbidden)
def handle_forbidden_error(e):
    return 'Too many requests to GitHub API', 403


@app.errorhandler(werkzeug.exceptions.InternalServerError)
def handle_internal_server_error(e):
    return 'Internal Server Error!', 500


@app.errorhandler(redis.exceptions.ConnectionError)
def handle_redis_connection_error(e):
    return 'Internal Server Error!', 500
