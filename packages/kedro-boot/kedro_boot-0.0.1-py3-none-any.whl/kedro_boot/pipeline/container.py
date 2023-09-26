import logging
from typing import List

from kedro.pipeline import Pipeline
from kedro.runner import AbstractRunner, SequentialRunner

LOGGER = logging.getLogger(__name__)


class PipelineSpec:
    def __init__(
        self,
        namespace: str = None,
        inputs: List[str] = None,
        outputs: List[str] = None,
        artifacts: List[str] = None,
        runner: AbstractRunner = None,
    ) -> None:
        self.namespace = namespace
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.artifacts = artifacts or []
        self.runner = runner


class PipelineModule:
    def __init__(
        self,
        namespace: str,
        pipeline: Pipeline,
        inputs: List[str],
        outputs: List[str],
        artifacts: List[str],
        runner: AbstractRunner = None,
    ) -> None:
        self.namespace = namespace
        self.pipeline = pipeline
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.artifacts = artifacts or []
        self.runner = runner or SequentialRunner()
