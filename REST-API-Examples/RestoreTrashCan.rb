require "rubygems"
require "rest_client"
require "json"
#This script restores every file inside the Trashcan
user_name = 'admin' #change this
password= 'password' #change this
repo = "auto-trashcan"
artifactory  = "http://127.0.0.1:8081/artifactory/api/storage/" #change this
listfolders = "?list&deep=1&listFolders=1"
url = artifactory + repo + listfolders
site = RestClient::Resource.new(url, user_name, password)
response = site.get(:accept=>"application/json")
string = response.body
parsed = JSON.parse(string)
parsed.map


while true
	i = 0
	trashedartifacts = parsed["files"][i]["uri"]
	restoreurl = "http://127.0.0.1:8081/artifactory/api/trash/restore" + trashedartifacts + "?to=" + trashedartifacts #change my artifactory home
	site2 = RestClient::Resource.new(restoreurl, user_name, password)
	response2 = site2.post(:accept=>"application/json")
	string2 = response2.body
	puts string2
	i+=1
end

