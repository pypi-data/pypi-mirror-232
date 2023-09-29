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

"""Utility functions."""
import logging
import inspect


def get_class_logger(obj: object) -> logging.Logger:
    """Obtains a logger object for a class.

    Args:
        obj (object): The class object.

    Returns:
        logging.Logger: The class' logger.
    """
    klass = list(filter(lambda m: m[0] == '__class__', inspect.getmembers(obj)))[0][1]
    cls_name = str(klass)[8:-2]
    return logging.getLogger(cls_name)
