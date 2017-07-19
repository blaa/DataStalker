# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

"""
OUI decoder and decorator
"""

import re
from time import time
from pprint import pprint
import logging

from datastalker.pipeline import Stage, Pipeline

@Pipeline.register_stage('oui')
class OuiStage(Stage):
    """Decode number of MAC fields"""

    def __init__(self, db_path, fields, suffix, stats):
        self.suffix = suffix

        self.stats = stats

        # [field -> new-field, field2 -> new-field2]
        self.fields = [(field, field + suffix) for field in fields]

        self.db_path = db_path
        self.db = self._parse_config(db_path)

    def _parse_config(self, path):
        "Load entries from OUI database"
        regexp = r'(?P<mac>[A-Z0-9]+)[\t ]+\(base 16\)[\t ]+(?P<producer>.*)'
        match = re.compile(regexp)
        db = {}
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                result = re.match(match, line)
                if not result:
                    continue

                mac_6, organization = result.groups()
                mac = ":".join([mac_6[0:2], mac_6[2:4], mac_6[4:6]])
                mac = mac.lower()
                if mac in db:
                    self.log.warning("Duplicate in OUI database (%s = %s)",
                                     mac, organization)
                    self.stats.incr('oui/entries/duplicated')

                db[mac] = organization
                self.stats.incr('oui/entries/loaded')
        return db

    def handle(self, entry):
        "Decorate based on config"
        for field_name, new_field_name in self.fields:
            if field_name in entry:
                mac = entry[field_name][:8]
                value = self.db.get(mac, 'unknown')
                entry[new_field_name] = value
                self.stats.incr('oui/entries/decoded')


    @classmethod
    def from_config(cls, config, stats):
        "Build oui stage"
        db_path = config.get('db_path', None)
        fields = config.get('fields', None)
        suffix = config.get('suffix', '_oui')

        if db_path is None or fields is None:
            raise Exception("OUI stage requires an db_path and fields options")
        if not isinstance(fields, list):
            raise Exception("OUI stage fields option must be a list")

        stage = OuiStage(db_path, fields, suffix, stats)

        return stage
