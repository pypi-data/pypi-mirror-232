"""This module implements Kedro boot session responsible for kedro boot app lifecycle."""

import logging
import uuid
from typing import List

from kedro.io import DataCatalog
from kedro.pipeline import Pipeline

from kedro_boot.catalog import AppCatalog, KedroBootCatalog
from kedro_boot.pipeline import KedroBootPipeline, PipelineSpec
from .utils import find_duplicates

LOGGER = logging.getLogger(__name__)


class KedroBootSession:
    """``KedroBootSession`` is the object that is responsible for managing kedro boot app lifecycle.
    It used BaseKedroResource to compile
    """

    def __init__(
        self, pipeline: Pipeline, catalog: DataCatalog, hook_manager, session_id
    ) -> None:
        """_summary_

        Args:
            pipeline (Pipeline): _description_
            catalog (DataCatalog): _description_
            hook_manager (_type_): _description_
            session_id (_type_): _description_
        """
        self._pipeline = KedroBootPipeline(pipeline)
        self._catalog = KedroBootCatalog(catalog)
        self._hook_manager = hook_manager
        self._session_id = session_id

        self._is_compiled_catalog = None

    def compile_catalog(
        self,
        pipeline_specs: List[PipelineSpec] = None,
    ) -> None:
        if self._is_compiled_catalog:
            raise KedroBootSessionError("Kedro boot catalog is already compiled")

        if pipeline_specs:
            duplicate_namespace = find_duplicates(
                [pipeline_spec.namespace for pipeline_spec in pipeline_specs]
            )
            if duplicate_namespace:
                raise KedroBootSessionError(
                    f"The given kedro specs contains duplicate namespaces {duplicate_namespace}. Please give one unique namespace per kedro spec."
                )
        else:
            pipeline_specs = [PipelineSpec()]

        self._pipeline.compile(pipeline_specs)
        self._catalog.compile(self._pipeline.pipeline_modules)

        self._is_compiled_catalog = True

    def run(
        self, namespace: str = None, app_catalog: AppCatalog = None, run_id: str = None
    ) -> dict:
        run_id = run_id or uuid.uuid4().hex
        app_catalog = app_catalog or AppCatalog()

        if not self._is_compiled_catalog:
            self.compile_catalog()

        if namespace not in self._pipeline.get_namespaces():
            raise KedroBootSessionError(
                f"The given app resource namespace'{namespace}' is not present in kedro resources {self._pipeline.get_namespaces()}."
            )

        pipeline_module = self._pipeline.get_pipeline_module(namespace)
        pipeline = pipeline_module.pipeline
        catalog = self._catalog.render(namespace=namespace, app_catalog=app_catalog)
        runner = pipeline_module.runner

        LOGGER.info(f"Running iteration {run_id}")
        runner.run(
            pipeline=pipeline,
            catalog=catalog,
            hook_manager=self._hook_manager,
            session_id=self._session_id,
        )

        outputs = pipeline_module.outputs

        if outputs and len(outputs) > 1:
            returned_datasets = {
                dataset_name: catalog.load(dataset_name) for dataset_name in outputs
            }
        elif outputs and len(outputs) == 1:
            returned_datasets = catalog.load(outputs[0])
        else:
            returned_datasets = {
                dataset_name: catalog.load(dataset_name)
                for dataset_name in pipeline.outputs()
                if catalog._data_sets[dataset_name].__class__.__name__.lower()
                == "memorydataset"
            }

        LOGGER.info(f"Iteration {run_id} completed")

        return returned_datasets


class KedroBootSessionError(Exception):
    """Error raised in catalog rendering operations"""
