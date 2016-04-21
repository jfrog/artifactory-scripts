#!/usr/bin/python2
import sys
import json
import base64
import urllib2
import getpass
import argparse

class DisableLogin():
    def __init__(self, args):
        self.url = args.url[0]
        if self.url[-1] != '/': self.url += '/'
        self.verbose = args.verbose
        # initialize the exit status
        self.status = 0
        # if any auth argument was provided, process it
        self.auth = self.initAuth(args.user)
        # get the list of users, and iterate over it
        self.log("Getting list of users ...")
        for user in self.getUserList():
            # get more info about the user
            self.log("Checking user " + user + " ...")
            userjson = self.getUserInfo(user)
            # ensure the user is both a non-admin and an external user
            # NOTE: An external user that last logged in with a password will be
            # considered to be an internal user, and will be skipped. This is an
            # effect of the way Artifactory handles user realms.
            if userjson['admin'] == True:
                self.log("User " + user + " is an admin user, skipping.")
            elif userjson['name'] == 'anonymous':
                self.log("Anonymous user, skipping.")
            elif userjson['realm'] == 'internal':
                self.log("User " + user + " is an internal user, skipping.")
            else:
                # disable the user's password
                self.log("Updating user " + user + ".")
                self.updateUser(user)
        self.log("Done.")

    # get a list of names of all users on the Artifactory instance
    def getUserList(self):
        req = urllib2.Request(self.url + 'api/security/users')
        req.add_header('Authorization', self.auth)
        return map(lambda x: x['name'], json.load(urllib2.urlopen(req)))

    # given a username, get data for that user and return as a json
    def getUserInfo(self, user):
        req = urllib2.Request(self.url + 'api/security/users/' + user)
        req.add_header('Authorization', self.auth)
        return json.load(urllib2.urlopen(req))

    # given a username, set that user's internalPasswordDisabled to true
    def updateUser(self, user):
        req = urllib2.Request(self.url + 'api/security/users/' + user)
        req.add_data('{"internalPasswordDisabled":true}')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', self.auth)
        urllib2.urlopen(req)

    # write a log line to stdout
    def log(self, line):
        # write the given line to stdout, if the user passed the verbose flag
        if self.verbose: print line

    # if authentication information is passed as an option, initialize it
    def initAuth(self, auth):
        # initialize the user and password
        userpass = None
        # if there is no auth available, get it from the cli
        if auth == None:
            user = raw_input("Authorization required\nUsername: ")
            userpass = user + ':' + getpass.getpass()
        # if the auth string contains a colon, extract the user and password
        elif ':' in auth:
            alist = auth.split(':', 1)
            userpass = alist[0] + ':' + alist[1]
        # otherwise, just extract the user, and get the password via cli
        else: userpass = auth + ':' + getpass.getpass()
        # format a Basic auth string so we can pass it as a header
        return "Basic " + base64.b64encode(unicode(userpass), "utf-8")

# parse the cli options and return an object, or respond accordingly
def getargs():
    help = [
        "Disable internal (password-based) logins for SSO Artifactory users.",
        "the Artifactory base url",
        "your Artifactory username (or username:password)",
        "print lots of text"]
    parser = argparse.ArgumentParser(description=help[0])
    parser.add_argument('url', nargs=1, help=help[1])
    parser.add_argument('-u', '--user', help=help[2])
    parser.add_argument('-v', '--verbose', action="store_true", help=help[3])
    return parser.parse_args()

if __name__ == "__main__":
    # get the cli options and run the program, then return its status
    # print any HTTP or URL error and exit
    try: sys.exit(DisableLogin(getargs()).status)
    except urllib2.HTTPError as ex:
        sys.stderr.write("HTTP Error: " + str(ex.code) + " " + ex.reason + "\n")
        sys.exit(1)
    except urllib2.URLError as ex:
        sys.stderr.write("URL Error: " + str(ex.reason) + "\n")
        sys.exit(1)
