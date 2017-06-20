# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

from datastalker.pipeline import Stage, Pipeline
from datastalker.elasticsearch import model

@Pipeline.register_stage('elasticsearch')
class ElasticSearchStage(Stage):
    "Connect sniffer code to pipeline as a sourcestage"

    def __init__(self, db):
        self.db = db

    def handle(self, entry):
        self.db.store(entry)
        return entry

    @classmethod
    def from_config(cls, config):
        "Create sniffer with injected hopper from YAML configuration"

        hosts = config.get('hosts', ['127.0.0.1:9200'])

        mapping = config.get('mapping', {})
        index_template = config.get('index_template')
        time_field = config.get('time_field')
        doc_type = config.get('doc_type', 'doc')

        db = model.ElasticStorage(hosts,
                                  index_template,
                                  time_field,
                                  doc_type,
                                  mapping)

        stage = ElasticSearchStage(db)
        return stage
