import logging
log = logging.getLogger('root.pipeline')

from .exceptions import StopPipeline
from .stage import Message, Stage, SourceStage
from .pipeline import Pipeline

# Impor/register basic stages
from . import basic
