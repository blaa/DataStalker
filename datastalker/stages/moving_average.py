from collections import namedtuple
from datastalker.pipeline import Stage, Pipeline

from time import time

@Pipeline.register_stage('moving_average')
class MovingAverageStage(Stage):
    """
    """
    def __init__(self, stats)
        self.stats = stats

    def clear_cache(self):
        "Periodical cache cleanup"
        self.stats.incr('beaconfilter/cleanups')
        now = time()
        self.last_cleanup = now
        drop_at = now - self.max_time_between
        for key, cache_entry in self.beacon_cache.items():
            if cache_entry.timestamp < drop_at:
                del self.beacon_cache[key]

    def handle(self, entry):
        self.stats.incr('beaconfilter/checked')

        if self.filter_beacon(entry):
            self.stats.incr('beaconfilter/dropped')
            return None
        else:
            self.stats.incr('beaconfilter/accepted')
            return entry

    @classmethod
    def from_config(cls, config, stats):
        "Build beaconfilter stage"
        cfg = {
            'cleanup_interval': config.get('cleanup_interval', 600),
            'max_strength_deviation': config.get('max_strength_deviation', 15),
            'max_time_between': config.get('max_time_between', 120),
            'timestamp_field': config.get('timestamp_field', 'timestamp'),
            'strength_field': config.get('strength_field', 'strength'),
        }
        stage = BeaconFilterStage(stats, **cfg)
        return stage
