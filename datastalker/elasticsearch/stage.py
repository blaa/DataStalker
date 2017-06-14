# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

from datastalker.pipeline import Stage, Pipeline
from datastalker.elasticsearch import model

@Pipeline.register_stage('elasticsearch')
class ElasticSearchStage(Stage):
    "Connect sniffer code to pipeline as a sourcestage"

    def __init__(self, model):
        self.model = model

    def handle(self, entry):
        print("ES Storing", entry)
        return entry

    @classmethod
    def from_config(cls, config):
        "Create sniffer with injected hopper from YAML configuration"

        index = config.get('index')
        port = config.get('port', 9200)
        host = config.get('hostname', '127.0.0.1')

        mapping = config.get('mapping', {})

        model = None

        stage = ElasticSearchStage(model=model)
        return stage
