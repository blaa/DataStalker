# (C) 2015 - 2019 by Tomasz bla Fortuna
# License: MIT

from datastalker.pipeline import (
    SourceStage,
    Pipeline,
    Message
)
from datastalker.wifisniffer import Sniffer, Hopper

from datastalker.elasticsearch import ElasticMessage, schema

class SnifferMessage(ElasticMessage):
    """
    Message generated by WifiSniffer source stage.

    TODO: Manage schema for elasticsearch here.
    """
    MAPPING = {
        # Date in UTC for Kibana
        "timestamp": schema.DATE,
        "dst": schema.STR_NOT_ANALYZED,
        "src": schema.STR_NOT_ANALYZED,

        # Network card producer
        "dst_oui": schema.STR_NOT_ANALYZED,
        "src_oui": schema.STR_NOT_ANALYZED,

        # Channel and frequency of the received packet
        "channel": schema.INT,
        "freq": schema.INT,

        # Channel the hopper was configured for when the packet was received.
        # (because the 2.4GHz 802.11 channels overlap)
        "channel_hopper": schema.INT,

        "strength": schema.DOUBLE,

        # Generic tags mechanisms for boolean operators
        "tags": schema.STR_NOT_ANALYZED,

        # High level protocol data
        "hl_sport": schema.INT,
        "hl_dport": schema.INT,
        "hl_src": schema.STR_NOT_ANALYZED,
        "hl_dst": schema.STR_NOT_ANALYZED,
        "hl_dns": schema.STR_NOT_ANALYZED,

        "ssid": schema.STR,

        # Location
        "location": schema.GEO,
    }


@Pipeline.register_stage('wifi_sniffer')
class WifiSnifferStage(SourceStage):
    "Connect sniffer code to pipeline as a sourcestage"

    def __init__(self, sniffer):
        self.sniffer = sniffer

    def run(self):
        for packets in self.sniffer.run():
            messages = [
                SnifferMessage(packet)
                for packet in packets
            ]
            yield messages

    @classmethod
    def from_config(cls, config, stats):
        "Create sniffer with injected hopper from YAML configuration"

        name = config.get('name', 'default')
        interface = config.get('interface')
        related_interface = config.get('related_interface')

        hopper_cfg = config.get('hopper', None)

        if hopper_cfg is not None:
            channels = hopper_cfg.get('channels', None)
            max_karma = hopper_cfg.get('max_karma', None)
            hop_tries = hopper_cfg.get('hop_tries', 10)

            # Create hopper
            hopper = Hopper(interface, related_interface, stats,
                            hop_tries=hop_tries)
            hopper.configure(channels, max_karma)
        else:
            hopper = None

        # Create sniffer, inject hopper
        sniffer = Sniffer(interface,
                          related_interface,
                          hopper,
                          stats,
                          sniffer_name=name)

        stage = WifiSnifferStage(sniffer)
        return stage
