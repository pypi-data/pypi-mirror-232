from typing import Any

from kedro.config import ConfigLoader
from kedro.framework.hooks.manager import _NullPluginManager
from kedro.io import DataCatalog, MemoryDataSet
from kedro.pipeline import Pipeline
from kedro.runner import AbstractRunner
from kedro.utils import load_obj
from pluggy import PluginManager


class KedroBootRunner(AbstractRunner):
    def __init__(
        self,
        config_loader: ConfigLoader,
        app_class: str,
        app_args: dict = None,
        **runner_args,
    ):
        super().__init__(**runner_args)

        app_args = app_args or {}
        print(app_args)
        self.app_obj = (
            load_obj(app_class)(config_loader=config_loader, **app_args)
            if app_args
            else load_obj(app_class)(config_loader=config_loader)
        )

    def run(
        self,
        pipeline: Pipeline,
        catalog: DataCatalog,
        hook_manager: PluginManager = None,
        session_id: str = None,
    ) -> Any:
        """Run the ``Pipeline`` using the datasets provided by ``catalog``
        and save results back to the same objects.

        Args:
            pipeline: The ``Pipeline`` to run.
            catalog: The ``DataCatalog`` from which to fetch data.
            hook_manager: The ``PluginManager`` to activate hooks.
            session_id: The id of the session.

        Raises:
            ValueError: Raised when ``Pipeline`` inputs cannot be satisfied.

        """

        hook_manager = hook_manager or _NullPluginManager()
        catalog = catalog.shallow_copy()

        unsatisfied = pipeline.inputs() - set(catalog.list())
        if unsatisfied:
            raise ValueError(
                f"Pipeline input(s) {unsatisfied} not found in the DataCatalog"
            )

        unregistered_ds = pipeline.data_sets() - set(catalog.list())
        for ds_name in unregistered_ds:
            catalog.add(ds_name, self.create_default_data_set(ds_name))

        if self._is_async:
            self._logger.info(
                "Asynchronous mode is enabled for loading and saving data"
            )

        app_return = self._run(pipeline, catalog, hook_manager, session_id)
        self._logger.info(f"{self.app_obj.__class__.__name__} execution completed.")
        return app_return

    def _run(self, *args) -> Any:
        return self.app_obj.run(*args)

    def create_default_data_set(self, ds_name: str):
        return MemoryDataSet()
