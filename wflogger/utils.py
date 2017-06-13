# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

"""
Utility functions for handling time
"""
import pytz
# import config

# TODO: Get from yaml file or from system.
LOCAL_TIMEZONE = pytz.timezone('Europe/Warsaw')

#LOCAL_TIMEZONE = pytz.timezone(config.local_timezone)
UTC = pytz.utc

def normalize(timestamp):
    "Convert UTC To local timestamp"
    return LOCAL_TIMEZONE.normalize(timestamp)

def localize(timestamp):
    "Add local timezone info to datetime without tzinfo"
    return LOCAL_TIMEZONE.localize(timestamp, is_dst=None)
