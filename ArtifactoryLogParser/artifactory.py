#!/usr/bin/python
import re
import sys


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

    def clear(self):
        print(self.ENDC)


if len(sys.argv) !=2:
    print('Usage: python artifactory.py /path/to/artifactory.log')
    sys.exit(0)


# Gather input values
readfile = sys.argv[1]

data = {'WARN':
            {'results': [],
             'color': Colors.WARNING,
             'message': 'WARNING:'},
        'ERROR':
            {'results': [],
             'color': Colors.FAIL,
             'message': 'ERROR:'},
        'INFO':
            {'results': [],
             'color': Colors.OKBLUE,
             'message': 'INFO:'
             }
        }


regex = '^([-0-9]+ [:0-9]+,[0-9]+) \[([-a-zA-Z0-9]+)\] \[([A-Z]+) *\] \(([.a-zA-Z0-9]+):([0-9]+)\) - (.*)$'

unexpected_error_log = "[artifactory.py] Unexpected exception when parsing for {}"

with open(readfile) as f:
    for line in f.readlines():
        message = ""
        match = re.search(regex, line, flags=0)

        if match:
            e_type = [x for x in ["ERROR", "WARN", "INFO"] if x in line][0]
            entry = ' '.join([data[e_type]['color'], data[e_type]['message'], (match.group(6))])
            data[e_type]['results'].append(entry)

for entry_type in data:
    for result in data[entry_type]["results"]:
        print(result)

Colors().clear()

exit()

