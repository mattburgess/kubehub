import os
import unittest

from kubehub.kubehub import app, get_repos_by_topic

class KubehubTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

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

if __name__ == "__main__":
    unittest.main()
