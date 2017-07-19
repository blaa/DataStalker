# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

"""
Pipeline interface definition. Not required really,
but used for documenting the API.
"""

class Stage:
    """
    Stage which reads data from previous stage and yields new data
    """

    # Created by registering decorator
    log = None

    def handle(self, data):
        "Handle incoming data and return result"
        raise NotImplementedError

    @classmethod
    def from_config(cls, config):
        "Creates a stage object from part of YAML configuration file"
        raise NotImplementedError


class SourceStage:
    """
    Stage which starts the pipeline
    """

    # Created by registering decorator
    log = None

    def run(self):
        "Yield incoming data"
        raise NotImplementedError

    @classmethod
    def from_config(cls, config):
        "Creates a sourcestage object from part of YAML configuration file"
        raise NotImplementedError
