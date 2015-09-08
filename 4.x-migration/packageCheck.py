#!/usr/bin/python2
import sys
import json
import base64
import urllib2
import getpass
import argparse
import xml.etree.ElementTree as ET

class PackageCheck():
    def __init__(self, args):
        # initialize the exit status
        self.status = 0
        # set the output file, if specified
        outf = None
        try:
            if args.output_file != None and args.output_file != '-':
                outf = open(args.output_file, 'w')
            else: outf = sys.stdout
        except (OSError, IOError) as ex:
            err = "Error: Could not open file: " + str(ex) + "\n"
            sys.stderr.write(err)
            sys.exit(1)
        # manage the output file
        with outf:
            # initialize a json representation, in case we need json output
            jsonobj = {}
            # if any auth argument was provided, process it
            auth = self.initAuth(args.user)
            # print initial log message, if we're doing plaintext output
            if not args.json: outf.write("Getting repository list\n")
            # get a list of repos, and iterate over them
            for key, types in self.getRepoList(args, auth):
                typelen, stat, msg = len(types), "passed", None
                # add the type list to the json object
                if args.json and (args.verbose or typelen > 1):
                    jsonobj[key] = {"status": typelen <= 1, "types": types}
                # if there are multiple package types, fail the current status
                if typelen > 1:
                    self.status = 1
                    stat = "failed"
                    msg = "\tRepo has conflicting types: " + ", ".join(types)
                # print the status message if necessary
                if not args.json and (args.verbose or typelen > 1):
                    outf.write("Checking repo '" + key + "' ... " + stat + "\n")
                    if msg != None: outf.write(msg + "\n")
            # if we're outputting json, print some json
            if args.json: outf.write(json.dumps(jsonobj))

    # given a repository xml node, extract and return a list of package types
    def collectTypes(self, ns, rclass, data):
        # a list of all the simple package types
        repoTypeList = ["NuGet", "Gems", "Npm", "Bower", "Debian",
                        "Pypi", "Docker", "Vagrant", "GitLfs"]
        # initialize an empty list to hold package types
        typeList = []
        # check for all the simple package support flags
        for typ in repoTypeList:
            t = data.find(ns + "enable" + typ + "Support")
            if t != None and t.text == "true": typeList.append(typ)
        # check for yum support
        yumc = data.find(ns + "calculateYumMetadata")
        yumg = data.find(ns + "yumGroupFileNames")
        yumd = data.find(ns + "yumRootDepth")
        if yumc != None and yumc.text == "true": typeList.append("Yum")
        elif rclass != "virtual":
            try:
                if ((yumg != None and len(yumg.text) > 0)
                    or (yumd != None and int(yumd.text) > 0)):
                    typeList.append("Yum")
            except: pass
        # check for vcs support if there is no bower support
        if rclass == "remote" and "Bower" not in typeList:
            vcs = data.find(ns + "enableVcsSupport")
            if vcs != None and vcs.text == "true": typeList.append("Vcs")
        # check for p2 support
        if rclass == "remote":
            p2 = data.find(ns + "p2Support")
            if p2 != None and p2.text == "true": typeList.append("P2")
        elif rclass == "virtual":
            p2 = data.find(ns + "p2")
            if p2 != None:
                enabled = p2.find(ns + "enabled")
                if enabled != None and enabled.text == "true":
                    typeList.append("P2")
        # if there are no package types so far, grab one from the layout
        if len(typeList) == 0:
            layout = data.find(ns + "repoLayoutRef")
            if layout != None:
                if layout.text == "ivy-default": typeList.append("Ivy")
                elif layout.text == "gradle-default": typeList.append("Gradle")
                else: typeList.append("Maven")
            else: typeList.append("Maven")
        return typeList

    # return the list of repositories
    def getRepoList(self, args, auth):
        tree = None
        # if we're reading from an xml, parse the given xml file
        if args.xml:
            fname = args.url[0]
            if fname == '-': fname = sys.stdin
            try: tree = ET.parse(fname)
            except (OSError, IOError) as ex:
                err = "Error: Could not open file: " + str(ex) + "\n"
                sys.stderr.write(err)
                sys.exit(1)
        # otherwise, request the data via the REST api
        else:
            url = args.url[0]
            if url[-1] != '/': url += '/'
            url += "api/system/configuration"
            # create a request for the configuration
            req = urllib2.Request(url)
            req.add_header('Authorization', self.getAuth(auth))
            # read out the xml object
            tree = ET.parse(urllib2.urlopen(req))
        # the default namespace
        root = tree.getroot()
        ns = root.tag[:root.tag.index('}') + 1]
        # iterate over the different repository types
        for name in "local", "remote", "virtual":
            # iterate over all repositories for each type
            for repo in root.iter(ns + name + "Repository"):
                # send back the results
                yield (repo.find(ns + "key").text,
                       self.collectTypes(ns, name, repo))

    # if authentication information is passed as an option, initialize it
    def initAuth(self, auth):
        # if no auth data is passed in, do nothing for now
        if auth == None: return None
        # initialize the user and password
        userpass = None
        # if the auth string contains a colon, extract the user and password
        if ':' in auth:
            alist = auth.split(':', 1)
            userpass = alist[0] + ':' + alist[1]
        # otherwise, just extract the user, and get the password via cli
        else: userpass = auth + ':' + getpass.getpass()
        # format a Basic auth string so we can pass it as a header
        return "Basic " + base64.b64encode(unicode(userpass), "utf-8")

    # get the authentication information, and return it
    def getAuth(self, auth):
        # if there is no auth available, get it from the cli
        if auth == None:
            user = raw_input("Authorization required\nUsername: ")
            pasw = getpass.getpass()
            # format a Basic auth string so we can pass it as a header
            userpass = user + ':' + pasw
            auth = "Basic " + base64.b64encode(unicode(userpass), "utf-8")
        # return the newly created (or the old) auth string
        return auth

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
