# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

import os
import sys
from time import time

from scapy import config, sendrecv

from .hopper import Hopper
from .parser import PacketParser

from . import log


class Sniffer:
    "Channel hopping, packet sniffing, parsing and finally storing"

    def __init__(self, interface, related_interface,
                 hopper, stats, sniffer_name):

        self.hopper = hopper
        self.sniffer_name = sniffer_name
        self.interface = interface
        self.stats = stats

        # Check interface existance
        if not self._iface_exists(interface):
            raise Exception("Interface %s doesn't exist" % interface)

        if related_interface and not self._iface_exists(related_interface):
            raise Exception("Exiting: Related interface %s doesn't exist" % related_interface)

        # Submodules
        self.packet_parser = PacketParser()

        config.conf.sniff_promisc = 0
        log.info("Promiscuous mode disabled in Scapy")

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

        if self.hopper is not None:
            self.hopper.hop()

        while True:
            start = time()

            # NOTE: This catches KeyboardInterrupt,
            # TODO: Disable this catching + Probably hop on another
            # thread and use prn argument.
            pkts = sendrecv.sniff(iface=self.interface, count=20, timeout=0.1)
            pkts_all += len(pkts)
            output = []

            for raw_pkt in pkts:
                packet = self.packet_parser.parse(raw_pkt)
                if packet is None:
                    continue

                # Decorate with current hopper configuration
                if self.hopper is not None:
                    packet['channel_hopper'] = self.hopper.channel_number
                else:
                    packet['channel_hopper'] = -1

                packet['sniffer'] = self.sniffer_name

                if ('PROBE_REQ' in packet['tags'] or
                    'PROBE_RESP' in packet['tags'] or
                    'ASSOC_REQ' in packet['tags'] or
                    'DISASS' in packet['tags']):
                    # Increase karma when client traffic is detected
                    self.hopper.increase_karma()

                # Lists are serializable, sets no - convert.
                packet['tags'] = list(packet['tags'])

                self.stats.incr('wifisniffer/frames')
                output.append(packet)

            yield output

            # Show stats
            now = time()
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
                log.info(s)

                stat_prev = now

            # Hop if hopper is defined and channel karma is zero.
            if self.hopper is not None:
                ret = self.hopper.karmic_hop()
                if ret is False:
                    log.error("Stopping sniffer - unable to hop")
                    break

