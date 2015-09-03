#!/usr/bin/python2
import sys
import json
import base64
import urllib2
import getpass
import argparse
import xml.etree.ElementTree as ET

class PackageCheck():
    repoTypeList = ["NuGet", "Gems", "Npm", "Bower", "Debian",
                    "Pypi", "Docker", "Vagrant", "GitLfs"]

    def __init__(self, args):
        # initialize a json representation, in case we need json output
        self.json = {}
        # set the output file, if specified
        self.of = sys.stdout
        if args.output_file != None:
            self.of = open(args.output_file, "w")
        # whether to print most logs (when the output is verbose plaintext)
        vp = args.verbose and not args.json
        # initialize the exit status
        self.status = 0
        # if any auth argument was provided, process it
        self.initAuth(args.user)
        # print initial log message, if we're doing plaintext output
        if not args.json: self.of.write("Getting repository list\n")
        # get a list of repos, and iterate over them
        for data in self.getRepoList(args):
            if vp: self.of.write("Checking repo '" + data["key"] + "' ... ")
            # get the data for this repository
            try: repodata = self.getRepoData(data["key"], args)
            except:
                if vp: self.of.write("error\n")
                raise
            # get a list of package types the repo is configured with
            typeList = self.collectTypes(repodata)
            # if there are multiple, fail the current status and log errors
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
        # if we're outputting json, filter it appropriately and print
        if args.json:
            newjson = self.json
            if not args.verbose:
                newjson = {}
                for repo in self.json:
                    if not self.json[repo]["status"]:
                        newjson[repo] = self.json[repo]
            self.of.write(json.dumps(newjson))
        # close the output stream
        self.of.close()

    # given a repository data dict, extract and return a list of package types
    def collectTypes(self, repodata):
        # initialize an empty list to hold package types
        typeList = []
        # check for all the simple package support flags
        for typ in self.repoTypeList:
            t = "enable" + typ + "Support"
            if t in repodata and repodata[t] == True:
                typeList.append(typ)
        # check for yum support
        yum = ["calculateYumMetadata", "yumRootDepth", "yumGroupFileNames"]
        if yum[0] in repodata and repodata[yum[0]] == True:
            typeList.append("Yum")
        elif repodata["rclass"] != "virtual":
            if ((yum[1] in repodata and repodata[yum[1]] > 0)
                or (yum[2] in repodata and len(repodata[yum[2]]) > 0)):
                typeList.append("Yum")
        # check for vcs support if there is no bower support
        if repodata["rclass"] == "remote" and "Bower" not in typeList:
            vcs = "enableVcsSupport"
            if vcs in repodata and repodata[vcs] == True:
                typeList.append("Vcs")
        # check for p2 support
        p2 = "p2Support"
        if p2 in repodata and repodata[p2] == True:
            typeList.append("P2")
        # if there are no package types so far, grab one from the layout
        if len(typeList) == 0:
            layout = None
            if "repoLayoutRef" in repodata:
                layout = repodata["repoLayoutRef"]
            if layout == "ivy-default":
                typeList.append("Ivy")
            elif layout == "gradle-default":
                typeList.append("Gradle")
            else: typeList.append("Maven")
        # add the resulting type list to the json object, and return it
        self.json[repodata["key"]] = {"status": len(typeList) <= 1,
                                      "types": typeList[:]}
        return typeList

    # return a json object representing the list of repositories
    def getRepoList(self, args):
        if args.xml:
            # if we're reading from an xml, precalculate all the data
            # the list of all the repo keys, to return
            repoList = []
            # the precalculated data, to access later
            self.repodata = {}
            # parse the given xml file
            tree = None
            try:
                tree = ET.parse(args.url[0])
            except IOError as ex:
                err = "Error: Could not open file: " + str(ex) + "\n"
                sys.stderr.write(err)
                sys.exit(1)
            # the default namespace
            root = tree.getroot()
            ns = root.tag[:root.tag.index('}') + 1]
            # iterate over the different repository types
            for name in "local", "remote", "virtual":
                # iterate over all repositories for each type
                for repo in root.iter(ns + name + "Repository"):
                    # initialze the json element with its repo type
                    elem = {"rclass": name}
                    # add all the given properties to the json element
                    for el in repo:
                        # remove the namespace
                        tag = el.tag[len(ns):]
                        # if the value is an integer, parse it
                        try: elem[tag] = int(el.text)
                        except ValueError:
                            # if the value is a boolean, parse it
                            # if not, treat it as a string
                            if el.text == "true" or el.text == "false":
                                elem[tag] = el.text == "true"
                            else: elem[tag] = el.text
                    # add a P2 support property if there is an enabled P2
                    p2 = repo.find(ns + "p2")
                    if name == "virtual" and p2 != None:
                        enabled = p2.find(ns + "enabled")
                        if enabled != None:
                            elem["p2Support"] = enabled.text == "true"
                    # add the element to the repo list and the json object
                    repoList.append({"key": elem["key"]})
                    self.repodata[elem["key"]] = elem
            # return the repository list
            return repoList
        else:
            # otherwise, request the data via the REST
            self.baseurl = args.url[0]
            if self.baseurl[-1] != '/': self.baseurl += '/'
            self.baseurl += "api/repositories"
            return self.requestData(self.baseurl)

    # return a json object containing repository data for the given key
    def getRepoData(self, repoKey, args):
        if args.xml:
            # if we're reading from an xml, just get the precalculated data
            return self.repodata[repoKey]
        else:
            # otherwise, request the data via the REST
            vp = args.verbose and not args.json
            repourl = self.baseurl + '/' + repoKey
            reponame = data["key"] if vp else None
            return self.requestData(repourl, reponame)

    # given a url, run a get request, and parse and return the resulting json
    def requestData(self, url, reponame = None):
        # create a request for the given resource
        req = urllib2.Request(url)
        conn = None
        if self.auth == None:
            # if authorization info does not exist, attempt to connect
            try: conn = urllib2.urlopen(req)
            except urllib2.HTTPError as ex:
                # if authorization is required, ask the user, and try again
                if ex.code == 401:
                    req.add_header('Authorization', self.getAuth())
                    if reponame != None and self.of == sys.stdout:
                        self.of.write("Checking repo '" + reponame + "' ... ")
                    conn = urllib2.urlopen(req)
                else: raise ex
        else:
            # if authorization info already exists, attempt to connect
            req.add_header('Authorization', self.getAuth())
            conn = urllib2.urlopen(req)
        # once a connection is established, read out the json object
        return json.load(conn)

    # if authentication information is passed as an option, initialize it
    def initAuth(self, auth):
        # if no auth data is passed in, do nothing for now
        if auth == None:
            self.auth = None
            return
        # initialize the user and password
        user, pasw = None, None
        if ':' in auth:
            # if the auth string contains a colon, extract the user and password
            alist = auth.split(':', 1)
            user, pasw = alist[0], alist[1]
        else:
            # otherwise, just extract the user, and get the password via cli
            user = auth
            pasw = getpass.getpass()
        # format a Basic auth string so we can pass it as a header
        userpass = user + ':' + pasw
        self.auth = "Basic " + base64.b64encode(unicode(userpass), "utf-8")

    # get the authentication information, and return it
    def getAuth(self):
        # if there is no auth available, get it from the cli
        if self.auth == None:
            user = raw_input("Authorization required\nUsername: ")
            pasw = getpass.getpass()
            # format a Basic auth string so we can pass it as a header
            userpass = user + ':' + pasw
            self.auth = "Basic " + base64.b64encode(unicode(userpass), "utf-8")
        # return the newly created (or the old) auth string
        return self.auth

