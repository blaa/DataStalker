# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT
from elasticsearch import Elasticsearch, helpers

from . import schema

class ElasticStorage:
    "Link to ElasticSearch + model factory"

    def __init__(self, connections,
                 index_format,
                 time_field,
                 mapping):

        # Auto indexing
        self.index_format = index_format
        self.time_field = time_field

        # Cache: indices created in ES by this object instance.
        self._created_idx = set()

        # Property mapping configuration
        self.mapping = mapping

        # Connection object
        self.es = Elasticsearch(connections)

    def get_index(self, entry):
        "Get index name for given date"
        date = entry[self.time_field]
        name = date.strftime(self.index_format)
        return name

    def create_index(self, index_name, message):
        "Create index with given configuration"
        if index_name in self._created_idx:
            return

        settings = self.get_schema(message)

        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(index=index_name,
                                   body=settings)
            self._created_idx.add(index_name)

    def get_schema(self, message):
        "Get the correct schema for the ES"

        settings = {
            'number_of_shards': 1,
            'index.codec': 'best_compression',
        }

        # Allow user to drop default mapping
        use_default_mapping = self.mapping.get('use_default_mapping', True)
        if use_default_mapping is False:
            properties = {}
        else:
            assert isinstance(message, ElasticMessage)
            properties = message.get_mapping()

        for key, key_map in self.mapping.items():
            if isinstance(key_map, str):
                if key_map.upper() not in schema.__dict__:
                    raise Exception("Unknown mapping for elasticsearch: %s" % key_map)
                key_map = schema.__dict__[key_map.upper()]
            properties[key] = key_map

        # Combine into ES API
        spec = {
            'settings': settings,
            'mappings': {
                'properties': properties
            }
        }

        return spec

    def store(self, message):
        "Add message to the database"
        try:
            idx_name = self.get_index(message)
            self.create_index(idx_name, message)

            ret = self.es.index(index=idx_name,
                                body=message.data)

            if ret['result'] != 'created':
                log.error('Error while creating entries in Elasticsearch')
                raise Exception('Elasticsearch storage error: %r' % ret)
        except:
            print("Message storage failed on:")
            print(repr(message))
            raise

