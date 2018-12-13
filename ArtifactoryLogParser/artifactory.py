#!/usr/bin/python
import re
import sys

try:
    import colorama
    from colorama import Fore, Back, Style
    ce = True  # Color Enabled

except ModuleNotFoundError:
    print("Colorama is not installed. Coloring functions will be disabled.")
    print("To enable coloring run 'pip install colorama'.")
    print()
    ce = False  # Color Enabled

except Exception as e:
    print("Unexpected exception during import of Colorama")
    print(e)

if len(sys.argv) !=2:
    print('Usage: python artifactory.py /path/to/artifactory.log')
    sys.exit(0)


# Gather input values
readfile = sys.argv[1]

with open(readfile) as f:
    for line in f.readlines():
        if "WARN" in line:
            try:
                regex = '^([-0-9]+ [:0-9]+,[0-9]+) \[([-a-zA-Z0-9]+)\] \[([A-Z]+) *\] \(([.a-zA-Z0-9]+):([0-9]+)\) - (.*)$'
                match = re.search(regex, line, flags=0)
                if ce:
                    print(Fore.RED, "WARNING:", (match.group(6)))
                else:
                    print("--")
            except Exception as e:
                print("[artifactory.py] Unexpected exception when parsing for warnings")
                print(e)

        if "ERROR" in line:
            try:
                match = re.search(regex, line, flags=0)
                print(Fore.YELLOW + "ERROR:" + (match.group(6)))

            except Exception as e:
                print("[artifactory.py] Unexpected exception when parsing for warnings")
                print(e)

        if "INFO" in line:
            try:
                regex = '^([-0-9]+ [:0-9]+,[0-9]+) \[([-a-zA-Z0-9]+)\] \[([A-Z]+) *\] \(([.a-zA-Z0-9]+):([0-9]+)\) - (.*)$'
                match = re.search(regex, line, flags=0)
                print(Fore.GREEN + "INFO:" + (match.group(6)))
            
            except Exception as e:
                print("[artifactory.py] Unexpected exception when parsing for warnings")
                print(e)
    
print (Style.RESET_ALL)
exit()

