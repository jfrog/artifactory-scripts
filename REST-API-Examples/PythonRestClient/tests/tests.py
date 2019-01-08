# Add the b directory to your sys.path

import sys, os
parent_dir = os.getcwd() # find the path to module a
# Then go up one level to the common parent directory
path = os.path.dirname(parent_dir)
# Add the parent to sys.pah
sys.path.append(path)

# Now you can import anything from b.s
import artifactopy

artifactopy.api
