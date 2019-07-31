# (C) 2015 - 2019 by Tomasz bla Fortuna
# License: MIT

import os
import sys
from collections import defaultdict
from time import time, sleep

from datastalker import pythonwifi

import logging
log = logging.getLogger('root.hopper')

class Hopper(object):
    """
    Handle all logic regarding channel hopping.
    """
    def __init__(self, base_interface, related_interface,
                 stats, hop_tries=10):
        self.base_interface = base_interface
        self.related_interface = related_interface
        self.stats = stats

        self.wifi = None
        self.reset_interface()

        self.tries = hop_tries

    def __del__(self):
        del self.wifi

    def reset_interface(self):
        "Reset interface"
        if self.wifi is not None:
            del self.wifi
        if self.related_interface:
            log.info("Putting related interface (%s) down" % self.related_interface)
            os.system('ifconfig %s down' % self.related_interface)
        self.wifi = pythonwifi.Wireless(self.base_interface)


    def configure(self, channels=None, max_karma=None):

        self.freqs = {
            1: '2.412GHz',
            2: '2.417GHz',
            3: '2.422GHz',
            4: '2.427GHz',
            5: '2.432GHz',
            6: '2.437GHz',
            7: '2.442GHz',
            8: '2.447GHz',
            9: '2.452GHz',
            10: '2.457GHz',
            11: '2.462GHz',
            12: '2.467GHz',
            13: '2.472GHz',

            36: '5.180GHz',
            40: '5.200GHz',
            44: '5.220GHz',
            48: '5.240GHz',
            #(14, '2.484 Ghz'), # 14
        }

        # 5Mhz gap, 22MHz wide band.
        # Hopping: 1,6,11; (+2) 3,8,13; (+1) 2,7,12; (+3); 4,10,[14],5,9
        channels_default = [
            1,6,11, 3,8,13, 2,7,12, 4,10,5,9
        ]

        if channels is None:
            self.channels = channels_default
        else:
            self.channels = channels

        log.info("Hopping on the following channels: " +
                 ", ".join(str(ch) for ch in self.channels))

        if not self.channels:
            print("ERROR: No channels selected for hopping")
            return False

        self.hop_total = 0
        self.swipes_total = 0

        self.channel_idx = 0
        self.channel_number = -1 # Not yet known in fact
        self.channel_cnt = len(self.channels)
        self.channel_karma = 0
        self.max_karma = max_karma
        self.channel_inc = 0
        self.took = 0
        self.channel_swipe_start = time()
        return True

    def increase_karma(self):
        "Current channel is nice - stay here longer"
        if self.max_karma is None:
            return

        if self.channel_inc > self.max_karma:
            self.stats.incr('hopper/karmic/saturated')
            return

        self.stats.incr('hopper/karmic/inc')
        self.channel_karma += 1
        self.channel_inc += 1

    def hop(self):
        "Unconditional channel hop"
        self.channel_karma = 0
        self.channel_inc = 0

        start = time()

        self.stats.incr('hopper/hops')

        # Increment channel
        self.channel_idx = (self.channel_idx + 1) % self.channel_cnt
        self.channel_number = self.channels[self.channel_idx]
        freq = self.freqs[self.channel_number]

        # Update swipe statistics
        if self.channel_idx == 0:
            took = time() - self.channel_swipe_start
            self.swipes_total += 1
            self.channel_swipe_start = time()
            self.stats.incr('hopper/swipe/total')
            self.stats.incr('hopper/swipe/total_time', took)

        # Tries must fit within watchdog limit.
        last_exc = None
        for i in range(0, self.tries):
            try:
                self.wifi.setFrequency(freq)
                self.hop_total += 1
                return True
            except IOError as e:
                s = 'Try {0}/{1}: Channel hopping failed (f={1} ch={2})'
                log.info(s.format(i+1, self.tries,
                         freq, self.channel_number))
                self.reset_interface()
                self.stats.incr('hopper/fail/soft')
                sleep(0.8)
                last_exc = e

        self.stats.incr('hopper/fail/hard')

        log.info('Failure after %d failed hopping tries', i)
        if self.related_interface is None:
            log.info('Try setting related interface or putting interface UP')

        raise last_exc
        return False


    def karmic_hop(self):
        "Hop to the next channel, take karma into account"
        if self.channel_karma:
            self.channel_karma -= 1
            s = 'Staying a bit longer on {2}; karma={0} karma_inc={1}'
            print(s.format(self.channel_karma,
                           self.channel_inc,
                           self.channel_number))
            self.stats.incr('hopper/karmic/stay')
            return True

        self.stats.incr('hopper/karmic/hop')
        return self.hop()
