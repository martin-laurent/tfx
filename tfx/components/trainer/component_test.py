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
"""Tests for tfx.components.trainer.component."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from tfx.components.trainer import component
from tfx.proto import trainer_pb2
from tfx.types import channel_utils
from tfx.types import standard_artifacts


class ComponentTest(tf.test.TestCase):

  def test_construct(self):
    transformed_examples = standard_artifacts.Examples()
    transform_output = standard_artifacts.TransformResult()
    schema = standard_artifacts.Schema()
    trainer = component.Trainer(
        module_file='/path/to/module/file',
        examples=channel_utils.as_channel([transformed_examples]),
        transform_output=channel_utils.as_channel([transform_output]),
        schema=channel_utils.as_channel([schema]),
        train_args=trainer_pb2.TrainArgs(num_steps=100),
        eval_args=trainer_pb2.EvalArgs(num_steps=50))
    self.assertEqual('ModelExportPath', trainer.outputs.output.type_name)

  def test_construct_without_transform_output(self):
    transformed_examples = standard_artifacts.Examples()
    schema = standard_artifacts.Schema()
    trainer = component.Trainer(
        module_file='/path/to/module/file',
        examples=channel_utils.as_channel([transformed_examples]),
        schema=channel_utils.as_channel([schema]),
        train_args=trainer_pb2.TrainArgs(num_steps=100),
        eval_args=trainer_pb2.EvalArgs(num_steps=50))
    self.assertEqual('ModelExportPath', trainer.outputs.output.type_name)


if __name__ == '__main__':
  tf.test.main()
