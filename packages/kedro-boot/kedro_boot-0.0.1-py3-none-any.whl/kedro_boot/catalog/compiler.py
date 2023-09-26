import logging
import re
from pathlib import PurePath
from typing import Any, List, Union

from jinja2 import Environment, meta
from kedro.io import MemoryDataSet

from ..pipeline import PipelineModule
from .container import CatalogTemplate

LOGGER = logging.getLogger(__name__)


def compile_with_pipeline_input(
    dataset_name: str,
    dataset_value: Any,
    pipeline_module: PipelineModule,
    catalog_template: CatalogTemplate,
) -> None:
    if pipeline_module.inputs:
        if dataset_name in pipeline_module.inputs:
            catalog_template.inputs[dataset_name] = dataset_value
        elif recursively_check_dataset_parametrized_values(dataset_value):
            catalog_template.templatized[dataset_name] = dataset_value
        elif pipeline_module.artifacts:
            if dataset_name in pipeline_module.artifacts:
                catalog_template.artifacts[dataset_name] = MemoryDataSet(
                    dataset_value.load(), copy_mode="assign"
                )
            else:
                catalog_template.unmanaged[dataset_name] = dataset_value
        else:
            catalog_template.artifacts[dataset_name] = MemoryDataSet(
                dataset_value.load(), copy_mode="assign"
            )
    else:
        if "parameters" in dataset_name or "params:" in dataset_name:
            catalog_template.params[dataset_name] = dataset_value
        elif recursively_check_dataset_parametrized_values(dataset_value):
            catalog_template.templatized[dataset_name] = dataset_value
        else:
            catalog_template.unmanaged[dataset_name] = dataset_value


def compile_with_pipeline_output(
    dataset_name: str,
    dataset_value: Any,
    pipeline_module: PipelineModule,
    catalog_template: CatalogTemplate,
) -> None:
    if dataset_name in pipeline_module.outputs:
        if dataset_value.__class__.__name__.lower() != "memorydataset":
            raise CatalogCompilerError(
                f"Only MemoryDataset are allowed as output resource. We got {dataset_value.__class__.__name__} for {dataset_name} output dataset."
            )
        catalog_template.outputs[dataset_name] = dataset_value
    elif recursively_check_dataset_parametrized_values(dataset_value):
        catalog_template.templatized[dataset_name] = dataset_value
    else:
        if (
            dataset_value.__class__.__name__.lower() != "memorydataset"
            and pipeline_module.outputs
        ):
            LOGGER.warning(
                f"This pipeline output {dataset_name} will cost you an I/O operation without being used by current app, please consider freeing it. the pipeline outputs that are needed by the current pipeline namespace ({catalog_template.namespace}) are : {pipeline_module.outputs}"
            )
        catalog_template.unmanaged[dataset_name] = dataset_value


def compile_with_pipeline_intermediary(
    dataset_name: str,
    dataset_value: Any,
    pipeline_module: PipelineModule,
    catalog_template: CatalogTemplate,
) -> None:
    if recursively_check_dataset_parametrized_values(dataset_value):
        catalog_template.templatized[dataset_name] = dataset_value
    else:
        if dataset_value.__class__.__name__.lower() != "memorydataset" and (
            pipeline_module.inputs or pipeline_module.outputs
        ):
            LOGGER.warning(
                f"{dataset_name} dataset will cost you an I/O operation without being used by current pipeline namespace ({catalog_template.namespace}), please consider freeing it"
            )
        catalog_template.unmanaged[dataset_name] = dataset_value


def recursively_check_parametrized_values(
    dataset_attributes: Union[str, list, dict, PurePath]
) -> bool:
    if isinstance(dataset_attributes, str):
        return bool(re.search(r"\[\[.*?\]\]", dataset_attributes))

    elif isinstance(dataset_attributes, PurePath):
        return bool(re.search(r"\[\[.*?\]\]", str(dataset_attributes)))

    elif isinstance(dataset_attributes, dict):
        for key in dataset_attributes:
            if recursively_check_parametrized_values(dataset_attributes[key]):
                return True
        return False

    elif isinstance(dataset_attributes, list):
        for i in range(len(dataset_attributes)):
            if recursively_check_parametrized_values(dataset_attributes[i]):
                return True
        return False

    else:
        return False


def recursively_check_dataset_parametrized_values(dataset: Any) -> bool:
    for attr, value in dataset.__dict__.items():
        if recursively_check_parametrized_values(value):
            return True
    return False


class CatalogCompilerError(Exception):
    """Error raised in Kedro catalog resources operations"""
