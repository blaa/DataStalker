# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

from datastalker.pipeline import SourceStage, Pipeline
from datastalker.wifisniffer import Sniffer, Hopper

@Pipeline.register_stage('wifi_sniffer')
class WifiSnifferStage(SourceStage):
    "Connect sniffer code to pipeline as a sourcestage"

    def __init__(self, sniffer):
        self.sniffer = sniffer

    def run(self):
        yield from self.sniffer.run()

    @classmethod
    def from_config(cls, config):
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
            hopper = Hopper(interface, related_interface,
                            hop_tries=hop_tries)
            hopper.configure(channels, max_karma)
        else:
            hopper = None

        # Create sniffer, inject hopper
        sniffer = Sniffer(interface,
                          related_interface,
                          hopper,
                          sniffer_name=name)

        stage = WifiSnifferStage(sniffer)
        return stage
