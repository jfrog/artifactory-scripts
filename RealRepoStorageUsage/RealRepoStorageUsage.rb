require "rubygems"
require "rest_client"
require "json"
require "filesize"

if ARGV.empty?
    puts "Usage: ruby RealUsage.rb $repositoryname"
    exit
end

repo = ARGV[0] #first argument should be repository to parse
user_name = 'admin' #change this
password= 'password' #change this
artifactory  = "http://127.0.0.1:8081/artifactory/api/storage/" #change this
listfolders = "?list&deep=1&listFolders=1"

url = artifactory + repo + listfolders
site = RestClient::Resource.new(url, user_name, password)
response = site.get(:accept=>"application/json")
string = response.body
parsed = JSON.parse(string)
parsed.map
array = Array.new
$i = 0
artifacts = parsed["files"].count
totalbytes = 0

while $i < artifacts do 
	sha1 = parsed["files"][$i]["sha1"]
	size = parsed["files"][$i]["size"]
	array.push("#{size}:#{sha1}")
	#grab sha1 and size of artifact, push to array
	$i +=1
end
array = array.uniq
#remove duplicates from array
array.each {|i| 
	re = /(.*):(.*)/
	m = re.match("#{i}")
	totalbytes += m[1].to_i
	#add up the total byte usage
 }  
puts "Total storage usage of repository " + repo + ": " + Filesize.from("#{totalbytes}" + "B").pretty