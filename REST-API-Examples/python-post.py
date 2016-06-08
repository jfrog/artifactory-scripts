import requests
import json

#enter credentials
username = "admin"
password = "password"
artifactory = "http://127.0.0.1:8081/artifactory/" #artifactory URL
api = "api/trash/empty" #you can change this API URL to any API method you'd like to use, this URL will empty the trash can
url = artifactory + api

r = requests.post(url, auth = (username, password)) #this script is only for API methods that use POST
print r.content

