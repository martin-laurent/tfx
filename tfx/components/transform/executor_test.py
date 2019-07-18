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
"""Tests for tfx.components.transform.executor."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import tempfile
import tensorflow as tf
import tensorflow_transform as tft

from tfx.components.testdata.module_file import transform_module
from tfx.components.transform import executor
from tfx.utils import types


# TODO(b/122478841): Add more detailed tests.
class ExecutorTest(tf.test.TestCase):

  def _get_output_data_dir(self, sub_dir=None):
    test_dir = self._testMethodName
    if sub_dir is not None:
      test_dir = os.path.join(test_dir, sub_dir)
    return os.path.join(
        os.environ.get('TEST_UNDECLARED_OUTPUTS_DIR', self.get_temp_dir()),
        test_dir)

  def _make_base_do_params(self, source_data_dir, output_data_dir):
    # Create input dict.
    train_artifact = types.TfxArtifact('ExamplesPath', split='train')
    train_artifact.uri = os.path.join(source_data_dir, 'csv_example_gen/train/')
    eval_artifact = types.TfxArtifact('ExamplesPath', split='eval')
    eval_artifact.uri = os.path.join(source_data_dir, 'csv_example_gen/eval/')
    schema_artifact = types.TfxArtifact('Schema')
    schema_artifact.uri = os.path.join(source_data_dir, 'schema_gen/')

    self.input_dict = {
        'input_data': [train_artifact, eval_artifact],
        'schema': [schema_artifact],
    }

    # Create output dict.
    self.transformed_output = types.TfxArtifact('TransformPath')
    self.transformed_output.uri = os.path.join(output_data_dir,
                                               'transformed_output')
    self.transformed_train_examples = types.TfxArtifact(
        'ExamplesPath', split='train')
    self.transformed_train_examples.uri = os.path.join(output_data_dir,
                                                       'train')
    self.transformed_eval_examples = types.TfxArtifact(
        'ExamplesPath', split='eval')
    self.transformed_eval_examples.uri = os.path.join(output_data_dir,
                                                      'eval')
    temp_path_output = types.TfxArtifact('TempPath')
    temp_path_output.uri = tempfile.mkdtemp()

    self.output_dict = {
        'transform_output': [self.transformed_output],
        'transformed_examples': [
            self.transformed_train_examples, self.transformed_eval_examples
        ],
        'temp_path': [temp_path_output],
    }

    # Create exec properties skeleton.
    self.exec_properties = {}

  def setUp(self):
    super(ExecutorTest, self).setUp()

    self.source_data_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'testdata')
    self.output_data_dir = self._get_output_data_dir()

    self._make_base_do_params(self.source_data_dir, self.output_data_dir)

    # Create exec properties skeleton.
    self.module_file = os.path.join(self.source_data_dir,
                                    'module_file/transform_module.py')
    self.preprocessing_fn = '%s.%s' % (
        transform_module.preprocessing_fn.__module__,
        transform_module.preprocessing_fn.__name__)

    # Executor for test.
    self.transform_executor = executor.Executor()

  def _verify_transform_outputs(self):
    self.assertNotEqual(
        0, len(tf.gfile.ListDirectory(self.transformed_train_examples.uri)))
    self.assertNotEqual(
        0, len(tf.gfile.ListDirectory(self.transformed_eval_examples.uri)))
    path_to_saved_model = os.path.join(
        self.transformed_output.uri, tft.TFTransformOutput.TRANSFORM_FN_DIR,
        tf.saved_model.constants.SAVED_MODEL_FILENAME_PB)
    self.assertTrue(tf.gfile.Exists(path_to_saved_model))

  def test_do_with_module_file(self):
    self.exec_properties['module_file'] = self.module_file
    self.transform_executor.Do(self.input_dict, self.output_dict,
                               self.exec_properties)
    self._verify_transform_outputs()

  def test_do_with_preprocessing_fn(self):
    self.exec_properties['preprocessing_fn'] = self.preprocessing_fn
    self.transform_executor.Do(self.input_dict, self.output_dict,
                               self.exec_properties)
    self._verify_transform_outputs()

  def test_do_with_no_preprocessing_fn(self):
    with self.assertRaises(ValueError):
      self.transform_executor.Do(self.input_dict, self.output_dict,
                                 self.exec_properties)

  def test_do_with_duplicate_preprocessing_fn(self):
    self.exec_properties['module_file'] = self.module_file
    self.exec_properties['preprocessing_fn'] = self.preprocessing_fn
    with self.assertRaises(ValueError):
      self.transform_executor.Do(self.input_dict, self.output_dict,
                                 self.exec_properties)

  def test_do_with_cache(self):
    # First run that creates cache.
    output_cache_artifact = types.TfxArtifact('OutputCache')
    output_cache_artifact.uri = os.path.join(self.output_data_dir, 'CACHE/')

    self.output_dict['cache_output_path'] = [output_cache_artifact]

    self.exec_properties['module_file'] = self.module_file
    self.transform_executor.Do(self.input_dict, self.output_dict,
                               self.exec_properties)
    self._verify_transform_outputs()
    self.assertNotEqual(0,
                        len(tf.gfile.ListDirectory(output_cache_artifact.uri)))

    # Second run from cache.
    self.output_data_dir = self._get_output_data_dir('2nd_run')
    input_cache_artifact = types.TfxArtifact('InputCache')
    input_cache_artifact.uri = output_cache_artifact.uri

    output_cache_artifact = types.TfxArtifact('OutputCache')
    output_cache_artifact.uri = os.path.join(self.output_data_dir, 'CACHE/')

    self._make_base_do_params(self.source_data_dir, self.output_data_dir)

    self.input_dict['cache_input_path'] = [input_cache_artifact]
    self.output_dict['cache_output_path'] = [output_cache_artifact]

    self.exec_properties['module_file'] = self.module_file
    self.transform_executor.Do(self.input_dict, self.output_dict,
                               self.exec_properties)

    self._verify_transform_outputs()
    self.assertNotEqual(0,
                        len(tf.gfile.ListDirectory(output_cache_artifact.uri)))


if __name__ == '__main__':
  tf.test.main()
