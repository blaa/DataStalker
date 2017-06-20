# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

import struct
from time import time
import datetime

from scapy.layers.dot11 import Dot11Beacon
from scapy.layers.dot11 import Dot11WEP, Dot11Elt, Dot11
from scapy.layers.dot11 import Dot11ProbeReq, Dot11ProbeResp, Dot11Deauth, Dot11Auth
from scapy.modules import p0f

from .fields import *

from datastalker import utils

from . import log

class PacketParser:
    "Helper class used to parse incoming packets"

    def parse(self, p):
        "Parse packet and return metadata dictionary or None if unable to parse"
        data = self._parse_radiotap(p)
        if data is None:
            return

        self._parse_dot11(data, p.payload)

        data['_pkt'] = p
        return data


    def _parse_dot11(self, data, p):
        "Parse Dot11/Dot11Elt layers adding data to dict created during radiotap parse"
        tags = data['tags']

        # http://www.wildpackets.com/resources/compendium/wireless_lan/wlan_packet_types
        dot11 = p.getlayer(Dot11)
        d_type = dot11.type
        d_subtype = dot11.subtype

        tag = None
        if d_type == 0:
            # Management
            tags.add('MGMT')
            tag = mgmt_subtype_tag.get(d_subtype, None)

        elif d_type == 1:
            # Control
            tags.add('CTRL')
            tag = ctrl_subtype_tag.get(d_subtype, None)

        elif d_type == 2:
            # Data
            tags.add('DATA')

            # Alter destination within BSSID for broadcasts
            if data['dst'] == 'ff:ff:ff:ff:ff':
                if data['mac_addr3'] is not None and data['mac_addr3'] != mac_source:
                    print("SUBS", repr(radiotap))
                    data['dst'] = data['mac_addr3'] # Set from bssid

            return # Nothing more to do with data packet

        # Add tag related to subtype
        if tag:
            tags.add(tag)


        found_vendor = False

        # Recurrent Dot11 parsing
        orig_p = p
        while p:
            p = p.payload

            if type(p) == Dot11Beacon:
                ssid = p.info
                assert p.len == len(ssid)
                if data['ssid'] != None:
                    log.warning("SSID wasn't None before setting new value ({0} - {1})" % (data['ssid'],
                                                                                           repr(ssid)))
                data['ssid'] = self._sanitize(ssid)
                continue

            if type(p) != Dot11Elt:
                continue

            if p.ID == ELT_SSID:
                if found_vendor:
                    continue # After vendor, there are dragons

                ssid = p.info
                if p.len != len(ssid):
                    if data['ssid'] is None:
                        print("  Ignoring ssid, wrong length", repr(ssid), d_type, d_subtype, end=' ')
                        print("LEN IS/GIVEN", len(ssid), p.len)
                    continue
                if ssid and data['ssid'] is None:
                    ssid = self._sanitize(ssid)
                    data['ssid'] = ssid

            elif p.ID == ELT_DIRECT_SPECTRUM:
                if found_vendor:
                    continue # After vendor, there are dragons
                if p.len != len(p.info) or p.len != 1:
                    msg = "LENGTH %s DOESNT MATCH FOR CHANNEL type/subtype %d/%d" % (p.len, d_type, d_subtype)
                    log.warning(msg)
                    continue
                if data['channel'] is None:
                    data['channel'] = ord(p.info)
                    # TODO: How about 5ghz?
                    if data['channel'] < 0 or data['channel'] > 13:
                        msg = 'Ignoring invalid channel value for type/subtype %d/%d' % (d_type, d_subtype)
                        log.warning(msg)
                        data['channel'] = None

            elif p.ID == ELT_RSN:
                data['tags'].add('WPA2')

            elif p.ID == ELT_VENDOR:
                found_vendor = True
                if p.info.startswith(b'\x00P\xf2\x01\x01\x00'):
                    data['tags'].add('WPA')

            elif p.ID == ELT_QOS:
                data['tags'].add('QOS')


    def _sanitize(self, s):
        "Parse SSID fields"
        try:
            x = s.decode('utf-8')
        except:
            x = ''.join([i if ord(i) < 128 else ' ' for i in s])
        return x

    def _parse_radiotap(self, p):
        "Handle data from radiotap header"
        radiotap = p

        # If no source MAC - ignore packet
        if not hasattr(radiotap, 'addr2') or radiotap.addr2 is None:
            log.warning('Dropping packet with null addr2')
            return None

        tags = set()

        # P2P: Addr1 is destination, Addr2 is source

        # Through intermediate distribution system:
        # Addr1 is ultimate destination,
        # Addr2 is intermediate sender (AP sending to Addr1),
        # Addr3 is intermediate destination (AP receiving from Addr4),
        # and Addr4 is the original source
        mac_dst = radiotap.addr1
        mac_source = radiotap.addr2

        sig_str = radiotap.dbm_antsignal
        antenna = radiotap.antenna
        freq = radiotap.channel_freq

        if sig_str < -120 or sig_str > 0:
            sig_str = None

        # Broadcast within some bssid - alter destination
        if mac_dst == 'ff:ff:ff:ff:ff:ff':
            tags.add('BROADCAST')

        time = datetime.datetime.fromtimestamp(p.time)
        time = utils.localize(time)
        #print "LOCALIZED", time

        # Basic data
        data = {
            # UTC datetime
            'timestamp': time.astimezone(tz=utils.UTC),

            'src': mac_source,
            'dst': mac_dst,

            'addr1': radiotap.addr1,
            'addr2': radiotap.addr2,
            'addr3': radiotap.addr3,
            'addr4': radiotap.addr4,

            'strength': sig_str,
            'freq': freq,
            'antenna': antenna,

            # Defaults for dot11 parsing
            'ssid': None,
            'channel': None,
            'tags': tags,
        }
        return data
