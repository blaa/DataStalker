
from pprint import pprint
from collections import defaultdict


class Stats:
    """
    Statistics aggregated during pipeline run.

    API mostly shamelessly "stolen" from scrapy.
    """

    def __init__(self):
        self.stats = defaultdict(lambda: 0)

    def incr(self, field, value=1):
        "Increment statistic by a given value"
        self.stats[field] += value

    def decr(self, field, value=1):
        "Decrement statistic by a given value"
        self.stats[field] -= value

    def set(self, field, value):
        "Increment statistic by one"
        self.stats[field] = value

    def get_stats(self):
        "Return dictionary with stats"
        return self.stats.copy()

    def dump(self):
        print()
        print("Pipeline statistics:")
        pprint(dict(self.stats))
