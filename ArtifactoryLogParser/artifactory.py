#!/usr/bin/python
import re
import sys
import colorama
from colorama import Fore, Back, Style
import operator

if len(sys.argv) !=2:
    print('Usage: python artifactory.py artifactory.log')
    sys.exit(0)

errors = []
warnings = []
debug = []
readfile = sys.argv[1]

def readlogs():
    with open(readfile) as f:
        for line in f:
            try:
               if "WARN" in line:
                    regex = '^([-0-9]+ [:0-9]+,[0-9]+) \[([-a-zA-Z0-9]+)\] \[([A-Z]+) *\] \(([.a-zA-Z0-9]+):([0-9]+)\) - (.*)$'
                    match = re.search(regex,line.encode('ascii'),flags = 0)
                    print Fore.RED  + (match.group(6))
                    warnings.append(match.group(6)[:40])

               elif "ERROR" in line:
                    regex = '^([-0-9]+ [:0-9]+,[0-9]+) \[([-a-zA-Z0-9]+)\] \[([A-Z]+) *\] \(([.a-zA-Z0-9]+):([0-9]+)\) - (.*)$'
                    match = re.search(regex,line.encode('ascii'),flags = 0)
                    print Fore.YELLOW  + (match.group(6))
                    errors.append(match.group(6)[:40])
               elif "INFO" in line:
                    regex = '^([-0-9]+ [:0-9]+,[0-9]+) \[([-a-zA-Z0-9]+)\] \[([A-Z]+) *\] \(([.a-zA-Z0-9]+):([0-9]+)\) - (.*)$'
                    match = re.search(regex,line.encode('ascii'),flags = 0)
                    print Fore.GREEN + (match.group(6))
               elif "DEBUG" in line:
                    regex = '^([-0-9]+ [:0-9]+,[0-9]+) \[([-a-zA-Z0-9]+)\] \[([A-Z]+) *\] \(([.a-zA-Z0-9]+):([0-9]+)\) - (.*)$'
                    match = re.search(regex,line.encode('ascii'),flags = 0)
                    print Fore.MAGENTA + line
                    debug.append(match.group(6)[:40])               
            except Exception:
                pass
    warningdic = dict((x,warnings.count(x)) for x in set(warnings))
    for key, value in sorted(warningdic.iteritems(), key=lambda (k,v): (v,k)):
        print Fore.RED + "%s : times --- %s" % (key, value)

    errorsdic = dict((x,errors.count(x)) for x in set(errors))
    for key, value in sorted(errorsdic.iteritems(), key=lambda (k,v): (v,k)):
        print Fore.YELLOW + "%s : times --- %s" % (key, value)

    debugdic = dict((x,debug.count(x)) for x in set(debug))
    for key,value in sorted(debugdic.iteritems(),key=lambda (k,v):(v,k)):
        print Fore.MAGENTA + "%s : times --- %s" % (key,value)


    print (Style.RESET_ALL)

readlogs()
exit()

