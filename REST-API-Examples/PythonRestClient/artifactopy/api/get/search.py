import requests
DEFAULT_URL = "http://localhost:8081/artifactory/"

"""
==========
TODO
-----


GET /api/search/prop?[p1=v1,v2][&p2=v3][&repos=x[,y]]
GET /api/search/checksum?md5=md5sum?sha1=sha1sum?sha256=sha256sum[&repos=x[,y]]
GET /api/search/badChecksum?type=md5|sha1[&repos=x[,y]]
GET /api/search/usage?notUsedSince=javaEpochMillis[&createdBefore=javaEpochMillis][&repos=x[,y]]
GET /api/search/dates?[from=fromVal][&to=toVal][&repos=x[,y]][&dateFields=c[,d]]
GET /api/search/creation?from=javaEpochMillis[&to=javaEpochMillis][&repos=x[,y]]
GET /api/search/pattern?pattern=repo-key:this/is/a/*pattern*.war
GET /api/search/dependency?sha1=sha1Checksum
GET /api/search/license[?unapproved=1][&unknown=1][&notfound=0][&neutral=0][&approved=0][&autofind=0][&repos=x[,y]]
GET /api/search/versions?[g=groupId][&a=artifactId][&v=version][&remote=0/1][&repos=x[,y]]
GET /api/search/latestVersion?[g=groupId][&a=artifactId][&v=version][&remote=1][&repos=x[,y]]


DONE
-----
GET /api/search/artifact?name=name[&repos=x[,y]]
GET /api/search/archive?name=[archiveEntryName][&repos=x[,y]]
GET /api/search/gavc?[g=groupId][&a=artifactId][&v=version][&c=classifier][&repos=x[,y]]


=========
"""


class Search:
    def __init__(self, auth, art_url, extra="", headers={}):
        self.auth = auth
        self.art_url = art_url
        self.headers = headers
        if self.art_url[-1] is not '/':
            self.art_url += '/'
        self.extra = extra

    @classmethod
    def quick(cls, name, repos=[], auth=None, art_url=DEFAULT_URL, props=False, info=False):
        """
        Description: Artifact search by part of file name.
        Searches return file info URIs. Can limit search to specific repositories (local or caches).
        Since: 2.2.0
        Security: Requires a privileged user (can be anonymous)
        Usage: GET /api/search/artifact?name=name[&repos=x[,y]]
        Headers (Optionally):
                 X-Result-Detail: info (To add all extra information of the found artifact),
                 X-Result-Detail: properties (to get the properties of the found artifact),
                 X-Result-Detail: info, properties (for both).
        Produces: application/vnd.org.jfrog.artifactory.search.ArtifactSearchResult+json
        """
        headers = cls.get_headers(info, props)
        extra = "/artifact?name={}&repos={}".format(name, cls.get_repos(repos))

        return cls(auth=auth, art_url=art_url, headers=headers, extra=extra)

    @classmethod
    def archive(cls, name, repos=[], auth=None, art_url=DEFAULT_URL, headers={}):
        """
        Description: Search archive for classes or any other resources within an archive.
        Can limit search to specific repositories (local or caches).
        Since: 2.2.0
        Security: Requires a privileged user (can be anonymous)
        Usage: GET /api/search/archive?name=[archiveEntryName][&repos=x[,y]]
        Produces: application/vnd.org.jfrog.artifactory.search.ArchiveEntrySearchResult+json
        """
        extra = "/archive?name={}&repos={}".format(name, ','.join(repos))

        return cls(auth=auth, art_url=art_url, headers=headers, extra=extra)

    @classmethod
    def gavc(cls, group=None, artifact=None, version=None, classifier=None, repos=[], auth=None, art_url=DEFAULT_URL,
             props=False, info=False):
        """
        Description: Search by Maven coordinates: GroupId, ArtifactId, Version & Classifier.
        Search must contain at least one argument. Can limit search to specific repositories (local and remote-cache).
        Since: 2.2.0
        Security: Requires a privileged user (can be anonymous)
        Usage: GET /api/search/gavc?[g=groupId][&a=artifactId][&v=version][&c=classifier][&repos=x[,y]]
        Headers (Optionally):
            X-Result-Detail: info (To add all extra information of the found artifact),
            X-Result-Detail: properties (to get the properties of the found artifact),
            X-Result-Detail: info, properties (for both).
        Produces: application/vnd.org.jfrog.artifactory.search.GavcSearchResult+json
        """

        gavc = ["{}={}".format(x, y) for x, y in {"g": group, "a": artifact, "v": version, "c": classifier}.items() if y]
        if not gavc:
            return {"Message": "Not Enough Arguments, Provide At Least One"}
        gavc = "&".join(gavc)
        headers = cls.get_headers(info, props)
        extra = "/gavc?={}{}".format(gavc, cls.get_repos(repos))

        return cls(auth=auth, art_url=art_url, headers=headers, extra=extra)

    @classmethod
    def props(cls, repos=None, auth=None, art_url=DEFAULT_URL):
        pass

    @staticmethod
    def get_headers(info, props, headers={}):
        if info:
            headers["X-Result-Detail"] = "info"
            if props:
                headers["X-Result-Detail"] = "info, properties"
        elif props:
            headers["X-Result-Detail"] = "properties"
        return headers

    @staticmethod
    def get_repos(repos):
        if not repos:
            return ""
        else:
            return "&repos={}".format(','.join(repos))


    def execute(self):
        full_url = "{}api/search{}".format(self.art_url, self.extra)
        resp = requests.get(url=full_url, auth=self.auth, headers=self.headers)
        return eval(resp.text)
