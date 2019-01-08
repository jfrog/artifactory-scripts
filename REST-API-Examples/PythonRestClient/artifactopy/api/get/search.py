import requests
import time
DEFAULT_URL = "http://localhost:8081/artifactory/"

"""
==========
TODO
-----

GET /api/search/dates?[from=fromVal][&to=toVal][&repos=x[,y]][&dateFields=c[,d]]

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
GET /api/search/prop?[p1=v1,v2][&p2=v3][&repos=x[,y]]
GET /api/search/checksum?md5=md5sum?sha1=sha1sum?sha256=sha256sum[&repos=x[,y]]
GET /api/search/badChecksum?type=md5|sha1[&repos=x[,y]]
GET /api/search/usage?notUsedSince=javaEpochMillis[&createdBefore=javaEpochMillis][&repos=x[,y]]
GET /api/search/creation?from=javaEpochMillis[&to=javaEpochMillis][&repos=x[,y]]

=========
"""


class Search:
    def __init__(self, auth, art_url: str=DEFAULT_URL, extra: str="", headers: dict=None):

        if not headers:
            headers = {}
        if self.art_url[-1] is not '/':
            self.art_url += '/'

        self.auth = auth
        self.art_url = art_url
        self.headers = headers

        self.extra = extra

    @classmethod
    def quick(cls, name, repos=None, auth=None, art_url=DEFAULT_URL, props=False, info=False):
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
        cls.repos = repos
        headers = cls.get_headers(info, props)
        extra = "/artifact?name={}{}".format(name, cls.get_repos(repos))

        return cls(auth=auth, art_url=art_url, headers=headers, extra=extra)

    @classmethod
    def archive(cls, name, repos=None, auth=None, art_url=DEFAULT_URL, headers=None):
        """
        Can limit search to specific repositories (local or caches).
        Since: 2.2.0
        Security: Requires a privileged user (can be anonymous)
        Usage: GET /api/search/archive?name=[archiveEntryName][&repos=x[,y]]
        Produces: application/vnd.org.jfrog.artifactory.search.ArchiveEntrySearchResult+json

        :param name:
        :param repos:
        :param auth:
        :param art_url:
        :param headers:
        :return:
        """
        extra = "/archive?name={}{}".format(name, cls.get_repos(repos))
        return cls(auth=auth, art_url=art_url, headers=headers, extra=extra)

    @classmethod
    def gavc(cls, group: str=None, artifact: str=None, version: str=None, classifier: str=None, repos: str=[], auth=None,
             art_url: str=DEFAULT_URL, props=False, info=False):
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
    def props(cls, properties, repos: list = None, auth=None, art_url: str = None, props=False, info=False):

        """
        Description: Search by properties.
        If no value is specified for a property - assume '*'. Can limit search to specific repositories (local, remote-cache or virtual).
        Since: 2.2.0
        Security: Requires a privileged user (can be anonymous)
        Usage: GET /api/search/prop?[p1=v1,v2][&p2=v3][&repos=x[,y]]
        Headers (Optionally): X-Result-Detail: info (To add all extra information of the found artifact), X-Result-Detail: properties (to get the properties of the found artifact), X-Result-Detail: info, properties (for both).
        Produces: application/vnd.org.jfrog.artifactory.search.MetadataSearchResult+json

        :param props:
        :param repos:
        :param auth:
        :param art_url:
        :return:
        """

        if not properties:
            raise IndexError
        if isinstance(properties, dict):
            props_arg = []
            for key, value in properties.items():
                if isinstance(value, list):
                    props_arg.append("{}={}".format(key, ','.join(value)))
                else:
                    props_arg.append("{}={}".format(key, value))

        headers = cls.get_headers(info, props)
        extra = "/prop?{}{}".format("&".join(props_arg), cls.get_repos(repos))

        return cls(auth=auth, art_url=art_url, headers=headers, extra=extra)

    @classmethod
    def checksum(cls, checksum, cs_type="sha1", repos: list = None, auth=None, art_url: str = None, props=False, info=False):

        """
        Description: Artifact search by checksum (md5, sha1, or sha256)
        Searches return file info URIs. Can limit search to specific repositories (local, remote-cache or virtual).
        Notes: Requires Artifactory Pro
        Since: 2.3.0
        Security: Requires a privileged user (can be anonymous)
        Usage: GET /api/search/checksum?md5=md5sum?sha1=sha1sum?sha256=sha256sum[&repos=x[,y]]
        Headers (Optionally): X-Result-Detail: info (To add all extra information of the found artifact), X-Result-Detail: properties (to get the properties of the found artifact), X-Result-Detail: info, properties (for both).
        Produces: application/vnd.org.jfrog.artifactory.search.ChecksumSearchResult+json
        """
        headers = cls.get_headers(info, props)
        extra = "/checksum?{}={}{}".format(cs_type, checksum, cls.get_repos(repos))

        return cls(auth=auth, art_url=art_url, headers=headers, extra=extra)

    @classmethod
    def bad_checksum(cls, cs_type="sha1", repos: list = None, auth=None, art_url: str = None):

        """
        Description: Find all artifacts that have a bad or missing client checksum values (md5 or sha1)
        Searches return file info uris. Can limit search to specific repositories (local, remote-cache or virtual).
        Notes: Requires Artifactory Pro
        Since: 2.3.4
        Security: Requires a privileged user (can be anonymous)
        Usage: GET /api/search/badChecksum?type=md5|sha1[&repos=x[,y]]
        Produces: application/vnd.org.jfrog.artifactory.search.BadChecksumSearchResult+json

        :param cs_type:
        :param repos:
        :param auth:
        :param art_url:
        :return:
        """

        extra = "/badChecksum?type={}{}".format(cs_type, cls.get_repos(repos))
        return cls(auth=auth, art_url=art_url, extra=extra)

    @classmethod
    def not_downloaded_since(cls, since: int, until: int = 0, repos: list = None, auth=None, art_url: str = None):
        """
        Description: Retrieve all artifacts not downloaded since the specified Java epoch in milliseconds.
        Optionally include only artifacts created before the specified createdBefore date, otherwise only artifacts created before notUsedSince are returned.
        Can limit search to specific repositories (local or caches).
        Since: 2.2.4
        Security: Requires a privileged non-anonymous user.
        Usage: GET /api/search/usage?notUsedSince=javaEpochMillis[&createdBefore=javaEpochMillis][&repos=x[,y]]
        Produces: application/vnd.org.jfrog.artifactory.search.ArtifactUsageResult+json

        :param since:
        :param until:
        :param repos:
        :param auth:
        :param art_url:
        :return:
        """
        if not until:
            until = int(time.time()*1000)

        extra = "/usage?notUsedSince={}&createdBefore={}{}".format(since, until, cls.get_repos(repos))
        return cls(auth=auth, art_url=art_url, extra=extra)

    @classmethod
    def created_in_date_range(cls, since: int, until: int = 0, repos: list = None, auth=None, art_url: str = None):
        """

        Description: Get All Artifacts Created in Date Range
        If 'to' is not specified use now(). Can limit search to specific repositories (local or remote-cache).
        Since: 2.2.0
        Security: Requires a privileged non-anonymous user.
        Usage: GET /api/search/creation?from=javaEpochMillis[&to=javaEpochMillis][&repos=x[,y]]
        Produces: application/vnd.org.jfrog.artifactory.search.ArtifactCreationResult+json

        :param since:
        :param until:
        :param repos:
        :param auth:
        :param art_url:
        :return:
        """
        if not until:
            until = int(time.time()*1000)

        extra = "/usage?notUsedSince={}&createdBefore={}{}".format(since, until, cls.get_repos(repos))
        return cls(auth=auth, art_url=art_url, extra=extra)

    @classmethod
    def date_in_date_range(cls, date_fields, since, until=None, repos: list = None, auth=None, art_url: str = None):
        """
        Description: Get all artifacts with specified dates within the given range. Search can be limited to specific repositories (local or caches).
        Since: 3.2.1
        Security: Requires a privileged non-anonymous user.
        Usage: GET /api/search/dates?[from=fromVal][&to=toVal][&repos=x[,y]][&dateFields=c[,d]]
        Parameters: The from and to parameters can be either a long value for the java epoch (milliseconds since the epoch), or an ISO8601 string value. from is mandatory. If to is not provided, now() will be used instead, and if either are omitted, 400 bad request is returned.
        The dateFields parameter is a comma separated list of date fields that specify which fields the from and to values should be applied to. The date fields supported are: created, lastModified, lastDownloaded.
        It is a mandatory field and it also dictates which fields will be added to the JSON returned.
        If ANY of the specified date fields of an artifact is within the specified range, the artifact will be returned.
        """
        if not until:
            until = int(time.time()*1000)

        extra = "/dates?from={}&to={}{}&dateFields={}".format(since, until, cls.get_repos(repos), ','.join(date_fields))
        return cls(auth=auth, art_url=art_url, extra=extra)

    @classmethod
    def pattern(cls, pattern: str, repo: str = "", auth=None, art_url: str = None):
        """
        Description: Get all artifacts matching the given Ant path pattern
        Since: 2.2.4
        Notes: Requires Artifactory Pro. Pattern "**" is not supported to avoid overloading search results.
        Security: Requires a privileged non-anonymous user.
        Usage: GET /api/search/pattern?pattern=repo-key:this/is/a/*pattern*.war
        Produces: application/vnd.org.jfrog.artifactory.search.PatternResultFileSet+json
        :param pattern:
        :param repo:
        :param auth:
        :param art_url:
        :return:
        """

        if not repo:
            repo, pattern = pattern.split(":")[0], pattern.split(":")[1]
        extra = "/pattern?pattern={}:{}".format(repo, pattern)
        return cls(auth=auth, art_url=art_url, extra=extra)

    @classmethod
    def builds_for_dependency(cls, checksum: str, auth=None, art_url: str = None):
        """
        Description: Find all the builds an artifact is a dependency of (where the artifact is included in the build-info dependencies)
        Notes: Requires Artifactory Pro
        Since: 2.3.4
        Security: Requires a privileged user (can be anonymous)
        Usage: GET /api/search/dependency?sha1=sha1Checksum
        Produces: application/vnd.org.jfrog.artifactory.search.DependencyBuilds+json
        :param checksum:
        :param auth:
        :param art_url:
        :return:
        """
        extra = "/dependency?sha1={}".format(checksum)
        return cls(auth=auth, art_url=art_url, extra=extra)

    @classmethod
    def license(cls, unapproved=1, unknown=1, notfound=0, neutral=0, approved=0, autofind=0, repos: list = None, auth=None, art_url: str = None):

        """
        Description: Search for artifacts that were already tagged with license information and their respective licenses.
        To search by specific license values use Property Search with the 'artifactory.licenses' property.

        When the autofind parameter is specified Artifactory will try to automatically find new license information and return it as part of the result in the found field.
        Please note that this can affect the speed of the search quite dramatically, and will still search only on already-tagged artifacts.

        Default parameter values when unspecified: unapproved=1, unknown=1, notfound=0, neutral=0, approved=0, autofind=0.
        Can limit search to specific repositories (local, remote-cache or virtual).
        :param unapproved:
        :param unknown:
        :param notfound:
        :param neutral:
        :param approved:
        :param autofind:
        :param repos:
        :param auth:
        :param art_url:
        :return:
        """
        extra = "/license?unapproved={}&unknown{}&notfound={}&neutral={}&approved={}&autofind={}{}".format(unapproved,
                                                unknown, notfound, neutral, approved, autofind, cls.get_repos(repos))
        return cls(auth=auth, art_url=art_url, extra=extra)


    @classmethod
    def version_search(cls, group: str=None, artifact: str=None, version: str=None, repos=None,
                       auth=None, art_url: str=DEFAULT_URL, remote=0):

        """
        Description: Search for all available artifact versions by GroupId and ArtifactId in local, remote or virtual repositories.
        Search can be limited to specific repositories (local, remote and virtual) by settings the repos parameter.
        Release/integration versions: Unless the version parameter is specified, both release and integration versions are returned. When version is specified, e.g. 1.0-SNAPSHOT, result includes only integration versions.

        Integration versions are determined by the repository layout of the repositories searched. For integration search to work the repository layout requires an 'Artifact Path Pattern' that contains the baseRev token and then the fileItegRev token with only literals between them.
        Remote searches: By default only local and cache repositories are used. When specifying remote=1, Artifactory searches for versions on remote repositories. NOTE! that this can dramatically slow down the search.
        For Maven repositories the remote maven-metadata.xml is consulted. For non-maven layouts, remote file listing runs for all remote repositories that have the 'List Remote Folder Items' checkbox enabled.
        Filtering results (Artifactory 3.0.2+): The version parameter can accept the * and/or ? wildcards which will then filter the final result to match only those who match the given version pattern.
        Since: 2.6.0
        Notes: Requires Artifactory Pro
        Security: Requires a privileged user (can be anonymous)
        Usage: GET /api/search/versions?[g=groupId][&a=artifactId][&v=version][&remote=0/1][&repos=x[,y]]
        Produces: application/vnd.org.jfrog.artifactory.search.ArtifactVersionsResult+json
        :param group:
        :param artifact:
        :param version:
        :param classifier:
        :param repos:
        :param auth:
        :param art_url:
        :param remote:
        :return:
        """
        gav = ["{}={}".format(x, y) for x, y in {"g": group, "a": artifact, "v": version}.items() if y]
        if not gav:
            return {"Message": "Not Enough Arguments, Provide At Least One"}
        gav = "&".join(gav)
        extra = "/versions?={}{}{}".format(gav, "&remote={}".format(remote), cls.get_repos(repos))

        return cls(auth=auth, art_url=art_url, extra=extra)


    @classmethod
    def latest_version(cls, group: str=None, artifact: str=None, version: str=None, repos=None,
                       auth=None, art_url: str=DEFAULT_URL, remote=0):

        gav = ["{}={}".format(x, y) for x, y in {"g": group, "a": artifact, "v": version}.items() if y]
        if not gav:
            return {"Message": "Not Enough Arguments, Provide At Least One"}
        gav = "&".join(gav)
        extra = "/latestVersion?={}{}{}".format(gav, "&remote={}".format(remote), cls.get_repos(repos))

        return cls(auth=auth, art_url=art_url, extra=extra)

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
