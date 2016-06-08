require "rubygems"
require "rest_client"
require "json"

#enter credentials
user_name = 'admin'
password= 'password'


artifactory  = "http://127.0.0.1:8081/artifactory/"
api = "api/trash/empty" #you can change this API URL to any API method you'd like to use, this URL will empty the trash can
url = artifactory + api

site = RestClient::Resource.new(url, user_name, password)

begin
  response = site.post(:accept=>'application/json') #this script is ONLY for POST commands
  puts "response_code: #{response.code} \n response_body: #{response.body} \n"
rescue RestClient::Exception => exception
  puts "X-Request-Id : #{exception.response.headers[:x_request_id]}"
  puts "Response Code: #{exception.response.code} \n Response Body: #{exception.response.body} \n"
end