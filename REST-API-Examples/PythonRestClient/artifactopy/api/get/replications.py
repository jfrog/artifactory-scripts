import requests
DEFAULT_URL = "http://localhost:8081/artifactory/"

"""
DONE:

GET /api/replications/{repoKey}
GET /api/replication/{repoKey}
GET api/replications/channels/{repo}
"""


class Replication:
    def __init__(self, auth, art_url, extra):
        self.auth = auth
        self.art_url = art_url
        self.extra = extra

    @classmethod
    def config(cls, repo_key, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='s/{}'.format(repo_key))

    @classmethod
    def status(cls, repo_key, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/{}'.format(repo_key))

    @classmethod
    def subscribed_instances(cls, repo_key, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='s/channels/{}'.format(repo_key))

    def execute(self):
        full_url = "{}api/replication{}".format(self.art_url, self.extra)
        resp = requests.get(url=full_url, auth=self.auth)
        return eval(resp.text)
