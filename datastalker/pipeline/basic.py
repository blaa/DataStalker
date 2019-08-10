# (C) 2015 - 2019 by Tomasz bla Fortuna
# License: MIT

"""
Basic stages which might be used in pipelines.
"""

import sys
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
    def __init__(self, prefix):
        self.prefix = prefix

    def handle(self, message):
        sys.stdout.write(self.prefix + str(message) + "\n")
        sys.stdout.flush()
        return message

    @classmethod
    def from_config(cls, config, stats):
        stage = PrintStage(config.get('prefix', ''))
        return stage


@Pipeline.register_stage('strip')
class StripStage(Stage):
    """Remove keys matching configured scheme"""
    def __init__(self, keys_startswith, keys, stats):
        self.keys_startswith = keys_startswith
        self.keys = keys
        self.stats = stats

    def handle(self, message):
        ks = self.keys_startswith
        for k in list(message.keys()):
            if ks is not None and k.startswith(ks):
                del message[k]
                self.stats.incr('stripstage/stripped_by_prefix')

        for key in self.keys:
            if key in message:
                del message[key]
                self.stats.incr('stripstage/stripped_by_name')
        return message

    @classmethod
    def from_config(cls, config, stats):
        keys_startswith = config.get('keys_startswith', None)
        keys = config.get('keys', [])

        stage = StripStage(keys_startswith, keys, stats)
        return stage


@Pipeline.register_stage('limit')
class LimitStage(Stage):
    """Stop pipeline when the limit is reached"""
    def __init__(self, time_limit=None, message_limit=None):
        self.time_limit = time_limit
        self.message_limit = message_limit

        self.start_time = time()
        self.message_cnt = 0

    def handle(self, message):
        "Raise StopPipeline when 1 of 2 possible events are triggered"
        if self.time_limit is not None:
            took = time() - self.start_time
            if took > self.time_limit:
                raise Pipeline.StopPipeline("Time limit reached")
        if self.message_limit is not None and self.message_cnt > self.message_limit:
            raise StopPipeline("Message limit reached")

        self.message_cnt += 1
        return message

    @classmethod
    def from_config(cls, config, stats):
        "Build limitstage"
        seconds = config.get('seconds', None)
        entries = config.get('messages', None)
        if seconds is None and entries is None:
            raise Exception("Limit stage requires seconds or entries config")

        stage = LimitStage(time_limit=seconds,
                           message_limit=entries)
        return stage
