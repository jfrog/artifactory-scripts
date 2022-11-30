#!/usr/bin/python3

#
# Requires no external Python libraries
#

import sys, re, os , glob , gzip

#
# Log RegEx patterns - Used to recognize request log files
#
# Pattern names: "year","month","day","hour","minute","second","requesttime","ip","user","type","path","proto","rcode","filesize"
# Patterns used: year, month, day, hour, minute, second, requesttime, path, rcode

### 6.X request log line pattern ###
#Ref: https://regex101.com/r/In1kBZ/2
#EX. 20190422084730|8|REQUEST|0:0:0:0:0:0:0:1|non_authenticated_user|GET|/|HTTP/1.1|302|0
sixXPattern = re.compile(r'(?P<year>.{4})(?P<month>.{2})(?P<day>.{2})(?P<hour>.{2})(?P<minute>.{2})(?P<second>.{2})\|(?P<requesttime>\d*)\|REQUEST\|(?P<ip>.*)\|(?P<user>.*)\|(?P<type>.*)\|(?P<path>.*)\|(?P<proto>.*)\|(?P<rcode>.*)\|(?P<reqsize>.*)')

### 7.X req. log line pattern ###
#Ref: https://regex101.com/r/bHfX6g/4
#EX. 2020-04-14T23:11:27.277Z|31627ed4a292c0e6|0:0:0:0:0:0:0:1|anonymous|GET|/api/system/ping|200|-1|0|4|JFrog-Router/1.2.1
#sevenXPattern = re.compile(r'(?P<year>\d*)-(?P<month>\d*)-(?P<day>\d*)T(?P<hour>\d\d)\:(?P<minute>\d\d)\:(?P<second>\d\d.\d\d\d)Z\|(?P<traceid>.*)\|(?P<ip>.*)\|(?P<user>.*)\|(?P<type>.*)\|(?P<path>.*)\|(?P<rcode>.*)\|(?P<filesize>.*)\|(?P<reqsize>.*)\|(?P<requesttime>.*)\|(?P<agent>.*)') 
sevenXPattern = re.compile(r'(?P<year>\d*)-(?P<month>\d*)-(?P<day>\d*)T(?P<hour>\d\d)\:(?P<minute>\d\d)\:(?P<second>\d|.*)Z\|(?P<traceid>.*)\|(?P<ip>.*)\|(?P<user>.*)\|(?P<type>.*)\|(?P<path>.*)\|(?P<rcode>.*)\|(?P<filesize>.*)\|(?P<reqsize>.*)\|(?P<requesttime>.*)\|(?P<agent>.*)')

#           #
# Variables #
#           #

#Files to parse
log_filenames=[]


# API Paths to ignore
# Warning: Not an exhaustive list, may need refinement!
system_APIs=[
   "api/system",
   "api/v1",
   "api/auth",
   "api/events",
   "api/retention",
   "api/storagesummary", 
   "api/saml", 
   "api/jobs", 
   "api/artifactsearch", 
   "api/onboarding",
   "api/search",
   "/webapp",
   "api/docker/v2/",
   "api/docker/null/"
]


cutoffThreshold = 10
default_filename = "artifactory-statistics"

#Loading indicator
loadingCount=0
loadingPrint=5000

#
# Main read function
#

