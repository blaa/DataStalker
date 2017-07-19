from time import time

class BeaconFilterStage(object):
    """Remove redundant information about beacons from pipeline.

    Stationary located receiver will receive a lot of beacons from other
    stationary APs with similar strength.
    """

    def __init__(self, cfg, stats):
        # Data for beacon filter; (mac, ssid) -> {last seen stamp,
        #                                         last stored str,
        #                                         cur averaged str}
        self.beacons = {}
        self.last_cleanup = time()

        self.stats = stats
        self.cfg = cfg

    def handle(self, entry):
        "Returns False to omit a entry, and True to include it"

        self.stats.incr('beaconfilter/frames_checked')

        if 'BEACON' not in entry['tags']:
            # Not a beacon, ignore
            self.stats.incr('beaconfilter/not_beacon')
            return entry

        # Clear cache from stale entries
        now = time()
        if now > self.last_cleanup + cfg['cleanup_interval']:
            self.stats.incr('beaconfilter/cleanups')

            self.last_cleanup = now
            drop_at = now - cfg['max_time_between']
            for key, cached_entry in self.beacons.items():
                if cached_entry[cfg['timestamp_field']] < drop_at:
                    del self.beacons[key]

        # Read from cache, or add to cache
        key = (entry['src'], entry['ssid'])
        cache = self.beacons.get(key, None)
        if not cache:
            self.stats.incr('beaconfilter/new_stored')

            strength = entry[cfg['strength_field']
            self.beacons[key] = {
                'stamp': entry[cfg['timestamp_field']]
                'stored_str': strength,
                'avg_str': strength,
            }
            return entry
        else:
            self.stats.incr('beaconfilter/cached')

        def update_cache():
            cache['stored_str'] = entry['strength']
            cache['stamp'] = entry['stamp']
            self.beacons_stored += 1

        # Update str
        if entry['strength'] is not None:
            # Can be none if it's our packet.
            cache['avg_str'] = (cache['avg_str'] * 5.0 + entry['strength']) / 6.0

        if abs(cache['avg_str'] - cache['stored_str']) >= cfg['max_str_dev']:
            update_cache()
            return True

        # Check time
        if cache['stamp'] + cfg['max_time_between'] < entry['timestamp_local']:
            update_cache()
            return True

        self.beacons_omitted += 1
        return False


    def debug(self):
        "Print filter stats"
        if self.frames_checked % 100 == 0:
            print "Beacon filter: filtered={0:.2f}% omitted={1} stored={2} checked={3} cache_size={4}".format(
                100.0 * self.beacons_omitted/(self.beacons_omitted + self.beacons_stored + 0.1),
                self.beacons_omitted, self.beacons_stored, self.frames_checked,
                len(self.beacons))

    @classmethod
    def from_config(cls, config, stats):
        "Build beaconfilter stage"

        cfg = {
            'cleanup_interval': config.get('cleanup_interval', 600)
            'max_str_deviation': config.get('max_str_deviation', 5)
            'max_time_between': config.get('max_time_between', 120)
            'timestamp_field': config.get('timestamp_field', '@timestamp')
            'strength_field': config.get('strength_field', '@timestamp')
        }

        stage = BeaconFilterStage(cfg, stats)

        return stage
