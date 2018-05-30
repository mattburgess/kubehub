"""Query the GitHub API for Kubernetes-related repositories

This module provides an API for querying GitHub for repositories related
to Kubernetes.

Endpoints:
    /api/kubernetes            - returns an unsorted list of 500
                                 Kubernetes-related repositories
    /api/popularity/kubernetes - returns a list of 500 Kubernetes-related
                                 repositories, sorted by popularity
    /api/activity/kubernetes   - returns a list of 500 Kubernetes-related
                                 repositories, sorted by most recent activity

Request format:
    All API requests must be HTTP GET requests

Response format:
    All successful responses will be in JSON (application/json) with the
    following structure: [{'id', name', 'full_name', 'html_url', 'language',
    'updated_at', 'pushed_at', 'stargazers_count'},...]

Todo:
    * Make Redis connection parameters configurable
    * Make Redis cache TTL configurable
    * Remove hard-coded sleep workaround for GitHub's rate-limiting (see
      https://developer.github.com/v3/rate_limit/)
    * Improve error handling, such that useful errors are logged to the API
      server but not exposed to clients
    * Make GitHub API endpoint configurable
"""

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
    """Return the list of repositories found in the Redis cache

    Returns:
        A list of dicts containing repository details
    """
    try:
        repos = []
        for key in r_cache.scan_iter("*"):
            repos.append(r_cache.hgetall(key))
    except redis.exceptions.ConnectionError as e:
        raise
    return repos


def get_repos_by_topic(topic_name, qry_limit):
    """Return a list of repositories from the Redis cache, or if the cache is
    invalid, then from GitHub's API

    Args:
        topic_name (str): The topic name to search on
        qry_limit (int): The number of repositories to return

    Returns:
        A list of dicts containing repository details
    """

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
    """Sorts a list of repository dictionaries by the provided attribute name,
    optionally reversing the sort order

    Args:
        repos (list of dicts): The list of repository dicts to sort
        key (str): The key to sort by
        reverse (bool): Reverse the sort order

    Return:
        list of dicts: The list of repository dictionaries sorted by `key`
    """

    return sorted(repos, key=itemgetter(key), reverse=reverse)


@app.route("/api/kubernetes")
def kubernetes():
    """/api/kubernetes endpoint. Returns an unsorted list of 500
    Kubernetes-related GitHub repositories
    """

    repos = get_repos_by_topic('kubernetes', 500)
    return jsonify(repos)


@app.route("/api/popularity/kubernetes")
def popularity_kubernetes():
    """/api/popularity/kubernetes endpoint. Returns a list of 500
    Kubernetes-related GitHub repositories, sorted by popularity
    """

    repos = get_repos_by_topic('kubernetes', 500)
    sorted_repos = sort_repos(repos, 'stargazers_count', reverse=True)
    return jsonify(sorted_repos)


@app.route("/api/activity/kubernetes")
def activity_kubernetes():
    """/api/activity/kubernetes endpoint. Returns a list of 500
    Kubernetes-related GitHub repositories, sorted by activity
    """

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
