import re
import sys

print(re.sub("[^0-9a-z]+", "-", sys.argv[1].lower()))
