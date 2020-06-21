#!/usr/bin/env python3
import sys
import json
import base64
import getpass
import argparse
import urllib.request
import urllib.error
import logging

FORMAT = "[%(asctime)s %(levelname)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger = logging.getLogger()

# check the integrity, and print the results to stdout or the specified file
def runCheck(conn, outfile):
    # open the output file for writing, or use stdout
    try:
        if outfile != None and outfile != '-':
            outf = open(outfile, 'w')
        else: outf = sys.stdout
    except (OSError, IOError) as ex:
        print('Error: Could not open file: {}'.format(ex), file=sys.stderr)
        sys.exit(1)
    count = 0
    # iterate through every artifact, and print the ones that don't check
    with outf:
        for repo in getRepoList(conn):
            logger.debug('Checking repository: %s', repo)
            for artif in getArtifactList(conn, repo):
                logger.debug('Checking: repo=%s artifact=%s', repo, artif)
                response = checkArtifact(conn, repo, artif)
                if response != None:
                    count += 1
                    print(response, file=outf)
        plural = 'artifacts'
        if count == 1: plural = 'artifact'
        msg = 'Check complete, found {} conspicuous {}.'.format(count, plural)
        print(msg, file=outf)

# request a list of all local repositories, and return them
def getRepoList(conn):
    logger.debug('Listing repositories...')
    stat, msg = runRequest(conn, '/api/repositories?type=local')
    if stat != 200:
        print('Error getting repository list: {}'.format(msg), file=sys.stderr)
        sys.exit(1)
    res = list(map(lambda x: x['key'], json.loads(msg.decode("utf-8"))))
    logger.debug('Found %d repositories', len(res))
    return res

# request a list of all artifacts in a repository, and return them
def getArtifactList(conn, repo):
    logger.debug('Listing artifacts in repository: %s', repo)
    stat, msg = runRequest(conn, '/api/storage/{}?list&deep=1'.format(repo))
    if stat != 200:
        err = "Error getting artifact list for '{}': {}".format(repo, msg)
        print(err, file=sys.stderr)
        sys.exit(1)
    res = list(
        map(lambda x: x['uri'], json.loads(msg.decode("utf-8"))['files'])
    )
    logger.debug('Found %d artifacts in repository: %s', len(res), repo)
    return res

# request an artifact, and return a summary of the artifact if the response code
# wasn't 200 or 404
def checkArtifact(conn, repo, artif):
    stat, msg = runRequest(conn, '/{}{}'.format(repo, artif), skipmsg=True)
    if stat in (200, 404): return None
    return '[{} {}] {}{}'.format(stat, msg, repo, artif)

# send a request to the server, and return the response code and body
def runRequest(conn, path, skipmsg=False):
    urlbase, auth = conn
    req = urllib.request.Request(urlbase + path)
    req.add_header('Authorization', auth)
    try:
        with urllib.request.urlopen(req) as resp:
            stat = resp.getcode()
            if skipmsg and stat in (200, 404): msg = None
            else: msg = resp.read()
    except urllib.error.HTTPError as ex:
        stat, msg = ex.code, ex.reason
    except urllib.error.URLError as ex:
        stat, msg = 0, ex.reason
    return stat, msg

# collect authentication information and return a Basic value
def getAuth(auth):
    if auth == None:
        # if no auth data was passed in, interactively ask for it
        user = input("Authorization required\nUsername: ")
        pasw = getpass.getpass()
        userpass = '{}:{}'.format(user, pasw)
    elif ':' not in auth:
        # if only the username was provided, interactively ask for the password
        userpass = '{}:{}'.format(auth, getpass.getpass())
    else: userpass = auth
    # encode the credentials in base64 and return a Basic value
    b64 = base64.b64encode(userpass.encode("utf-8")).decode("utf-8")
    return "Basic {}".format(b64)

# parse the cli options and return an object, or respond accordingly
def getArgs():
    help = [
        "Check Artifactory for filestore integrity.",
        "the Artifactory base url",
        "your Artifactory username (or username:password)",
        "output to the given file, rather than to stdout",
        "log verbose output while retrieving artifacts"
    ]
    parser = argparse.ArgumentParser(description=help[0])
    parser.add_argument('url', nargs=1, help=help[1])
    parser.add_argument('-u', '--user', help=help[2])
    parser.add_argument('-o', '--output-file', help=help[3])
    parser.add_argument(
        '-v', '--verbose', dest='verbose', help=help[4], action='store_true',
        default=False
    )
    return parser.parse_args()

if __name__ == "__main__":
    # get the base url and the authentication information from the commandline,
    # and start the integrity check
    args = getArgs()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    auth = getAuth(args.user)
    urlbase = args.url[0]
    if urlbase[-1] == '/': urlbase = urlbase[:-1]
    logger.debug('Running against: %s', urlbase)
    runCheck((urlbase, auth), args.output_file)
