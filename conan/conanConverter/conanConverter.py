#!/usr/bin/env python2

import re
import sys
import json
import urllib2
import base64

class PostRequest(urllib2.Request):
    def __init__(self, *args, **kwargs):
        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self, *args, **kwargs):
        return 'POST'

def getaql(repo):
    query = {}
    query['repo'] = repo
    query['type'] = 'folder'
    query['depth'] = '4'
    query['path'] = {'$match': '*/*.*.*/*'}
    return 'items.find(' + json.dumps(query) + ').include("name","repo","path")'

def reqaql(url, user, pasw, repo):
    path = url
    if path[-1] != '/': path += '/'
    path += 'api/search/aql'
    auth = 'Basic ' + base64.b64encode(user + ':' + pasw)
    headers = {'Content-Type': 'text/plain', 'Authorization': auth}
    req = PostRequest(path, getaql(repo), headers)
    resp = urllib2.urlopen(req)
    return json.load(resp)

def reqcp(url, user, pasw, pathfrom, pathto):
    path = url
    if path[-1] != '/': path += '/'
    path += 'api/copy' + pathfrom + '?to=' + pathto #+ '&dry=1'
    auth = 'Basic ' + base64.b64encode(user + ':' + pasw)
    headers = {'Content-Type': 'text/plain', 'Authorization': auth}
    req = PostRequest(path, None, headers)
    return json.load(urllib2.urlopen(req))

def main():
    if len(sys.argv) != 6:
        print("Usage: ./conanConverter.py <artifactory url> <username> <password> <source repository> <destination repository>")
        return
    url, user, pasw, repo1, repo2 = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    aqlresp = reqaql(url, user, pasw, repo1)
    for item in aqlresp['results']:
        match = re.match(r'^([^/]+)/(\d+\.\d+\.\d+[^/]*)/([^/]+)$', item['path'])
        if match == None: continue
        newpath = match.group(3) + '/' + match.group(1) + '/' + match.group(2)
        pathto = '/' + repo2 + '/' + newpath + '/' + item['name']
        pathfrom = '/' + item['repo'] + '/' + item['path'] + '/' + item['name']
        print("#### Copying " + pathfrom + " to " + pathto)
        print("     " + json.dumps(reqcp(url, user, pasw, pathfrom, pathto)))

if __name__ == '__main__': main()
