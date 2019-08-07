# (C) 2015 - 2019 by Tomasz bla Fortuna
# License: MIT

"""
Abstract pipeline interface definition.
"""

from . import StopPipeline

class Message:
    """
    Base class which represents information passed within the Pipeline.
    """
    def __str__(self):
        "Used for printing to stdout"
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def serialize(self):
        """
        Return a dictionary representation
        """
        raise NotImplementedError


class Stage:
    """
    Stage which reads data from previous stage and yields new data
    """

    # Created by registering decorator
    log = None

    def handle(self, message):
        """
        Handle incoming data and return result

        Returns:
            None: to drop message from the pipeline.
            message: converted/augmented message.
            message list: multiple messages created from single one
        """
        raise NotImplementedError

    def handle_bulk(self, messages):
        "Naive handler for bulk of messages"
        output = []
        for message in messages:
            # Handling can return single message or multiple.
            message = self.handle(message)
            if isinstance(message, list):
                output += message
            elif message is not None:
                if not isinstance(message, Message):
                    self.log.error("Stage %s returned invalid message type: %s",
                                   self, type(message))
                    raise StopPipeline("Pipeline Error")
                output.append(message)
        return output

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
