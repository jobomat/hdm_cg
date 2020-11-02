# In this file just add the folders where your application setup scripts reside
# and call the initialization function.
# Take care of unique naming e.g. by prefixing your scripts with the app-name.
import os
import sys

base = os.path.dirname(os.path.dirname(__file__))

# Maya
sys.path.append(os.path.join(base, "maya/setup"))
from maya_setup import *