#!/usr/bin/python2
import sys
import json
import base64
import urllib2
import getpass
import argparse

# singleRepoTypeConverter.java
# Special cases:
# - remote:
#   - add vcs if no bower
# - virtual:
#   - add p2 if p2 is enabled
# - all:
#   - add yum if there are any yum settings
#   - vcs and p2
#   - if no other type exists, get mvn, ivy, or gradle from layout

class PackageCheck():
    repoTypeList = ["Bower", "Debian", "Docker", "Gems", "GitLfs",
                    "Npm", "NuGet", "Pypi", "Vagrant"]

    def __init__(self, args):
        self.json = {}
        self.of = sys.stdout
        if args.output_file != None:
            self.of = open(args.output_file, "w")
        vp = args.verbose and not args.json
        self.status = 0
        self.initAuth(args.user)
        baseurl = args.url[0]
        if baseurl[-1] != '/': baseurl += '/'
        baseurl += "api/repositories"
        if vp: self.of.write("Getting repository list\n")
        for data in self.requestData(baseurl):
            if vp: self.of.write("Checking repo '" + data["key"] + "' ... ")
            repourl = baseurl + '/' + data["key"]
            reponame = data["key"] if vp else None
            try: repodata = self.requestData(repourl, reponame)
            except:
                if vp: self.of.write("error\n")
                raise
            typeList = []
            for typ in self.repoTypeList:
                t = "enable" + typ + "Support"
                if t in repodata and repodata[t] == True:
                    typeList.append(typ)
            self.json[data["key"]] = {"status": len(typeList) <= 1,
                                      "types": typeList[:]}
            if len(typeList) > 1:
                self.status = 1
                msg = "\tRepo has conflicting types: " + typeList.pop(0)
                for typ in typeList:
                    msg += ", " + typ
                if vp: self.of.write("failed\n" + msg + "\n")
                elif not args.json:
                    self.of.write("Checking repo '" + data["key"]
                                  + "' ... failed\n" + msg + "\n")
            elif vp: self.of.write("passed\n")
        if args.json:
            newjson = self.json
            if not args.verbose:
                newjson = {}
                for repo in self.json:
                    if not self.json[repo]["status"]:
                        newjson[repo] = self.json[repo]
            self.of.write(json.dumps(newjson))

    def requestData(self, url, reponame = None):
        req = urllib2.Request(url)
        conn = None
        if self.auth == None:
            try: conn = urllib2.urlopen(req)
            except urllib2.HTTPError as ex:
                if ex.code == 401:
                    req.add_header('Authorization', self.getAuth())
                    if reponame != None and self.of == sys.stdout:
                        self.of.write("Checking repo '" + reponame + "' ... ")
                    conn = urllib2.urlopen(req)
                else: raise ex
        else:
            req.add_header('Authorization', self.getAuth())
            conn = urllib2.urlopen(req)
        return json.load(conn)

    def initAuth(self, auth):
        if auth == None:
            self.auth = None
            return
        user, pasw = None, None
        if ':' in auth:
            alist = auth.split(':', 1)
            user, pasw = alist[0], alist[1]
        else:
            user = auth
            pasw = getpass.getpass()
        userpass = user + ':' + pasw
        self.auth = "Basic " + base64.b64encode(unicode(userpass), "utf-8")

    def getAuth(self):
        if self.auth == None:
            user = raw_input("Authorization required\nUsername: ")
            pasw = getpass.getpass()
            userpass = user + ':' + pasw
            self.auth = "Basic " + base64.b64encode(unicode(userpass), "utf-8")
        return self.auth

def getargs():
    help = [
        "Check for Artifactory repositories with multiple package types.",
        "the Artifactory base url",
        "your Artifactory username (or username:password)",
        "output to the given file, rather than to stdout",
        "output status of all repositories, rather than just problematic ones",
        "output a json object, rather than plaintext"]
    parser = argparse.ArgumentParser(description=help[0])
    parser.add_argument('url', nargs=1, help=help[1])
    parser.add_argument('-u', '--user', help=help[2])
    parser.add_argument('-o', '--output-file', help=help[3])
    parser.add_argument('-v', '--verbose', action="store_true", help=help[4])
    parser.add_argument('-j', '--json', action="store_true", help=help[5])
    return parser.parse_args()

if __name__ == "__main__":
    try: sys.exit(PackageCheck(getargs()).status)
    except urllib2.HTTPError as ex:
        sys.stderr.write("HTTP Error: " + str(ex.code) + " " + ex.reason + "\n")
        sys.exit(1)
    except urllib2.URLError as ex:
        sys.stderr.write("URL Error: " + str(ex.reason) + "\n")
        sys.exit(1)
