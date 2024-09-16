import requests
import json
import sys
import re

username = "admin"
password = "password"
artifactory = "https://127.0.0.1:8081/artifactory/" # change this artifactory URL
#make sure to clarify if HTTP or HTTPS
	
def deletebuild(buildtodelete,idtodelete):
	print buildtodelete + idtodelete
	r = requests.delete(buildtodelete + idtodelete, auth= (username,password))

def inspectbuildjson(buildjson,buildjsonid):
	#looks through every single build json in every build ID
	r = requests.get(buildjson+buildjsonid, auth = (username, password))
	buildinfo = json.loads(r.text)

	if "statuses" not in buildinfo["buildInfo"] or len(buildinfo["buildInfo"]["statuses"]) == 0:
		print "Deleting this build: " + buildjson + buildjsonid
		deletebuild(buildjson,re.sub('/', '?buildNumbers=', buildjsonid))
	else:
		print "Keeping this build: " + buildjson + buildjsonid +  " - " + buildinfo["buildInfo"]["statuses"][0]["status"]

def findbuildnumbers(buildname):
	#finds all build ID's from all build projects
	url = buildname
	r = requests.get(url, auth = (username, password))
	build_data = json.loads(r.text)
	for item in build_data["buildsNumbers"]:
		inspectbuildjson(url,item["uri"])

def getallbuilds():
	#looks through all build projects
	buildurl = "api/build"
	url = artifactory + buildurl
	r = requests.get(url, auth = (username, password))
	json_data = json.loads(r.text)
	for item in json_data["builds"]:
		findbuildnumbers(url + item["uri"])


getallbuilds()