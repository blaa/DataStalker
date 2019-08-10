# (C) 2015 - 2019 by Tomasz bla Fortuna
# License: MIT

"""
Abstract pipeline interface definition.
"""

from . import StopPipeline

class Message:
    """
    Base class which represents information passed within the Pipeline.

    Implements dict-like interface, should be simple and extendable.

    Should allow subclasses to support data and schema (elasticsearch schema).
    """
    def __init__(self, data):
        self.data = data

    # Dict-like interface
    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __contains__(self, key):
        return key in self.data

    def keys(self):
        return self.data.keys()

    # Debug interface
    def __str__(self):
        "Used for printing to stdout"
        def format_dict(d):
            if not isinstance(d, dict):
                return repr(d)
            return " ".join("{}={}".format(key, format_dict(value))
                            for key, value in d)
        return repr(self.data)

    def __repr__(self):
        return "<Message %r>" % self.data


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
