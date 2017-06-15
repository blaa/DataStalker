# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

from datastalker.pipeline import SourceStage

from . import log

class Pipeline:
    """
    Creates a pipeline and handles flow of the data within the logger.
    """

    class StopPipeline(Exception):
        "Raised in stages to stop pipeline cleanly"
        pass

    def __init__(self):
        self._stages = []

    def build(self, configuration):
        "Build pipeline using given configuration"
        builder = PipelineBuilder()
        self._stages = builder.build(configuration)

    def run(self):
        "Run pipeline"
        source = self._stages[0]
        operations = self._stages[1:]

        log.warning('Entering pipeline')
        try:
            for entry in source.run():
                for stage in operations:
                    entry = stage.handle(entry)

                    if entry is None:
                        # Stop iteration of this entry
                        break
        except Pipeline.StopPipeline as e:
            log.info("Pipeline stopped on software request: %s", e.args[0])
        except KeyboardInterrupt:
            log.info("Pipeline stopped on keyboard request")


    @staticmethod
    def register_stage(name):
        "Decorator which registers stage class in the pipeline"
        def decorator(stage_cls):
            if name in PipelineBuilder._registered:
                raise Exception("Stage with that name already defined")
            PipelineBuilder._registered[name] = stage_cls
            return stage_cls
        return decorator


class PipelineBuilder:
    """
    Pipeline builder: Creates the pipeline, handles registration of stages.

    Private API; no need to use it externally - use Pipeline class.
    """

    # Registered stages: {stagename: stage class, ...}
    _registered = {}

    def build(self, configuration):
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

            stage = stage_cls.from_config(stage_config)
            pipeline.append(stage)

        if len(pipeline) < 1:
            raise Exception("Generated pipeline needs at least one SourceStage")

        if not isinstance(pipeline[0], SourceStage):
            raise Exception("First pipeline stage must be a SourceStage")

        return pipeline
