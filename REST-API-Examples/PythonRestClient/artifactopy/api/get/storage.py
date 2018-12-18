import requests
DEFAULT_URL = "http://localhost:8081/artifactory/"

"""
DONE:

GET /api/storage/{repoKey}/{folder-path}
GET /api/storage/{repoKey}/{filePath}
GET /api/storageinfo
GET /api/storage/{repoKey}/{item-path}?lastModified
GET /api/storage/{repoKey}/{item-path}?stats
GET /api/storage/{repoKey}/{itemPath}?properties[=x[,y]]

TODO

GET /api/storage/{repoKey}/{folder-path}?list[&deep=0/1][&depth=n][&listFolders=0/1][&mdTimestamps=0/1][&includeRootPath=0/1]
GET /api/storage/{repoKey}/{itemPath}?permissions

"""


class Storage:
    def __init__(self, auth, art_url, extra):
        self.auth = auth
        self.art_url = art_url
        self.extra = extra

    @classmethod
    def folder_info(cls, repo_key, folder_path, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/{}/{}'.format(repo_key, folder_path))

    @classmethod
    def file_info(cls, repo_key, file_path, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/{}/{}'.format(repo_key, file_path))

    @classmethod
    def info(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='info')

    @classmethod
    def last_modified(cls, repo_key, file_path, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/{}/{}?lastModified'.format(repo_key, file_path))

    @classmethod
    def file_stats(cls, repo_key, file_path, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/{}/{}?stats'.format(repo_key, file_path))

    @classmethod
    def item_properties(cls, repo_key, file_path, auth=None, art_url=DEFAULT_URL, props=''):
        if props:
            props = "={}".format(str(props))
        return cls(auth, art_url, extra='/{}/{}?props{}'.format(repo_key, file_path, props))

    def execute(self):
        full_url = "{}api/storage{}".format(self.art_url, self.extra)
        resp = requests.get(url=full_url, auth=self.auth)
        return eval(resp.text)
