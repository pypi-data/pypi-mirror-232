import copy
import logging
from pathlib import PurePath
from typing import Any, List, Union

import pandas as pd
from jinja2 import Environment, Template, meta
from kedro.io import MemoryDataSet

LOGGER = logging.getLogger(__name__)


def renderDatasets(datasets: dict) -> dict:
    return {
        dataset_name: copy.deepcopy(dataset_value)
        for dataset_name, dataset_value in datasets.items()
    }


def renderTemplatizedDatasets(datasets: dict, app_template_params: dict):
    kedro_template_params = recursively_get_dataset_template_params(datasets)
    remaining_kedro_tempate_params = (
        set(kedro_template_params) - app_template_params.keys()
    )
    if remaining_kedro_tempate_params:
        raise CatalogRendererError(
            f"The is not enough given app_template_params to render all the kedro_template_params. kedro template params datasets are {set(kedro_template_params)} and the actual given app template params are {set(app_template_params)}. {remaining_kedro_tempate_params} cannot be rendered"
        )

    remaining_app_template_params = app_template_params.keys() - set(
        kedro_template_params
    )
    log_message = f"There is remaining app template params that are not used for rendering kedro template params. kedro template params are {set(kedro_template_params)} and the actual given app template params are {set(app_template_params)}. {remaining_app_template_params} are remaining unused"
    if remaining_app_template_params == {"run_id"}:
        LOGGER.info(log_message)
    if len(remaining_app_template_params) > 1:
        LOGGER.warning(log_message)

    rendered_datasets = {}
    for dataset_name, dataset_value in datasets.items():
        # rendered_dataset_name = contextualize_dataset_name(dataset_name, rendered_id)
        rendered_dataset_value = copy.deepcopy(dataset_value)
        recursively_render_parametrized_dataset_template(
            rendered_dataset_value, app_template_params
        )
        rendered_datasets[dataset_name] = rendered_dataset_value

    return rendered_datasets


def renderParamDatasets(datasets: dict, app_catalog_params: dict) -> dict:
    formatted_app_catalog_params = {f"params:{param}" for param in app_catalog_params}
    formated_dataset_params = {
        f"params:{param}" for param in datasets.get("parameters").load()
    }

    remaining_app_catalog_params = set(formatted_app_catalog_params) - set(
        formated_dataset_params
    )
    if remaining_app_catalog_params:
        LOGGER.warning(
            f"There is remainig app catalog params that are not used for rendering kedro catalog params. kedro catalog params are {datasets.keys()} and the actual given app catalog params are {formatted_app_catalog_params}. {remaining_app_catalog_params} are remaining unused"
        )
    rendered_datasets = {}

    for dataset_name, dataset_value in datasets.items():
        # rendered_dataset_name = contextualize_dataset_name(dataset_name, rendered_id)

        rendered_dataset_value = copy.deepcopy(dataset_value)

        if dataset_name in formatted_app_catalog_params:
            rendered_datasets[dataset_name] = MemoryDataSet(
                formatted_app_catalog_params[dataset_name]
            )
        elif dataset_name == "parameters":
            parameters = rendered_dataset_value.load()
            parameters.update(app_catalog_params)
            rendered_datasets[dataset_name] = MemoryDataSet(parameters)
        else:
            rendered_datasets[dataset_name] = rendered_dataset_value

    return rendered_datasets


def renderInputDatasets(datasets: dict, app_datasets: dict) -> dict:
    remaining_input_datasets = set(datasets) - set(app_datasets)

    if remaining_input_datasets:
        raise CatalogRendererError(
            f"There is not enough app datasets to render compiled kedro inputs datasets. compiled kedro inputs datasets are {set(datasets)} and the actual given app datasets are {set(app_datasets)}."
        )

    rendered_datasets = {}

    for dataset_name, dataset_value in datasets.items():
        # rendered_dataset_name = contextualize_dataset_name(dataset_name, rendered_id)
        rendered_dataset_value = copy.deepcopy(dataset_value)
        if "pandas" in str(rendered_dataset_value.__class__).lower():
            LOGGER.info(f"Converting {dataset_name} to pandas")
            rendered_dataset_value = MemoryDataSet(
                pd.json_normalize(app_datasets[dataset_name])
            )
        else:
            rendered_dataset_value = MemoryDataSet(app_datasets[dataset_name])
        rendered_datasets[dataset_name] = rendered_dataset_value

    return rendered_datasets


def recursively_render_template(
    dataset_attributes: Union[str, list, dict, PurePath], template_args: dict
) -> Union[None, str, list, dict, PurePath]:
    if isinstance(dataset_attributes, str):
        return Template(
            dataset_attributes, variable_start_string="[[", variable_end_string="]]"
        ).render(template_args)

    elif isinstance(dataset_attributes, PurePath):
        return PurePath(
            Template(
                str(dataset_attributes),
                variable_start_string="[[",
                variable_end_string="]]",
            ).render(template_args)
        )

    elif isinstance(dataset_attributes, dict):
        for key in dataset_attributes:
            dataset_attributes[key] = recursively_render_template(
                dataset_attributes[key], template_args
            )
        return dataset_attributes

    elif isinstance(dataset_attributes, list):
        for i in range(len(dataset_attributes)):
            dataset_attributes[key] = recursively_render_template(
                dataset_attributes[i], template_args
            )
        return dataset_attributes

    else:
        return dataset_attributes


def recursively_render_parametrized_dataset_template(dataset: Any, template_args: dict):
    for attr, value in dataset.__dict__.items():
        setattr(dataset, attr, recursively_render_template(value, template_args))


def recursively_get_dataset_template_params(datasets: dict) -> List[str]:
    template_params = []
    for ds_key, ds_value in datasets.items():
        for attr, value in ds_value.__dict__.items():
            template_params.extend(recursively_get_template_params(value))
    return template_params


env = Environment(variable_start_string="[[", variable_end_string="]]")


def recursively_get_template_params(
    dataset_attributes: Union[str, list, dict, PurePath]
) -> List[str]:
    if isinstance(dataset_attributes, str):
        return list(meta.find_undeclared_variables(env.parse(dataset_attributes)))

    elif isinstance(dataset_attributes, PurePath):
        return list(meta.find_undeclared_variables(env.parse(str(dataset_attributes))))

    elif isinstance(dataset_attributes, dict):
        template_params = []
        for key in dataset_attributes:
            template_params.extend(
                recursively_get_template_params(dataset_attributes[key])
            )
        return template_params

    elif isinstance(dataset_attributes, list):
        template_params = []
        for dataset_attribute in dataset_attributes:
            template_params.extend(recursively_get_template_params(dataset_attribute))
        return template_params

    else:
        return []


class CatalogRendererError(Exception):
    """Error raised in catalog rendering operations"""
