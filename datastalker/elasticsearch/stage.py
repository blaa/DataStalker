# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

from datastalker.pipeline import Stage, Pipeline, Message
from datastalker.elasticsearch import model, schema
from . import log

class ElasticMessage(Message):
    """
    Add support for elasticsearch schemas
    """
    SHARDS = 1
    CODEC = "best_compression"

    MAPPING = {
        # Date in UTC for Kibana
        "timestamp": schema.DATE,
    }

    def get_mapping(self):
        return self.MAPPING.copy()


@Pipeline.register_stage('elasticsearch')
class ElasticStage(Stage):
    "Connect sniffer code to pipeline as a sourcestage"

    def __init__(self, storage, stats):
        self.storage = storage
        self.stats = stats

    def handle(self, message):
        assert isinstance(message, ElasticMessage)
        self.storage.store(message)
        self.stats.incr('elasticsearch/stored')
        return message

    @classmethod
    def from_config(cls, config, stats):
        "Create sniffer with injected hopper from YAML configuration"

        hosts = config.get('hosts', ['127.0.0.1:9200'])

        mapping = config.get('mapping', {})
        index_template = config.get('index_template')
        time_field = config.get('time_field')

        storage = model.ElasticStorage(hosts,
                                       index_template,
                                       time_field,
                                       mapping)

        stage = ElasticSearchStage(storage, stats)
        log.info("Elasticsearch stage initialized")
        return stage
