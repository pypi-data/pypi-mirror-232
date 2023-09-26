"""A collection of CLI commands for working with Kedro project."""

import logging
from typing import List

import click
from click import Command, Option
from kedro.framework.cli.project import run as kedro_run_command
from kedro.framework.cli.utils import _get_values_as_tuple
from kedro.framework.session import KedroSession

from kedro_boot.runner import KedroBootRunner

LOGGER = logging.getLogger(__name__)


def kedro_boot_cli_factory(
    app_class: str = None, app_params: List[Option] = None
) -> Command:
    app_params = app_params or []
    # No app_class given. We'll add an app Option in the Command and use DummyApp as default
    if not app_class:
        for app_param in app_params:
            if app_param.name == "app":
                LOGGER.warning(
                    "No app_class was given and at the same time 'app' Option is found in the kedro boot cli factory app_params. We're going to replace your app Option by kedro boot app Option. So you can have a way to provide an app_class"
                )
                app_params.remove(app_param)
                break

        app_params.append(
            click.option(
                "--app",
                type=str,
                default="kedro_boot.app.DummyApp",
                help="Kedro Boot App Class",
            )
        )

    @click.command()
    def kedro_boot_command(**kwargs):
        """New command with all the existing run options plus a new option."""

        ctx = click.get_current_context()
        kedro_run_params = [param.name for param in kedro_run_command.params]
        app_args = {
            arg_key: arg_value
            for arg_key, arg_value in ctx.params.items()
            if arg_key not in kedro_run_params
        }
        kedro_args = {
            arg_key: arg_value
            for arg_key, arg_value in kwargs.items()
            if arg_key not in app_args
        }

        # pop the app_class from app_args
        boot_app_class = app_class or app_args.pop("app")

        tag = _get_values_as_tuple(kedro_args["tag"])
        node_names = _get_values_as_tuple(kedro_args["node_names"])

        # temporary duplicates for the plural flags
        tags = _get_values_as_tuple(kedro_args["tags"])
        nodes_names = _get_values_as_tuple(kedro_args["nodes_names"])

        tag = tag + tags
        node_names = node_names + nodes_names
        load_version = {**kedro_args["load_version"], **kedro_args["load_versions"]}

        with KedroSession.create(
            env=kedro_args["env"],
            conf_source=kedro_args["conf_source"],
            extra_params=kedro_args["params"],
        ) as session:
            runner_args = {"is_async": kedro_args["is_async"]}
            config_loader = session._get_config_loader()
            runner = KedroBootRunner(
                config_loader=config_loader,
                app_class=boot_app_class,
                app_args=app_args,
                **runner_args
            )
            session.run(
                tags=tag,
                runner=runner,
                node_names=node_names,
                from_nodes=kedro_args["from_nodes"],
                to_nodes=kedro_args["to_nodes"],
                from_inputs=kedro_args["from_inputs"],
                to_outputs=kedro_args["to_outputs"],
                load_versions=load_version,
                pipeline_name=kedro_args["pipeline"],
                namespace=kedro_args["namespace"],
            )

    kedro_boot_command.params.extend(kedro_run_command.params)
    for param in app_params:
        kedro_boot_command = param(kedro_boot_command)

    return kedro_boot_command
