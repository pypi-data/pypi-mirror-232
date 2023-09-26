import logging
from typing import List

from kedro.io import DataCatalog

from ..pipeline import PipelineModule, namespacing_datasets
from .compiler import (
    compile_with_pipeline_input,
    compile_with_pipeline_intermediary,
    compile_with_pipeline_output,
)
from .container import AppCatalog, CatalogTemplate
from .renderer import (
    renderDatasets,
    renderInputDatasets,
    renderParamDatasets,
    renderTemplatizedDatasets,
)

LOGGER = logging.getLogger(__name__)


class KedroBootCatalog:
    def __init__(self, catalog: DataCatalog) -> None:
        self.base_catalog = catalog

        self.catalog_templates = []

    def compile(self, pipeline_modules: List[PipelineModule]):
        for pipeline_module in pipeline_modules:
            catalog_template = CatalogTemplate(namespace=pipeline_module.namespace)

            for dataset_name in pipeline_module.pipeline.data_sets():
                dataset_value = self.base_catalog._data_sets[dataset_name]

                if dataset_name in pipeline_module.pipeline.inputs():
                    compile_with_pipeline_input(
                        dataset_name, dataset_value, pipeline_module, catalog_template
                    )
                elif dataset_name in pipeline_module.pipeline.outputs():
                    compile_with_pipeline_output(
                        dataset_name, dataset_value, pipeline_module, catalog_template
                    )
                else:
                    compile_with_pipeline_intermediary(
                        dataset_name, dataset_value, pipeline_module, catalog_template
                    )

            self.catalog_templates.append(catalog_template)

            # self._compile_with_pipeline_dataset(dataset_name=dataset_name, dataset_value=dataset_value, pipeline_module=pipeline_module, catalog_template=catalog_template)

            # if not catalog_template.outputs:
            #     LOGGER.warning(
            #         f"No output datasets were given for the current pipeline namespace '{catalog_template.namespace}'. We gonna return all free pipeline outputs"
            #     )

            LOGGER.info(
                "Catalog compilation completed for the namespace '%s'. Here is the report:\n"
                "  - Input datasets to be replaced/rendered at iteration time by the kedro app: %s\n"
                "  - Artifact datasets to be materialized (preloader as memory dataset) at startup time: %s\n"
                "  - Templatized datasets to be rendered at iteration time by the kedro app: %s\n"
                "  - Output datasets that hold the data to be returned to the kedro app at iteration time: %s",
                catalog_template.namespace,
                set(catalog_template.inputs),
                set(catalog_template.artifacts),
                set(catalog_template.templatized),
                set(catalog_template.outputs),
            )

    def render(self, namespace: str, app_catalog: AppCatalog) -> DataCatalog:
        catalog_template = self.get_catalog_template(namespace)

        namespaced_app_datasets = namespacing_datasets(
            namespace=namespace,
            app_datasets=app_catalog.datasets,
            kedro_datasets=catalog_template.inputs,
        )
        namespaced_app_catalog_params = namespacing_datasets(
            namespace=namespace,
            app_datasets=app_catalog.catalog_params,
            kedro_datasets=catalog_template.params,
        )

        rendered_catalog = DataCatalog()

        inputs_datasets = renderInputDatasets(
            datasets=catalog_template.inputs, app_datasets=namespaced_app_datasets
        )
        artifact_datasets = catalog_template.artifacts
        templatized_datasets = renderTemplatizedDatasets(
            datasets=catalog_template.templatized,
            app_template_params=app_catalog.template_params,
        )
        params_datasets = renderParamDatasets(
            datasets=catalog_template.params,
            app_catalog_params=namespaced_app_catalog_params,
        )
        output_datasets = renderDatasets(datasets=catalog_template.outputs)
        unmanaged_datasets = renderDatasets(datasets=catalog_template.unmanaged)

        rendered_catalog.add_all(
            {
                **inputs_datasets,
                **artifact_datasets,
                **templatized_datasets,
                **params_datasets,
                **output_datasets,
                **unmanaged_datasets,
            }
        )

        return rendered_catalog

    def get_catalog_template(self, namespace: str) -> CatalogTemplate:
        return next(
            (
                catalog_template
                for catalog_template in self.catalog_templates
                if catalog_template.namespace == namespace
            ),
            None,
        )


class KedroBootCatalogError(Exception):
    """Error raised in Kedro catalog resources operations"""
