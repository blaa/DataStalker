# (C) 2015 - 2019 by Tomasz bla Fortuna
# License: MIT

import logging
from time import time

from datastalker.pipeline import SourceStage, StopPipeline

from . import log
from .stats import Stats

class Pipeline:
    """
    Creates a pipeline and handles flow of the data within the logger.
    """

    def __init__(self):
        self._stages = []
        self.stats = Stats()

    def build(self, configuration):
        "Build pipeline using given configuration"
        builder = PipelineBuilder()
        self._stages = builder.build(configuration, self.stats)

    def run(self):
        "Run pipeline"
        source = self._stages[0]
        operations = self._stages[1:]

        log.warning('Entering pipeline')
        pipeline_start = time()
        try:
            for messages in source.run():
                start = time()
                for stage in operations:
                    messages = stage.handle_bulk(messages)

                    if not messages:
                        # Stop iteration of this message - None or []
                        self.stats.incr('pipeline/dropped')
                        break

                took = time() - start
                self.stats.incr('pipeline/entries')
                self.stats.incr('pipeline/stages_total_s', took)

        except StopPipeline as e:
            log.info("Pipeline stopped on software request: %s", e.args[0])
        except KeyboardInterrupt:
            log.info("Pipeline stopped on keyboard request")

        took = time() - pipeline_start
        self.stats.incr('pipeline/total_s', took)
        self.stats.dump()

    @staticmethod
    def register_stage(name):
        "Decorator which registers stage class in the pipeline"
        def decorator(stage_cls):
            if name in PipelineBuilder._registered:
                raise Exception("Stage with that name already defined")
            PipelineBuilder._registered[name] = stage_cls
            stage_cls.log = logging.getLogger('root.stage.' + name)
            return stage_cls
        return decorator


class PipelineBuilder:
    """
    Pipeline builder: Creates the pipeline, handles registration of stages.

    Private API; no need to use it externally - use Pipeline class.
    """

    # Registered stages: {stagename: stage class, ...}
    _registered = {}

    def build(self, configuration, stats):
        "Build pipeline using given configuration"
        pipeline = []
        for stage_def in configuration:
            if isinstance(stage_def, str):
                # Stage without configuration
                stage_name, stage_config = stage_def, {}
            else:
                assert len(stage_def) == 1
                stage_name, stage_config = list(stage_def.items())[0]

            stage_cls = PipelineBuilder._registered.get(stage_name, None)
            if stage_cls is None:
                raise Exception("Stage name '{}' is not defined".format(stage_name))

            try:
                stage = stage_cls.from_config(stage_config, stats)
            except:
                log.error('Error while building stage: %s', stage_name)
                raise
            pipeline.append(stage)

        if len(pipeline) < 1:
            raise Exception("Generated pipeline needs at least one SourceStage")

        if not isinstance(pipeline[0], SourceStage):
            raise Exception("First pipeline stage must be a SourceStage")

        return pipeline
