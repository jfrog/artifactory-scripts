#requestToUsage.sh
This script is used with the syntax:
```request.sh request.log```
(replace request.log with the name of your request log file)

It outputs a file request.csv which you can open in excel.
The furthest right field is your overall usage in gigabytes over the period of the request log.  You need to figure out the difference in the dates and turn it into a 30-day figure to get a monthly usage figure.

TODO: Automate date difference calculation to monthly statistic
