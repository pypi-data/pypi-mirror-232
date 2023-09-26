import logging
from typing import List, Union

from kedro.pipeline import Pipeline

from .container import PipelineModule, PipelineSpec

LOGGER = logging.getLogger(__name__)


class KedroBootPipeline:
    # def __init__(self, namespace: str, inputs: list, outputs: list, artifacts: list) -> None:
    def __init__(self, pipeline: Pipeline) -> None:
        self.base_pipeline = pipeline

        self.pipeline_modules = []

    def compile(self, pipeline_specs: List[PipelineSpec] = None) -> None:
        for pipeline_spec in pipeline_specs:
            if pipeline_spec.namespace:
                base_pipeline_module = self.base_pipeline.only_nodes_with_namespace(
                    pipeline_spec.namespace
                )
            else:
                base_pipeline_module = Pipeline(
                    nodes=[
                        node
                        for node in self.base_pipeline.nodes
                        if node.namespace is None
                    ]
                )

            namespaced_inputs = namespacing_datasets(
                namespace=pipeline_spec.namespace,
                app_datasets=pipeline_spec.inputs,
                kedro_datasets=list(base_pipeline_module.inputs()),
            )
            namespaced_artifacts = namespacing_datasets(
                namespace=pipeline_spec.namespace,
                app_datasets=pipeline_spec.artifacts,
                kedro_datasets=list(base_pipeline_module.inputs()),
            )
            namespaced_outputs = namespacing_datasets(
                namespace=pipeline_spec.namespace,
                app_datasets=pipeline_spec.outputs,
                kedro_datasets=list(base_pipeline_module.outputs()),
            )

            remaining_pipeline_resource_inputs = set(namespaced_inputs) - set(
                base_pipeline_module.inputs()
            )
            if remaining_pipeline_resource_inputs:
                raise KedroBootPipelineError(
                    f"These app inputs {remaining_pipeline_resource_inputs} are not present in kedro pipeline inputs for namespace '{pipeline_spec.namespace}'"
                )

            remaining_pipeline_resource_outputs = set(namespaced_outputs) - set(
                base_pipeline_module.outputs()
            )
            if remaining_pipeline_resource_outputs:
                raise KedroBootPipelineError(
                    f"These app outputs {remaining_pipeline_resource_outputs} are not present in kedro pipeline outputs for namespace '{pipeline_spec.namespace}'"
                )

            pipeline_module = PipelineModule(
                namespace=pipeline_spec.namespace,
                pipeline=base_pipeline_module,
                inputs=namespaced_inputs,
                outputs=namespaced_outputs,
                artifacts=namespaced_artifacts,
            )
            self.pipeline_modules.append(pipeline_module)

    def get_pipeline_module(self, namespace: str) -> PipelineModule:
        return next(
            (
                pipeline_module
                for pipeline_module in self.pipeline_modules
                if pipeline_module.namespace == namespace
            ),
            None,
        )

    def get_pipeline_module_inputs(self, namespace: str) -> List[str]:
        return self.get_pipeline_module(namespace).inputs

    def get_pipeline_module_outputs(self, namespace: str) -> List[str]:
        return self.get_pipeline_module(namespace).outputs

    def get_namespaces(self) -> List[str]:
        return [pipeline_module.namespace for pipeline_module in self.pipeline_modules]


def namespacing_datasets(
    namespace: str, app_datasets: Union[list, dict], kedro_datasets: Union[list, dict]
) -> Union[list, dict]:
    if namespace:
        if isinstance(app_datasets, list):
            namespaced_datasets = []
            for app_dataset in app_datasets:
                if f"{namespace}.{app_dataset}" in kedro_datasets:
                    namespaced_datasets.append(f"{namespace}.{app_dataset}")
                else:
                    namespaced_datasets.append(app_dataset)
            return namespaced_datasets

        if isinstance(app_datasets, dict):
            namespaced_datasets = {}
            for dataset_name, dataset_value in app_datasets.items():
                if f"{namespace}.{dataset_name}" in kedro_datasets:
                    namespaced_datasets[f"{namespace}.{dataset_name}"] = dataset_value
                else:
                    namespaced_datasets[dataset_name] = dataset_value

            return namespaced_datasets

    return app_datasets


class KedroBootPipelineError(Exception):
    """Error raised in Kedro resources operations"""
