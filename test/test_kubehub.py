import os
import redis
import unittest

from kubehub.kubehub import app, get_repos_by_topic

class KubehubTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        r_cache = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        r_cache.flushall()

    def tearDown(self):
        pass

    def test_get_repos_by_topic_no_pagination(self):
        repos = get_repos_by_topic('kubernetes', 100)
        assert len(repos) == 100

    def test_get_repos_by_topic_with_pagination(self):
        repos = get_repos_by_topic('kubernetes', 200)
        assert len(repos) == 200

    def test_kubernetes(self):
        response = self.app.get('/api/kubernetes')
        self.assertEqual(response.status_code, 200)
        assert len(response.get_json()) == 500

    def test_popularity_kubernetes(self):
        response = self.app.get('/api/popularity/kubernetes')
        self.assertEqual(response.status_code, 200)
        json = response.get_json()
        num_repos = len(json)
        assert num_repos == 500
        for i in range(num_repos - 1):
            assert json[i]['stargazers_count'] >= json[i+1]['stargazers_count']

    def test_activity_kubernetes(self):
        response = self.app.get('/api/activity/kubernetes')
        self.assertEqual(response.status_code, 200)
        json = response.get_json()
        num_repos = len(json)
        assert num_repos == 500
        for i in range(num_repos - 1):
            assert json[i]['updated_at'] >= json[i+1]['updated_at']

if __name__ == "__main__":
    unittest.main()
