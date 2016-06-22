import sys
import re

if len(sys.argv) !=2:
    print('Usage: python access.py access.log')
    sys.exit(0)
#match.group(1) = time
#match.group(2) = Response
#match.group(3) = File
#match.group(6) = user
#match.group(8) = IP Address

readfile = sys.argv[1]
with open(readfile) as f:
    for line in f:
        try:
            p = re.compile(ur'(\d*-\d*-\d*\d*.............)(.*])(.*)(for)(.)(.*)(\/)(.*)(\.)')
            match = re.match(p,line)
            print  match.group(1) + " - " + match.group(6) + " - " + match.group(8)
        except Exception:
            pass

exit()