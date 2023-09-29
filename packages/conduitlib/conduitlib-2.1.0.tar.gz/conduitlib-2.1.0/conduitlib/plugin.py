# Copyright 2021 Software Factory Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module containing classes for Plugin and Trigger.
Also contains LoggerAdapters for the Plugin and Trigger classes."""

import logging
from typing import Any, Optional, MutableMapping
from . import util


class Plugin:
    """A `Plugin` for a `Workflow`.

    Used as a 'template' for a `Workflow` task. Gets instantiated each time a `Workflow` runs.

    Attributes:
        workflow (str): The name of the `Workflow` this `Plugin` is part of.
        instance_id (int): The instance ID of the `Workflow` run this `Plugin` (as a task) is
            part of.
        logger (logging.Logger): This `Plugin`'s logger.
    """

    def __init__(self, workflow: str, instance_id: int, args: Optional[dict[str, Any]] = None):
        """Initalize a `Plugin` object.

        Args:
            workflow (str): The name of the `Workflow` this plugin (as a task) is a part of.
            instance_id (int): The instance ID of the `Workflow` run this `Plugin` (as a task) is
                a part of.
            args (Optional[dict[str, Any]], optional): An optional dictionary containing arguments
                for this `Plugin`. Defaults to None.
        """
        self.workflow = workflow
        self.instance_id = instance_id
        self.args = args if args is not None else {}

        self.logger = PluginLoggerAdapter(util.get_class_logger(self),
                                          self.workflow,
                                          self.instance_id)

    def execute(self, data: Optional[dict] = None) -> Optional[dict]:
        """Execute the task instantiated using this `Plugin` in a `Workflow`.

        This must be overridden by a subclass.

        Args:
            data (Optional[dict[str, Any]], optional): Optional dictionary containing data from the
                previous workflow task. Defaults to None.

        Raises:
            NotImplementedError: When the sublcass has not overridden this.

        Returns:
            Optional[dict[str, Any]]: Containing data to pass on to the next workflow task, if any.
        """
        raise NotImplementedError


class Trigger:
    """A `Trigger` for a `Workflow`, used to determine when a `Workflow` executes.

    Attributes:
        workflow (str): The name of the `Workflow` this trigger is part of.
        args (Optional[dict[str, Any]]): Any additional arguments for this `Trigger`.
        logger (logging.Logger): This `Trigger`'s logger.
    """

    def __init__(self, workflow: str, args: Optional[dict] = None):
        """Initialize a `Trigger` object.

        Args:
            workflow (str): The name of the `Workflow` this trigger is part of.
            args (Optional[dict[str, Any]], optional): Optional dictionary containing arguments for
                this `Trigger`. Defaults to None.
        """
        self.workflow = workflow
        self.args = args if args is not None else {}

        self.logger = TriggerLoggerAdapter(util.get_class_logger(self), self.workflow)

    def run(self) -> None:
        """Initialize this `Trigger`.

        Raises:
            NotImplementedError: When the subclass has not overridden this.
        """
        raise NotImplementedError


class PluginLoggerAdapter(logging.LoggerAdapter):
    """`LoggerAdapter` for the `Plugin` class.

    Prepends `[WORKFLOW_NAME:INSTANCE_ID]` to the log message.

    Attributes:
        workflow (str): The name of the `Workflow` this logger is for.
        instance_id (int): The instance ID associated with the `Workflow` run.
    """

    def __init__(self, logger: logging.Logger, workflow: str, instance_id: int):
        """Initializes a `PluginLoggerAdapter`.

        Args:
            logger (logging.Logger): The base `Logger` this is adapting.
            workflow (str): The name of the `Workflow` this logger is for.
            instance_id (int): The instance ID associated with the `Workflow` run.
        """
        super().__init__(logger, {})
        self.workflow = workflow
        self.instance_id = instance_id

    def process(self, msg: str, kwargs: MutableMapping[str, Any]) -> tuple[str, Any]:
        """Process `Plugin` log messages by adding `Workflow` name and instance information.

        Args:
            msg (str): The log message.
            kwargs (dict[str, Any]): Keyword arguments provided to logger, unaltered.

        Returns:
            tuple[str, Any]: The log message prefixed with the `Workflow:instance_id` information
            and the unaltered keyword args used.
        """
        return f'[{self.workflow}:{self.instance_id}] {msg}', kwargs


class TriggerLoggerAdapter(logging.LoggerAdapter):
    """`LoggerAdapter` for the `Trigger` class.

    Prepends `[WORKFLOW_NAME]` to the log message.

    Attributes:
        workflow (str): The name of the `Workflow` this logger is for.
        instance_id (int): The instance ID associated with the `Workflow` run.
    """

    def __init__(self, logger: logging.Logger, workflow: str):
        """Initalizes a `TriggerLoggerAdapter`.

        Args:
            logger (logging.Logger): The base `Logger` this is adapting.
            workflow (str): The name of the `Workflow` this logger is for.
        """
        super().__init__(logger, {})
        self.workflow = workflow

    def process(self, msg: str, kwargs: MutableMapping[str, Any]) -> tuple[str, Any]:
        """Process `Trigger` log messages by adding `Workflow` name information.

        Args:
            msg (str): The log message.
            kwargs (dict[str, Any]): Keyword arguments provided to logger, unaltered.

        Returns:
            tuple[str, Any]: The log message prefixed with the `Workflow` name information
            and the unaltered keyword args used.
        """
        return f'[{self.workflow}] {msg}', kwargs
