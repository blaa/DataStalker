# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT
from elasticsearch import Elasticsearch, helpers

from .autoindex import AutoIndex
from . import schema

class ElasticStorage(AutoIndex):
    "Link to ElasticSearch + model factory"

    def __init__(self, connections,
                 index_format,
                 time_field,
                 mapping):

        # Init auto index
        super(ElasticStorage, self).__init__(time_field,
                                             index_format)

        self.mapping = mapping

        # Connection object
        self.es = Elasticsearch(connections)

    def store(self, frame):
        "Add frame to the database"
        #self.all_frames.insert(metadata)
        try:
            idx_name = self.get_index(frame)
            self.create_index(idx_name)

            ret = self.es.index(index=idx_name,
                                body=frame)

            if ret['result'] != 'created':
                log.error('Error while creating entries in Elasticsearch')
                raise Exception('Elasticsearch storage error: %r' % ret)
        except:
            print("Frame storage failed on:")
            print(repr(frame))
            raise

    def get_schema(self):
        "Get the correct schema for the ES"

        settings = {
            'number_of_shards': 1,
            'index.codec': 'best_compression',
        }

        properties = {
            # Date in UTC for Kibana
            "@timestamp": schema.DATE,
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

        # Allow user to drop default mapping
        use_default_mapping = self.mapping.get('_use_default_mapping', True)
        if use_default_mapping is False:
            properties = {}

        for key, key_map in self.mapping.items():
            if isinstance(key_map, str):
                if key_map.upper() not in schema.__dict__:
                    raise Exception("Unknown mapping for elasticsearch: %s" % key_map)
                key_map = schema.__dict__[key_map.upper()]
            properties[key] = key_map

        # Combine into ES api
        spec = {
            'settings': settings,
            'mappings': {
                'properties': properties
            }
        }

        return spec
