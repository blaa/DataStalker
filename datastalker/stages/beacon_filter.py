from time import time
from collections import namedtuple

from datastalker.pipeline import Stage, Pipeline


CacheEntry = namedtuple('CacheEntry', 'timestamp, strength')


@Pipeline.register_stage('beacon_filter')
class BeaconFilterStage(Stage):
    """Remove redundant information about beacons from pipeline.

    Stationary located receiver will receive a lot of beacons from other
    stationary APs with similar strength.
    """
    def __init__(self, stats, cleanup_interval,
                 max_strength_deviation, min_time_between,
                 timestamp_field, strength_field):

        self.cleanup_interval = cleanup_interval
        self.max_strength_deviation = max_strength_deviation
        self.min_time_between = min_time_between
        self.timestamp_field = timestamp_field
        self.strength_field = strength_field

        # Data for beacon filter;
        # {(mac, ssid): CacheEntry, ...}
        self.beacon_cache = {}
        self.last_cleanup = time()

        self.stats = stats

    def clear_cache(self):
        "Periodical cache cleanup"
        self.stats.incr('beaconfilter/cleanups')
        drop_at = time() - self.min_time_between
        drop = [
            key
            for key, cache_entry in self.beacon_cache.items()
            if cache_entry.timestamp < drop_at
        ]
        self.log.info("Clearing beacon cache entries %d %r",
                      len(drop), drop)
        for key in drop:
            del self.beacon_cache[key]

    def filter_beacon(self, entry):
        "Returns True to filter out entry"
        now = time()
        if now > self.last_cleanup + self.cleanup_interval:
            self.clear_cache()
            self.last_cleanup = now

        if 'BEACON' not in entry['tags']:
            # Not a beacon, ignore
            self.stats.incr('beaconfilter/not_beacon')
            return False

        # Read from cache, or add to cache
        key = (entry['src'], entry['ssid'])
        strength = entry[self.strength_field]
        timestamp = time()

        cache = self.beacon_cache.get(key, None)
        if not cache:
            self.stats.incr('beaconfilter/cache_miss')
            cache_entry = CacheEntry(timestamp=time(),
                                     strength=strength)
            self.beacon_cache[key] = cache_entry
            return False
        else:
            self.stats.incr('beaconfilter/cache_hit')

        def update_cache():
            cache_entry = CacheEntry(timestamp=time(),
                                     strength=strength)
            self.beacon_cache[key] = cache_entry

        # Update case 1 - strength variation
        if abs(strength - cache.strength) >= self.max_strength_deviation:
            update_cache()
            return False

        # Update case 2 - time elapsed
        time_elapsed = timestamp - cache.timestamp
        if time_elapsed >= self.min_time_between:
            update_cache()
            return False

        return True

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
        cfg = {
            'cleanup_interval': config.get('cleanup_interval', 60),
            'max_strength_deviation': config.get('max_strength_deviation', 15),
            'min_time_between': config.get('min_time_between', 120),
            'timestamp_field': config.get('timestamp_field', 'timestamp'),
            'strength_field': config.get('strength_field', 'strength'),
        }
        stage = BeaconFilterStage(stats, **cfg)
        return stage
