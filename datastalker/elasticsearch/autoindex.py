# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

class AutoIndex(object):
    "Base class which handles index creation for descendants"

    def __init__(self, time_field, index_format):
        self.index_format = index_format
        self.time_field = time_field

        # Indices created in ES by this object instance
        # Keep them and don't recreate them.
        self._created_idx = set()

    def get_index(self, entry):
        "Get index name for given date"
        date = entry[self.time_field]
        name = date.strftime(self.index_format)
        return name

    def get_schema(self):
        "Returns dictionary with index configuration"
        raise NotImplementedError

    def create_index(self, index_name):
        "Create index with given configuration"
        if index_name in self._created_idx:
            return

        settings = self.get_schema()

        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(index=index_name,
                                   body=settings)
            self._created_idx.add(index_name)
