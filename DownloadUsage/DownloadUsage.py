import sys
import re
import requests
import json
from colorama import Fore, Back, Style
import colorama

username = "admin" #EDIT THIS
password = "password" #EDIT THIS
artifactory = "http://127.0.0.1:8081" #EDIT THIS
apiurl = "/artifactory/api/storage/" 

if len(sys.argv) != 2:
    print('Usage: python DownloadUsage.py access.log')
    print('Edit your credentials within this script!')
    sys.exit(0)

readfile = sys.argv[1]
totalbytes = 0
notfound = 0

with open(readfile) as f:
    print "Parsing Access Log..."
    for line in f:
        try:
            p = re.compile(ur'(\d*)-(\d*-\d*\d*......)(........)(.*])(.*)(:)(.*)(for)(.)(.*)(\/)(.*)(\.)')
            match = re.match(p,line)
            if "ACCEPTED DOWNLOAD" in match.group(4):
                checkfile = match.group(5) + "/" + match.group(7)
                url = artifactory + apiurl + checkfile
                r = requests.get(url, auth = (username, password))
                json_data = r.content 
                parsedata = json.loads(json_data)
                jsonbytes = int(parsedata["size"])
                totalbytes += jsonbytes
        except Exception:
            notfound +=1 #An error may occur if the file has been deleted. This script is not perfect.
            pass
print Fore.RED + "Could not find",(notfound),"artifacts(most likely deleted)" 
print Fore.GREEN + "Total download usage:",(totalbytes/1000000),"MB"
print (Style.RESET_ALL)
exit()
