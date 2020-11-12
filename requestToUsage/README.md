#requestToUsage.sh

To quickly grab these scripts without cloning or downloading and unpacking a zip:

```
curl -L -O https://raw.githubusercontent.com/jfrog/artifactory-scripts/master/requestToUsage/requestToUsage.sh && chmod +x requestToUsage.sh
# multiLog script requires requestToUsage, but multiLog is only needed if you want to parse all `request.*` logs in a folder in one run
curl -L -O https://raw.githubusercontent.com/jfrog/artifactory-scripts/master/requestToUsage/multiLogParse.sh && chmod +x multiLogParse.sh
```

These scripts are used with the syntax:
`./requestToUsage.sh request.log [optional-output-prefix]` or
(replace request.log with the name of your request log file)
`./multiLogParse.sh ./logs [optional-output-prefix]`
(the `multiLogParse.sh` script currently has `request.*` hardcoded for the file glob to match in the folder path given)

The script has been updated to provide you a day by day summary of data transferred as well as a summary of the data transferred during the entire period of the log(s). It doesn't currently calculate averages, but that could be considered in the future, the challenge is that currently it only analyzes one log file at a time which only encompasses a few days and doesn't track state across multiple files, that would probably be broken out into a separate script.

It outputs one or more files of the pattern `[optional-output-prefix-]FIRSTDATEINLOG.csv` which you can open in Excel/OpenOffice Calc.
The furthest bottom right field is your overall usage in gigabytes over the period of the request log.  You need to figure out the difference in the dates and turn it into a 30-day figure to get a monthly usage figure if the summaries in the script run output mentioned above aren't sufficient.
