# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from typing import Optional

from submarine.entities._submarine_object import _SubmarineObject


class ModelVersion(_SubmarineObject):
    """
    Model version object.
    """

    def __init__(
        self,
        name: str,
        version: int,
        id: str,
        user_id: str,
        experiment_id: str,
        model_type: str,
        current_stage: str,
        creation_time: datetime,
        last_updated_time: datetime,
        dataset: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list] = None,
    ):
        self._name = name
        self._version = version
        self._id = id
        self._user_id = user_id
        self._experiment_id = experiment_id
        self._model_type = model_type
        self._current_stage = current_stage
        self._creation_time = creation_time
        self._last_updated_time = last_updated_time
        self._dataset = dataset
        self._description = description
        self._tags = [tag.tag for tag in (tags or [])]

    @property
    def name(self):
        """String. Registered model name"""
        return self._name

    @property
    def version(self):
        """Integer. version"""
        return self._version

    @property
    def id(self):
        """String. ID of the model"""
        return self._id

    @property
    def user_id(self):
        """String. User ID that created this version."""
        return self._user_id

    @property
    def experiment_id(self):
        """String. Experiment ID that created this version."""
        return self._experiment_id

    @property
    def model_type(self):
        """String. Type of model."""
        return self._model_type

    @property
    def creation_time(self):
        """Datetime object. The creation datetime of this version."""
        return self._creation_time

    @property
    def last_updated_time(self):
        """Datetime object. Datetime of last update for this version."""
        return self._last_updated_time

    @property
    def current_stage(self):
        """String. Current stage of this version."""
        return self._current_stage

    @property
    def dataset(self):
        """String. Dataset used for this version."""
        return self._dataset

    @property
    def description(self):
        """String. Description"""
        return self._description

    @property
    def tags(self) -> list:
        """List of strings."""
        return self._tags
