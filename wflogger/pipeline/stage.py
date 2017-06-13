
"""
Pipeline interface definition. Not required really,
but used for documenting the API.
"""

class Stage:
    """
    Stage which reads data from previous stage and yields new data
    """
    def handle(self, data):
        "Handle incoming data and yield result"
        raise NotImplementedError

    @classmethod
    def from_config(cls, config):
        "Creates a stage object from part of YAML configuration file"
        raise NotImplementedError


class SourceStage:
    """
    Stage which starts the pipeline
    """
    def run(self):
        "Yield incoming data"
        raise NotImplementedError

    @classmethod
    def from_config(cls, config):
        "Creates a sourcestage object from part of YAML configuration file"
        raise NotImplementedError
