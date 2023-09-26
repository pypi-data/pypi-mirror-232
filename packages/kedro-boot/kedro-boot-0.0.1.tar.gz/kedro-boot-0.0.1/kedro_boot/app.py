"""``AbstractKedroBootApp`` is the base class for all kedro boot app implementations.
"""
from abc import ABC, abstractmethod
from typing import Any

from kedro.config import ConfigLoader
from kedro.io import DataCatalog
from kedro.pipeline import Pipeline
from pluggy import PluginManager

from kedro_boot.session import KedroBootSession


class AbstractKedroBootApp(ABC):
    """``AbstractKedroBootApp`` is the base class for all kedro boot app implementations"""

    def __init__(self, config_loader: ConfigLoader = None) -> None:
        """Instantiate kedro boot app class

        Args:
            config_loader (ConfigLoader, optional): kedro config loader. Defaults to None.
        """

        super().__init__()
        self.config_loader = config_loader

    def run(
        self,
        pipeline: Pipeline,
        catalog: DataCatalog,
        hook_manager: PluginManager,
        session_id: str,
    ) -> Any:
        """Create a ``KedroBootSession`` then run the kedro boot app

        Args:
            pipeline: The ``Pipeline`` to be used by the app.
            catalog: The ``DataCatalog`` from which to fetch data.
            hook_manager: The ``PluginManager`` to activate hooks.
            session_id: The id of the kedro session.

        Returns:
            Any: The value return by kedro boot app at it's end of execution
        """
        return self._run(
            KedroBootSession(
                pipeline=pipeline,
                catalog=catalog,
                hook_manager=hook_manager,
                session_id=session_id,
            )
        )

    @abstractmethod
    def _run(self, session: KedroBootSession) -> Any:
        """The abstract interface for running kedro boot apps, assuming that the
        ``KedrobootSession`` have already be created by run().

        Args:
            session (KedroBootSession): is the object that is responsible for managing the kedro boot app lifecycle
        """
        pass


class DummyApp(AbstractKedroBootApp):
    def _run(self, session: KedroBootSession) -> Any:
        return session.run()
