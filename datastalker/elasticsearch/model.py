# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT
from elasticsearch import Elasticsearch, helpers

from .autoindex import AutoIndex

class ElasticStorage(AutoIndex):
    "Link to ElasticSearch + model factory"

    def __init__(self, connections,
                 index_format,
                 time_field,
                 doc_type,
                 mapping):

        # Init auto index
        super(ElasticStorage, self).__init__(time_field,
                                             index_format)

        self.doc_type = doc_type
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
                                doc_type=self.doc_type,
                                body=frame)

            if ret['created'] != True:
                log.error('Error while creating entries in Elasticsearch')
                raise Exception('Elasticsearch storage error: %r' % ret)
        except:
            print("Frame storage failed on:")
            print(repr(frame))
            raise


    schema_parts = {
        'str_analyzed': { "type": "string", "index": "analyzed" },
        'str_not_analyzed': { "type": "string", "index": "not_analyzed" },
        'str': {
            "type": "string",
            "index": "analyzed",
            "fields": {
                "keyword": {
                    "type": "string",
                    "index": "not_analyzed"
                },
            }
        },
        'integer': { "type": "integer" },
        'date': { "type": "date" },
        'double': { "type": "double" },
        'boolean': { "type": "boolean" },
        'geo': { "type": "geo_point" },
    }

    def get_schema(self):
        "Get the correct schema for the ES"
        sp = self.schema_parts

        settings = {
            'number_of_shards': 1,
            'index.codec': 'best_compression',
        }

        properties = {
            # Date in UTC for Kibana
            "@timestamp": sp['date'],
            "dst": sp['str_not_analyzed'],
            "src": sp['str_not_analyzed'],

            # Network card producer
            "dst_oui": sp['str_not_analyzed'],
            "src_oui": sp['str_not_analyzed'],


            # Channel and frequency of the received packet
            "channel": sp['integer'],
            "freq": sp['integer'],

            # Channel the hopper was configured for when the packet was received.
            # (because the 2.4GHz 802.11 channels overlap)
            "channel_hopper": sp['integer'],

            "strength": sp['double'],

            # Generic tags mechanisms for boolean operators
            "tags": sp['str_not_analyzed'],

            # High level protocol data
            "hl_sport": sp['integer'],
            "hl_dport": sp['integer'],
            "hl_src": sp['str_not_analyzed'],
            "hl_dst": sp['str_not_analyzed'],
            "hl_dns": sp['str_not_analyzed'],

            "ssid": sp['str'],

            # Location
            "location": sp['geo'],
        }

        # Allow user to drop default mapping
        use_default_mapping = self.mapping.get('_use_default_mapping', True)
        if use_default_mapping is False:
            properties = {}

        for key, key_map in self.mapping.items():
            if isinstance(key_map, str):
                if key_map not in sp:
                    raise Exception("Unknown mapping for elasticsearch: %s" % key_map)
                key_map = sp[key_map]
            properties[key] = key_map

        # Combine into ES api
        schema = {
            'settings': settings,
            'mappings': {
                self.doc_type: {
                    'properties': properties
                }
            }
        }

        return schema
