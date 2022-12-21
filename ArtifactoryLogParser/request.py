import sys
import re
#match.group(1) = time(example: 20160621065454)
#match.group(4) = IP Address
#match.group(6) = HTTP Method(GET,POST,PUT)
#match.group(7) = URL
#match.group(9) = HTTP Response Code

if len(sys.argv) !=2:
    print('Usage: python request.py request.log')
    sys.exit(0)
readfile = sys.argv[1]
with open(readfile) as f:
    for line in f:
        try:
            p = re.compile(r'(\d*)\|(\d*)\|(.*)\|(.*)\|(.*)\|(.*)\|(.*)\|(.*)\|(.*)\|(.*)')
            match = re.match(p,line)
            print(match.group(4) + " - " + match.group(6) + " - " + match.group(9))
        except Exception:
            pass
exit()
