# topRepo - A Python Request Log Script

topRepo.py is a Python 3 script designed to compile and print statistics using a request.log file's data. This script is helpful for finding the most heavily used repositories, 
and the most active user accounts. Using this information, you can determine who to contact to test a new Artifactory system or process. It provides insight into who's using 
the system the most, either by request volume or data volume.

The Python script should require no external dependencies, you may need to install "python-datetime":

```
pip3 install python-datetime
```

The script counts requests done to both *repositories* and *usernames,* using a Dictionary for each. After reviewing the log, it produces tab-separated output that can be copy/pasted
into a spreadsheet program. *IP addresses* can also optionally be counted. The script then prints a sorted list of these Dictionaries with the request count, for example it prints
*usernames* sorted by how many requests each user does.

Optionally, pass the "-csv" parameter to create CSV files that you can open in Excel or a spreadsheet program. It creates one file per element (Users, Repositories, IPs).

If you want to see data transfer statistics (Upload and downloads), pass "-data" and the size in bytes is counted instead. Otherwise by default the script counts requests made.

By default the script will not show usernames who have made less than *ten requests*.

## How it works

Determining what repository was in use is more complicated than it first appears. The artifactory-request.log has two kinds of patterns for upload and download APIs. 
The script filters out other kinds of requests and will only count these upload and download events.

First, there is the /api/something/repo-name pattern:

```
GET /api/<package-manager>/<repo-name>/<path-to-file.ext>
    Ex: GET /api/nuget/nuget-local/package.nupkg
```

Second, there's the /repo-name pattern:

```
GET /<repo-name>/<path-to-file.ext>
    Ex: GET /libs-snapshot-local/org/hello/hello.pom
```

The script will count requests which match these two kinds of path patterns. You may see some odd results, especially if a user gets an API path wrong.

Counting usernames and IPs is less complicated and doesn't have any nuance.

## Usage:

```
./topRepo.py ./artifactory-request.log [-ip] [-full] [-csv] [-data]
```

-ip: Count and print the IP addresses as a separate table
     Useful if usernames aren't unique and the host IP matters

-full: Print even minor request counts below 10 requests

-csv: Write to CSV files and use comma separators

-data: Count and display the request's file size when sorting usage

## Expected Output

```
Repository Statistics:
-----------------------
Repository	request count
jfrog-dev	16251
frog-central-remote	12267
froggy-dev	4592
swampland-prod	2892
[...]

-----

User Statistics:
-----------------
username	request count
anonymous	20671
sys-frog	4457
sys-froggie	4217
sys-jimmy	3942
sys-frank	3524
[...]

-----

IP Statistics:
-----------------
IP	request count
10.60.14.1	4608
10.60.15.2	3782
10.60.15.4	3210
10.60.15.3	3023
10.60.15.22	2859
10.60.14.25	2705
10.60.15.26	2276
[...]
```

