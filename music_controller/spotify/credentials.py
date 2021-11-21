"""
Holds variables for the different spotify credentials to connect to the spotify api. These are actually kept in environment variables, but are imported here so I can more easily continue to follow the tutorial.
"""

from decouple import config

CLIENT_ID = config("CLIENT_ID")
CLIENT_SECRET = config("CLIENT_SECRET")
REDIRECT_URI = config("REDIRECT_URI")
