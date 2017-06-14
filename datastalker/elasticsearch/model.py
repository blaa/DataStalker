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
        super(ElasticStorage).__init__(time_field,
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

            if self.beacon_filter.filter(frame):
                ret = self.es.index(index=idx_name,
                                    doc_type=self.doc_type,
                                    body=frame)
                print("RET ", ret)
        except:
            print "Frame storage failed on:"
            print repr(frame)
            raise

    schema_parts = {
        'str_analyzed': { "type": "string", "index": "analyzed" },
        'str_not_analyzed': { "type": "string", "index": "not_analyzed" },
        # TODO: Add .raw
        'str': { "type": "string", "index": "not_analyzed" },

    }

    def get_schema(self):
        settings = {
            'number_of_shards': 1,
            'index.codec': 'best_compression',
        }

        properties = {
            # Date in UTC for Kibana
            "@timestamp": { "type": "date" },
            "dst": { "type": "string", "index": "not_analyzed" },
            "src": { "type": "string", "index": "not_analyzed" },

            "channel": {
                "type": "integer",
            },

            "freq": {
                "type": "integer",
            },

            "strength": {
                "type": "double",
            },

            "broadcast": {
                "type": "boolean",
            },

            # Generic tags mechanisms
            "tags": {
                "type": "string",
                "index": "not_analyzed",
            },

            "label": {
                "type": "string",
                "index": "not_analyzed",
            },
                
            "hl_sport": {"type": "integer" },
            "hl_dport": {"type": "integer" },
            "hl_src": {"type": "string", "index": "not_analyzed" },
            "hl_dst": {"type": "string", "index": "not_analyzed" },
            "hl_dns": {"type": "string", "index": "not_analyzed" },

            "ssid": {
                "type": "string",
                "index": "not_analyzed",
                },

                # Location
            "location": { "type": "geo_point" },
        }

        schema = {
            'settings': settings,
            'mappings': {
                self.doc_type: {
                    'properties': properties
                }
            }
        }
