#!/usr/bin/python
import re
import sys
import colorama
from colorama import Fore, Back, Style

if len(sys.argv) !=2:
    print('Usage: python artifactory.py artifactory.log')
    sys.exit(0)


readfile = sys.argv[1]
i = 0
with open(readfile) as f:
    for line in f:
        if "WARN" in line:
            try:
                regex = '^([-0-9]+ [:0-9]+,[0-9]+) \[([-a-zA-Z0-9]+)\] \[([A-Z]+) *\] \(([.a-zA-Z0-9]+):([0-9]+)\) - (.*)$'
                match = re.search(regex,line.encode('ascii'),flags = 0)
                print Fore.RED + "WARNING:" + (match.group(6))
           
            except Exception:
                pass

with open(readfile) as f:
    for line in f:
        if "ERROR" in line:
            try:
                regex = '^([-0-9]+ [:0-9]+,[0-9]+) \[([-a-zA-Z0-9]+)\] \[([A-Z]+) *\] \(([.a-zA-Z0-9]+):([0-9]+)\) - (.*)$'
                match = re.search(regex,line.encode('ascii'),flags = 0)
                print Fore.YELLOW + "ERROR:" + (match.group(6))
            
            except Exception:
                pass

with open(readfile) as f:
    for line in f:
        if "INFO" in line:
            try:
                regex = '^([-0-9]+ [:0-9]+,[0-9]+) \[([-a-zA-Z0-9]+)\] \[([A-Z]+) *\] \(([.a-zA-Z0-9]+):([0-9]+)\) - (.*)$'
                match = re.search(regex,line.encode('ascii'),flags = 0)
                print Fore.GREEN + "INFO:" + (match.group(6))
            
            except Exception:
                pass
    
print (Style.RESET_ALL)
exit()