# parse the cli options and return an object, or respond accordingly
def getargs():
    help = [
        "Check for Artifactory repositories with multiple package types.",
        "the Artifactory base url, or a path to the xml config file",
        "your Artifactory username (or username:password)",
        "output to the given file, rather than to stdout",
        "get data from an Artifactory config xml file, rather than via REST",
        "output status of all repositories, rather than just problematic ones",
        "output a json object, rather than plaintext"]
    parser = argparse.ArgumentParser(description=help[0])
    parser.add_argument('url', nargs=1, help=help[1])
    parser.add_argument('-u', '--user', help=help[2])
    parser.add_argument('-o', '--output-file', help=help[3])
    parser.add_argument('-x', '--xml', action="store_true", help=help[4])
    parser.add_argument('-v', '--verbose', action="store_true", help=help[5])
    parser.add_argument('-j', '--json', action="store_true", help=help[6])
    return parser.parse_args()

if __name__ == "__main__":
    # get the cli options and run the package check, then return its status
    # print any HTTP or URL error and exit
    try: sys.exit(PackageCheck(getargs()).status)
    except urllib2.HTTPError as ex:
        sys.stderr.write("HTTP Error: " + str(ex.code) + " " + ex.reason + "\n")
        sys.exit(1)
    except urllib2.URLError as ex:
        sys.stderr.write("URL Error: " + str(ex.reason) + "\n")
        sys.exit(1)
