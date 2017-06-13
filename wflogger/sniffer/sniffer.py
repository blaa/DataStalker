# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

import os
import sys
from time import time
from IPython import embed

from scapy import config, sendrecv

from .hopper import Hopper
from .parser import PacketParser

import logging
log = logging.getLogger()

class Sniffer(object):
    "Channel hopping, packet sniffing, parsing and finally storing"

    def __init__(self, interface, related_interface, hopper,
                 sniffer_name):

        self.hopper = hopper
        self.sniffer_name = sniffer_name
        self.interface = interface

        # Check interface existance
        if not self._iface_exists(interface):
            print("Exiting: Interface %s doesn't exist" % interface)
            sys.exit(1)

        if related_interface and not self._iface_exists(related_interface):
            print("Exiting: Related interface %s doesn't exist" % interface)
            sys.exit(1)

        # Submodules
        self.packet_parser = PacketParser()

        config.conf.sniff_promisc = 0
        log.info("Promiscuous mode disabled")


    def _iface_exists(self, iface_name):
        "Check if interface exists"
        path = '/sys/class/net'
        iface_path = os.path.join(path, iface_name)
        try:
            _ = os.stat(iface_path)
            return True
        except OSError:
            return False

    def run(self):
        "Sniffer main loop"

        begin = time()
        pkts_all = 0

        sniff_begin = time()
        stat_prev = sniff_begin
        stat_every = 3 # seconds
        while True:
            start = time()

            # This catches KeyboardInterrupt,
            # TODO: Disable this catching + Probably hop on another thread and use prn argument.
            # But then - you'd have watchdog problems.
            pkts = sendrecv.sniff(iface=self.interface, count=20, timeout=0.1)
            pkts_all += len(pkts)
            for pkt in pkts:
                data = self.packet_parser.parse(pkt)
                if data is None:
                    continue

                # Decorate with current hopper configuration
                if self.hopper:
                    data['ch'] = self.hopper.channel_number
                else:
                    data['ch'] = -1

                data['sniffer'] = self.sniffer_name

                if ('PROBE_REQ' in data['tags'] or
                    'PROBE_RESP' in data['tags'] or
                    'ASSOC_REQ' in data['tags'] or
                    'DISASS' in data['tags']):
                    # Increase karma when client traffic is detected
                    self.hopper.increase_karma()

                data['tags'] = list(data['tags'])
                yield data

            now = time()
            took = now - start

            if stat_prev + stat_every < now:
                took = time() - sniff_begin
                s = "STAT: pkts=%d t_total=%.2fs pps=%.2f"
                s %= (pkts_all, took, pkts_all / took)
                if self.hopper:
                    s2 = " swipes=%d avg_swipe_t=%.2f cur_ch=%d"
                    s2 %= (self.hopper.swipes_total,
                           took/(self.hopper.swipes_total + 0.001),
                           self.hopper.channel_number)
                    s += s2
                print(s)

                stat_prev = now

            # Hop if hopper is defined and channel karma is zero.
            if self.hopper is not None:
                ret = self.hopper.karmic_hop()
                if ret is False:
                    print("Stopping sniffer - unable to hop")
                    break

