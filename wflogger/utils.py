# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

"""
Utility functions for handling time
"""
import pytz
import tzlocal

LOCAL_TIMEZONE = tzlocal.get_localzone()
UTC = pytz.utc

def normalize(timestamp):
    "Convert UTC To local timestamp"
    return LOCAL_TIMEZONE.normalize(timestamp)

def localize(timestamp):
    "Add local timezone info to datetime without tzinfo"
    return LOCAL_TIMEZONE.localize(timestamp, is_dst=None)
