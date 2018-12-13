#!/usr/bin/python
import re
import sys


class Colors:

    def __init__(self):
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''

    def clear(self):
        print(self.ENDC)


class Logger:

    default_sf = ["WARN", "ERROR", "INFO"]

    def __init__(self, readfile, regex):
        self.colors = Colors()
        self.data = {
            'WARN':
                {'results': [],
                 'color': self.colors.WARNING,
                 'message': 'WARNING:'},
            'ERROR':
                {'results': [],
                 'color': self.colors.FAIL,
                 'message': 'ERROR:'},
            'INFO':
                {'results': [],
                 'color': self.colors.OKBLUE,
                 'message': 'INFO:'
                 }
            }
        self.readfile = readfile
        self.regex = regex

    def parse(self):
        with open(self.readfile) as f:
            for line in f.readlines():
                match = re.search(self.regex, line, flags=0)
                if match:
                    e_type = [x for x in self.default_sf if x in line][0]
                    entry = ' '.join([self.data[e_type]['color'], self.data[e_type]['message'], (match.group(6))])
                    self.data[e_type]['results'].append(entry)

    def output(self, sf):
        for entry_type in self.data:
            if entry_type in sf:
                for result in self.data[entry_type]["results"]:
                    print(result)

    def disable_color(self):
        for entry_type in self.data:
            self.data[entry_type]["color"] = ''


def main():

    # Gather input values
    readfile = sys.argv[1]
    regex = '^([-0-9]+ [:0-9]+,[0-9]+) \[([-a-zA-Z0-9]+)\] \[([A-Z]+) *\] \(([.a-zA-Z0-9]+):([0-9]+)\) - (.*)$'
    logger = Logger(readfile, regex)
    n_args = len(sys.argv)

    if n_args < 2:
        print('Usage: python artifactory.py /path/to/artifactory.log [filters]')
        sys.exit(0)

    elif n_args == 2:
        search_filter = logger.default_sf
    else:
        search_filter = sys.argv[2:]

    if "nocolor" in search_filter:
        logger.disable_color()

    logger.parse()
    logger.output(sf=search_filter)
    logger.colors.clear()
    exit()


if __name__ == '__main__':
    main()





