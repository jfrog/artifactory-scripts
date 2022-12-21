require "rubygems"
require "rest_client"
require "json"

#enter credentials
user_name = 'admin' #enter artifactory username
password= 'password' #enter artifactory password 
artifactory  = "http://127.0.0.1:8081/artifactory/" #enter artifactory base URL
api = "api/security/users" #don't touch
api2 = "api/security/users/" #don't touch

#gets all users in artifactory
url = artifactory + api
site = RestClient::Resource.new(url, user_name, password)
response = site.get(:accept=>"application/json")
string = response.body
parsed = JSON.parse(string)
parsed.map
emailnum = 0

while true do
	if parsed[emailnum].nil? #make sure it's not null
		break
	else
		checkmail = parsed[emailnum]["name"] #grabs username
		url = artifactory + api2 + checkmail #makes REST API call for each username
		site2 = RestClient::Resource.new(url, user_name, password)
		response2 = site2.get(:accept=>"application/json")
		string2 = response2.body
		parsed2 = JSON.parse(string2)
		parsed2.map
		puts parsed2["email"] #prints email
		emailnum +=1
	end
end