def readlogs(filenames, countData):
     topRepos = {}
     topUsers = {}
     topIPs   = {}

     # totalfiles = len(filenames)
     # for test_case in filenames:
     #      print(test_case)

     #Before beginning, determine what type of request log this is (6.X or 7.X)
     for gzfile  in filenames: 
          print(gzfile) 
          # https://stackoverflow.com/questions/16813267/python-gzip-refuses-to-read-uncompressed-file
          if gzfile.endswith('.gz'):
               opener = gzip.open
          else:
               opener = open
          with opener( gzfile, 'r') as f:
               try:
                    if opener == gzip.open :
                         pattern = checkPattern_in_gz_file(f)
                    else:
                         pattern = checkPattern(f)
               except Exception:
                    raise Exception ("Error!")
               p = re.compile(pattern) #Compile the "pattern" created by checkFormat

               loadingCount=0

               #Read each line of the request log file, extract the API path and usernames
               for line in f:
                    if opener == gzip.open :
                         match = re.match(p,line.decode('utf-8')) #Match the line to the pattern
                    else:
                         match = re.match(p,line) 
                    
                    #                    
                    # Find the repository name, add +1 to the dictionary count
                    #
                    
                    # First, filter out the system ping checks using a reference dictionary
                    reqPath = match.group("path").split("/")
                    shouldSkip = False 
                    for api in system_APIs: 
                         if api in match.group("path"): shouldSkip = True; break
                    if shouldSkip: continue
                    # Second, split up the path into an array for parsing
                    
                    # Count the size of the request using the request size parameter, or just set to 1 if you want to count requests instead
                    if countData: 
                         requestSize = int(match.group("reqsize"))
                         if requestSize == -1: requestSize = 0 #Fix the "empty request" -1 marker to avoid accidental subtractions
                    else: requestSize = 1
                    
                    
                    # If the format is something like /api/nuget/nuget-local, 
                    # the repository name is nuget-local
                    if reqPath[1] == "api" and len(reqPath) > 3 and reqPath[3] is not None:
                         if reqPath[3] not in topRepos:
                              topRepos.update({reqPath[3]:requestSize})
                         else:
                              requests = topRepos[reqPath[3]] + requestSize
                              topRepos.update({reqPath[3]: requests})
                    # If the format is something like /libs-snapshot-local/file/path/something.pom, 
                    # the repo name is libs-snapshot-local
                    elif reqPath[1] != "api" and reqPath[1] != "ui" and reqPath[1] is not None:
                         if reqPath[1] not in topRepos:
                              topRepos.update({reqPath[1]:requestSize})
                         else:
                              requests = topRepos[reqPath[1]] + requestSize
                              topRepos.update({reqPath[1]: requests})
                                                  
                    #
                    # Find the user name, add +1 to the username dictionary
                    # 
                    
                    if match.group("user") in topUsers:
                         userRequests = topUsers[match.group("user")] + requestSize
                         topUsers.update({match.group("user"): userRequests})
                         #print("DEBUG:\tUpdating request for: " + match.group("user") + " They now have: " + str(userRequests) + " Requests")
                    else:
                         topUsers.update({match.group("user"): requestSize})
                         #print("DEBUG:\tAdding new user: " + match.group("user"))
                    
                    
                    #
                    # Find the IP, add +1 to the IP dictionary, if the -ip param is passed
                    #
                    if printIPs:
                         if match.group("ip") in topIPs:
                              ipCount = topIPs[match.group("ip")] + requestSize
                              topIPs.update({match.group("ip"): ipCount})
                         else:
                              topIPs.update({match.group("ip"): requestSize})
                    
                    #
                    # Print a loading indicator every X lines
                    #
                    loadingCount = loadingCount + 1
                    
                    if loadingCount >= loadingPrint:
                         loadingCount = 0
                         print(".", end='', flush=True)
          
     #All done, return the dictionaries for printing
     return [topRepos, topUsers, topIPs]

# 
# Generic print statement for statistics
# Expects: 
# topThing = Dictionary
# header = header for top row (2 element array), also used for the filename
# printToCSV = boolean on whether to make files or not
#

def printThing(topThing, header):
     print("-----\n")
     for line in header: 
          print(line, end='', flush=True)
          print("\t", end='', flush=True)
     print("")
     for thing in sorted(topThing, key=topThing.get, reverse=True):
          if not printFull and topThing[thing] > cutoffThreshold:
               print(thing + "\t" + str(topThing[thing]))
          elif printFull:
               print(thing + "\t" + str(topThing[thing]))

def printToCSV(topThing, header):
     print("Scan complete!\nWriting to "+ default_filename + "-" + header[0] + ".csv...")
     with open(default_filename+"-"+header[0]+".csv", "w") as exportFile:
          exportFile.write(header[0] + ',' + header[1] + "\n")
          for thing in sorted(topThing, key=topThing.get, reverse=True):
               if not printFull and topThing[thing] > cutoffThreshold: #When the printFull param isn't there
                    exportFile.write(thing + "," + str(topThing[thing]) + "\n")
               elif printFull:
                    exportFile.write(thing + "," + str(topThing[thing]) + "\n")

