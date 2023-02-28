#requestToUsage.sh
This script is used with the syntax:
```requestToUsage.sh artifactory-request.log $Delimiter $Prefix```
(replace artifactory-request.log with the name of your request log file. $Delimiter could be pipe or comma. Default is comma.)

1.It consolodates the GET requests and generate a CSV file with the naming convention of 
{Date}_GET_Requests.CSV. 
2.It consolodates the POST requests and generate a CSV file with the naming convention of
{Date}_POST_Requests.CSV
3.It generates DataUsageSummary.txt which lists the individual files and their data 
usage size.

#multiLogParseWithCounter.sh
This script is used with the syntax:
```multiLogParseWithCounter.sh ../var/log/archived $Delimiter```
This will recursively go behind all the artifactory-requet-*.log from the archived folder and summarizes
the data usage in the DataUsageSummary.txt file. Every log file will be split with ONE CSV file with GET
requests and Second CSV file with POST requets. $Delimiter could be pipe or comma. Default is comma.

