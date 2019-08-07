# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

"""
Basic stages which might be used in pipelines.
"""

from time import time
from pprint import pprint

from datastalker.pipeline import (
    Stage,
    Pipeline,
    StopPipeline
)

from . import log

@Pipeline.register_stage('print')
class PrintStage(Stage):
    """Print all data passing this stage"""
    def handle(self, entry):
        pprint(entry)
        return entry

    @classmethod
    def from_config(cls, config, stats):
        stage = PrintStage()
        return stage


@Pipeline.register_stage('strip')
class StripStage(Stage):
    """Remove keys matching configured scheme"""
    def __init__(self, keys_startswith, keys, stats):
        self.keys_startswith = keys_startswith
        self.keys = keys
        self.stats = stats

    def handle(self, entry):
        ks = self.keys_startswith
        for k in list(entry.keys()):
            if ks is not None and k.startswith(ks):
                del entry[k]
                self.stats.incr('stripstage/stripped_by_prefix')

        for key in self.keys:
            if key in entry:
                del entry[key]
                self.stats.incr('stripstage/stripped_by_name')
        return entry

    @classmethod
    def from_config(cls, config, stats):
        keys_startswith = config.get('keys_startswith', None)
        keys = config.get('keys', [])

        stage = StripStage(keys_startswith, keys, stats)
        return stage


@Pipeline.register_stage('limit')
class LimitStage(Stage):
    """Stop pipeline when the limit is reached"""
    def __init__(self, time_limit=None, entry_limit=None):
        self.time_limit = time_limit
        self.entry_limit = entry_limit

        self.start_time = time()
        self.entry_cnt = 0

    def handle(self, entry):
        "Raise StopPipeline when 1 of 2 possible events are triggered"
        if self.time_limit is not None:
            took = time() - self.start_time
            if took > self.time_limit:
                raise Pipeline.StopPipeline("Time limit reached")
        if self.entry_limit is not None and self.entry_cnt > self.entry_limit:
            raise StopPipeline("Entry limit reached")

        self.entry_cnt += 1
        return entry

    @classmethod
    def from_config(cls, config, stats):
        "Build limitstage"
        seconds = config.get('seconds', None)
        entries = config.get('entries', None)
        if seconds is None and entries is None:
            raise Exception("Limit stage requires seconds or entries config")

        stage = LimitStage(time_limit=seconds,
                           entry_limit=entries)
        return stage