#
# Function to determine which log RegEx to use
# Takes in a filename, reads the first line, tries to match the pattern
#
def checkPattern(f):
     firstLine = f.readline()

     if sixXPattern.match(firstLine):
         #It's a 6.X request.log, as the timestamp should only have numerals
         return sixXPattern
     elif sevenXPattern.match(firstLine):
         #It's a 7.X artifactory-request.log file, there's a full timestamp
         return sevenXPattern
     elif len(firstLine.strip()) == 0:
         raise Exception("Emptyfile")
     else:
         print("ERROR:\tThis is not a request log format I recognize!")
         print(("ERROR:\tFailed to recognize:\n\n"+firstLine))
         raise Exception("Not a request log file")

def checkPattern_in_gz_file(f):
     
     for firstLine in f:
          #print(firstLine)

          if sixXPattern.match(firstLine.decode('utf-8')):
          #It's a 6.X request.log, as the timestamp should only have numerals
               return sixXPattern
          elif sevenXPattern.match(firstLine.decode('utf-8')):
          #It's a 7.X artifactory-request.log file, there's a full timestamp
               return sevenXPattern
          elif len(firstLine.decode('utf-8').strip()) == 0:
               raise Exception("Emptyfile")
          else:
               print("ERROR:\tThis is not a request log format I recognize!")
               print(("ERROR:\tFailed to recognize:\n\n"+firstLine.decode('utf-8')))
               raise Exception("Not a request log file")


#
# Script Input Handler
# Reads commandline arguments passed when the script is called
#

#
# Variables to skip printing things
#
printFull = False
printIPs  = False
printCSV  = False
countData = False

if len(sys.argv) >= 2:
     for arg in sys.argv:
          if "-full" == arg:
               print("\n-----\nDisplaying tiny request counts!\n-----\n")
               printFull = True
          elif "-ip" == arg:
               print("\n-----\nDisplaying IP usage!\n-----\n")
               printIPs = True
          elif "-csv" == arg:
               print("\n-----\nCSV-write mode activated!\nWriting to: " + default_filename + "-*.csv\n-----\n")
               printCSV = True
          elif "-data" == arg:
               print("\n-----\nCounting Data instead of requests...\n-----\n")
               countData = True
          elif "topRepos" not in arg and "request_trace" not in arg:
               # log_filenames.append(arg)
               print("\nScanning: \t" + arg + "\n")
               #print(arg)
               log_filenames.extend(sorted(glob.glob(arg), key=os.path.getmtime))


else:
     print("Usage:\n\t./topRepos.py artifactory-request.log [-ip] [-full] [-csv]")


# for gzfile in log_filenames:
#      print(gzfile)

results = readlogs(log_filenames, countData)

#After reading the input arguments, begin analyzing the logs one by one
if not printCSV:
     headerType = "Request Count"
     printThing(results[0],["Repository",headerType])
     printThing(results[1],["Username",headerType])
     if printIPs and results[2] is not None: printThing(results[2],["IP address",headerType])
else:
     headerType = "Data Transfer (Bytes)"
     printToCSV(results[0],["Repository",headerType])
     printToCSV(results[1],["Username",headerType])
     if printIPs and results[2] is not None: printToCSV(results[2],["IP address",headerType])
""" for f in log_filenames:
     results = readlogs(f, countData)
     if not printCSV:
          headerType = "Request Count"
          printThing(results[0],["Repository",headerType])
          printThing(results[1],["Username",headerType])
          if printIPs and results[2] is not None: printThing(results[2],["IP address",headerType])
     else:
          headerType = "Data Transfer (Bytes)"
          printToCSV(results[0],["Repository",headerType])
          printToCSV(results[1],["Username",headerType])
          if printIPs and results[2] is not None: printToCSV(results[2],["IP address",headerType])
 """
