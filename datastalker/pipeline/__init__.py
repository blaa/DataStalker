import logging
log = logging.getLogger('root.pipeline')

from .stage import Stage, SourceStage
from .pipeline import Pipeline

# Impor/register basic stages
from . import basic
