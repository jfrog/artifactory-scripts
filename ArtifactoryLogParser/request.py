import sys
import re
import colorama
from colorama import Fore, Back, Style
#match.group(1) = time(example: 20160621065454)
#match.group(4) = IP Address
#match.group(6) = HTTP Method(GET,POST,PUT)
#match.group(7) = URL
#match.group(9) = HTTP Response Code

responsecodes = []


if len(sys.argv) !=2:
    print('Usage: python request.py request.log')
    sys.exit(0)

readfile = sys.argv[1]

def readlogs():
    with open(readfile) as f:
        for line in f:
            try:
                p = re.compile(ur'(\d*)\|(\d*)\|(.*)\|(.*)\|(.*)\|(.*)\|(.*)\|(.*)\|(.*)\|(.*)')
                match = re.match(p,line)
                response = match.group(4) + " - " + match.group(6) + " - " + match.group(9)
                if match.group(9)[:1] == "2":
                    print Fore.GREEN + response
                    responsecodes.append(match.group(9))
                elif match.group(9)[:1] == "4" or "5":
                    print Fore.RED + response
                    responsecodes.append(match.group(9))
                else:
                    print response
                    responsecodes.append(match.group(9))
            except Exception:
                pass
    print (Style.RESET_ALL)
    responsedic = dict((x,responsecodes.count(x)) for x in set(responsecodes))
    for key, value in sorted(responsedic.iteritems(), key=lambda (k,v): (v,k)):
        print "%s: %s" % (key, value)


readlogs()
exit()