import os
import sys

# Ensure the API package path is on sys.path when pytest runs from other CWDs
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
