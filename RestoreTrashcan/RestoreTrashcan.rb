require "rubygems"
require "rest_client"
require "json"

# Insert the correct url, and an administrator username and password
artifactory = "http://artifactorydomain.org:8081/artifactory"
user_name = 'admin'
password= 'password'

url = artifactory + "/api/storage/auto-trashcan?list&deep=1"
site = RestClient::Resource.new(url, user_name, password)
response = site.get(:accept=>"application/json")
parsed = JSON.parse(response.body)

parsed["files"].each { |artifact|
  path = artifact["uri"]
  restoreurl = artifactory + "/api/trash/restore" + path + "?to=" + path
  site = RestClient::Resource.new(restoreurl, user_name, password)
  begin
    response = site.post(nil)
    puts "[#{response.code}] #{path}"
  rescue RestClient::Exception => ex
    puts "[#{ex.http_code()}] #{path}"
    puts ex.http_body()
  end
}
