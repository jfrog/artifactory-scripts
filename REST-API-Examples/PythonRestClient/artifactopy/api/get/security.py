import requests
DEFAULT_URL = "http://localhost:8081/artifactory/"

"""
DONE:

GET /api/security/users
GET /api/security/users/{userName}
GET /api/security/encryptedPassword
GET /api/security/configuration/passwordExpirationPolicy
GET /api/security/userLockPolicy
GET /api/security/lockedUsers
GET /api/security/apiKey
GET /api/security/groups
GET /api/security/groups/{groupName}
GET /api/security/permissions
GET /api/security/permissions/{permissionTargetName}
GET /api/security/token
"""


class Security:
    def __init__(self, auth, art_url, extra):
        self.auth = auth
        self.art_url = art_url
        self.extra = extra

    @classmethod
    def users(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/users')

    @classmethod
    def user(cls, username, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/users/{}'.format(username))

    @classmethod
    def encrypted_password(cls, auth, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/encryptedPassword')

    @classmethod
    def password_expiration_policy(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/configuration/passwordExpirationPolicy')

    @classmethod
    def user_lock_policy(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/userLockPolicy')

    @classmethod
    def locked_users(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/lockedUsers')

    @classmethod
    def api_key(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/apiKey')

    @classmethod
    def groups(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/groups')

    @classmethod
    def group(cls, name, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/groups/{}'.format(name))

    @classmethod
    def permissions(cls, target='', auth=None, art_url=DEFAULT_URL):
        if target:
            target = '/'+target

        return cls(auth, art_url, extra='/permissions{}'.format(target))

    @classmethod
    def token(cls, auth=None, art_url=DEFAULT_URL):
        return cls(auth, art_url, extra='/groups')

    def execute(self):
        full_url = "{}api/security".format(self.art_url, self.extra)
        resp = requests.get(url=full_url, auth=self.auth)
        return eval(resp.text)
