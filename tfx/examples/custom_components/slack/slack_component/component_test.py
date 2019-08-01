# Copyright 2019 Google LLC. All Rights Reserved.
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
"""Tests for slack component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from slack_component import component
import tensorflow as tf
from tfx import types
from tfx.types import channel_utils
from tfx.types import standard_artifacts


class ComponentTest(tf.test.TestCase):

  def setUp(self):
    self.model_export = channel_utils.as_channel(
        [types.Artifact(type=standard_artifacts.Model)])
    self.model_blessing = channel_utils.as_channel(
        [standard_artifacts.ModelBlessing()])

  def test_construct(self):
    slack_component = component.SlackComponent(
        model_export=self.model_export,
        model_blessing=self.model_blessing,
        slack_token='token',
        channel_id='channel_id',
        timeout_sec=3600)
    self.assertEqual('ModelBlessingPath',
                     slack_component.outputs.slack_blessing.type_name)


if __name__ == '__main__':
  tf.test.main()
