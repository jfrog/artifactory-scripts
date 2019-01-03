import requests
DEFAULT_URL = "http://localhost:8081/artifactory/"

"""
DONE

GET /api/build
GET /api/build/{buildName}
GET /api/build/{buildName}/{buildNumber}
GET /api/build/{buildName}/{buildNumber}?diff={OlderbuildNumber}
"""


class Build:
    def __init__(self, auth, art_url, extra=""):
        self.auth = auth
        self.art_url = art_url
        self.extra = extra
        if self.art_url[-1] is not '/':
            self.art_url += '/'

    @classmethod
    def all_builds(cls, auth=None, art_url=DEFAULT_URL):
        """
        Description: Provides information on all builds
        Since: 2.2.0
        Security: Requires a privileged user (can be anonymous)
        Usage: GET /api/build
        Produces: application/vnd.org.jfrog.build.Builds+json

        :param auth:
        :param art_url:
        :return application/vnd.org.jfrog.build.Builds+json:
        """
        return cls(auth=auth, art_url=DEFAULT_URL)

    @classmethod
    def build_runs(cls, build_name, auth=None, art_url=DEFAULT_URL):
        """
        Description: Build Runs
        Since: 2.2.0
        Security: Requires a privileged user (can be anonymous)
        Usage: GET /api/build/{buildName}
        Produces: application/vnd.org.jfrog.build.BuildsByName+json
        :param build_name:
        :param auth:
        :param art_url:
        :return application/vnd.org.jfrog.build.BuildsByName+json:
        """
        return cls(auth=auth, art_url=art_url, extra='/{}'.format(build_name))

    @classmethod
    def build_info(cls, build_name, build_number, auth=None, art_url=DEFAULT_URL):
        """
        Description: Build Info
        Since: 2.2.0
        Security: Requires a privileged user with deploy permissions (can be anonymous)
        Usage: GET /api/build/{buildName}/{buildNumber}
        Produces: application/vnd.org.jfrog.build.BuildInfo+json
        :param build_name:
        :param build_number:
        :param auth:
        :param art_url:
        :return application/vnd.org.jfrog.build.BuildInfo+json:
        """
        return cls(auth, art_url, extra='/{}/{}'.format(build_name, build_number))

    @classmethod
    def build_diff(cls, build_name, build_number, diff_number, auth=None, art_url=DEFAULT_URL):
        """
        Description: Compare a build artifacts/dependencies/environment with an older build to see what has changed (new artifacts added, old dependencies deleted etc).
        Since: 2.6.6
        Security: Requires a privileged user (can be anonymous)
        Usage: GET /api/build/{buildName}/{buildNumber}?diff={OlderbuildNumber}
        Produces: application/vnd.org.jfrog.build.BuildsDiff+json
        :param build_name:
        :param build_number:
        :param diff_number:
        :param auth:
        :param art_url:
        :return:
        """
        return cls(auth, art_url, extra='/{}/{}?diff={}'.format(build_name, build_number, diff_number))

    def execute(self):
        full_url = "{}api/build{}".format(self.art_url, self.extra)
        resp = requests.get(url=full_url, auth=self.auth)
        return eval(resp.text)

