import requests
DEFAULT_URL = "http://localhost:8081/artifactory/"

"""
DONE:

GET /api/system/security
GET /api/system/service_id
GET /api/system/security/certificates
GET /api/system
GET /api/system/ping
GET /api/system/configuration
GET /api/system/licenses
GET /api/system/version
GET /api/system/configuration/webServer
GET /api/system/configuration/reverseProxy/nginx
GET /api/system/replications

"""

class System:
    def __init__(self, auth, art_url, extra):
        self.auth = auth
        self.art_url = art_url
        self.extra = extra

    @classmethod
    def info(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='')

    @classmethod
    def security(cls, auth=None, art_url=DEFAULT_URL):
        """ DEPRECATED """
        return cls(auth, art_url, extra='/security')

    @classmethod
    def certificates(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/security/certificates')

    @classmethod
    def service_id(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/service_id')

    @classmethod
    def ping(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/ping')

    @classmethod
    def configuration(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/configuration')

    @classmethod
    def licenses(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/licenses')

    @classmethod
    def version(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/version')

    @classmethod
    def proxy_configuration(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/webServer')

    @classmethod
    def reverse_proxy_configuration(cls, proxy_type='nginx', auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/reverseProxy/{}'.format(proxy_type))

    @classmethod
    def replications(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/replications')


    def execute(self):
        full_url = "{}api/system".format(self.art_url, self.extra)
        resp = requests.get(url=full_url, auth=self.auth)
        return eval(resp.text)
