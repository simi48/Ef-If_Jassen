# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""Contains the Policy class for mixed precision training."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib

from tensorflow.python.training.experimental import mixed_precision_global_state
from tensorflow.python.util.tf_export import keras_export


@keras_export('keras.mixed_precision.experimental.Policy')
class Policy(object):
  """A mixed precision policy for a Keras layer.

  A mixed precision policy determines the floating-point dtype that Keras layers
  should create variables in. For non-default policies, if the variable dtype
  does not match the input dtype, variables will automatically be casted to the
  input dtype to avoid type errors. Policies can be passed to the 'dtype'
  argument of layer constructors, or a global policy can be set with
  'set_policy'.

  In the near future, policies will also determine the computation dtype of
  layers, as well as the loss scaling algorithm.

  Policies are intended to enable mixed precision training, which require using
  float32 variables and [b]float16 computations for most layers. The term "mixed
  precision" refers to the use of both float16 (or bfloat16) and float32 in a
  model. See https://arxiv.org/abs/1710.03740 for more information on mixed
  precision training.

  Note: We currently recommend using mixed precision through an alternative
  function: `tf.train.experimental.enable_mixed_precision_graph_rewrite`. This
  alternative function enables mixed precision under the hood, by rewriting the
  graph to use float16 for certain ops. This alternative function is currently
  more complete and easy to use than using a Policy. However, compared to
  `enable_mixed_precision_graph_rewrite`, using a Policy supports Eager mode
  outside `tf.function`s/`tf.keras.Model`s, and a Policy gives you more control
  over what parts of the model are done in what dtype.

  Policies are constructed by passing a string to the `name` constructor
  argument. `name` determines the behavior of the policy. Currently, `name` can
  be one of the following values.

    * 'infer': Infer the variable and computation dtypes from the input dtype.
      This is the default behavior.
    * 'infer_float32_vars': Infer the computation dtypes from the input
      dtype, but create variables in float32. Variables will be casted to the
      computation dtype. This is intended to enable mixed precision. Users can
      cast tensors to float16 before passing them to a layer, which causes the
      layer to run it's computation in float16 while keeping variables in
      float32.

  To use mixed precision in a model, the 'infer_float32_vars' policy can be used
  alongside float16 input tensors, which results in float16 computations and
  float32 variables. For example:

  ```python
  tf.keras.mixed_precision.experimental.set_policy('infer_float32_vars')
  model = tf.keras.models.Sequential(
      tf.keras.layers.Input((100,), dtype='float16'),
      tf.keras.layers.Dense(10),
      tf.keras.layers.Dense(10),
      tf.keras.layers.Lambda(lambda x: tf.cast(x, 'float32')),
      tf.keras.layers.Activation('Softmax')
  )
  ```

  Alternatively, the policy can be passed to individual layers instead of
  setting the global policy with `set_policy`:

  ```python
  policy = tf.keras.mixed_precision.experimental.Policy('infer_float32_vars')
  model = tf.keras.models.Sequential(
      tf.keras.layers.Input((100,), dtype='float16'),
      tf.keras.layers.Dense(10, dtype=policy),
      tf.keras.layers.Dense(10, dtype=policy),
      tf.keras.layers.Lambda(lambda x: tf.cast(x, 'float32')),
      tf.keras.layers.Activation('Softmax')
  )
  ```

  Note that a LossScaleOptimizer should also be used for mixed precision models
  to avoid numerical underflow. See `LossScaleOptimizer`.
  """

  def __init__(self, name):
    self._name = name
    if name == 'infer':
      self._default_variable_dtype = None
    elif name == 'infer_float32_vars':
      self._default_variable_dtype = 'float32'
    else:
      raise ValueError('"name" argument to Policy constructor must be "infer" '
                       'or "infer_float32_vars", but got: %s' % name)

  @property
  def name(self):
    """Returns the name of the policy: "infer" or "infer_float32_vars."""
    return self._name

  @property
  def default_variable_dtype(self):
    """Returns the default variable dtype of this policy.

    This is the dtype layers will create their variables in, unless a layer
    explicit chooses a different dtype. Layers will cast variables to the
    appropriate dtype to avoid type errors.

    Returns:
      The default variable dtype of this policy, or None if the default variable
      dtype should be derived from the inputs.
    """
    return self._default_variable_dtype

  @property
  def should_cast_variables(self):
    """Returns true if variables should be casted."""
    return self.default_variable_dtype is not None

  # TODO(reedwm): Implement get_config/from_config.


# The policy in effect when TensorFlow starts. This is constant and never
# changes.
_default_policy = Policy('infer')

# The current global policy in effect. This starts as the default policy, but
# can be changed with `set_policy`.
# TODO(reedwm): Make this thread local?
_global_policy = _default_policy


@keras_export('keras.mixed_precision.experimental.global_policy')
def global_policy():
  """Returns the global Policy.

  The global policy is the default policy used for layers, if no policy is
  passed to the layer constructor. When TensorFlow starts, the global policy is
  set to an "infer" policy, and can be changed with `set_policy`.

  Returns:
    The global Policy.
  """
  return _global_policy


def _check_if_mixed_precision_graph_rewrite_is_enabled():
  if mixed_precision_global_state.mixed_precision_graph_rewrite_is_enabled:
    raise ValueError(
        'The mixed precision policy cannot be set, because the mixed '
        'precision graph rewrite has already been enabled.\n'
        'At most, one of the following functions can be called:\n\n'
        '  1. tf.train.experimental.enable_mixed_precision_graph_rewrite() '
        '(You called this first)\n'
        '  2. tf.keras.mixed_precision.experimental.set_policy() (You called '
        'this second)\n\n'
        'You called both functions, which is an error, because both functions '
        'enable you to use mixed precision. If in doubt which function to use, '
        'use the first, as it is currently more complete and easy to use. The '
        'first function enables mixed precision in the graph with a graph '
        'rewrite. However it is currently not very customizable, and does not '
        'support eager.')


@keras_export('keras.mixed_precision.experimental.set_policy')
def set_policy(policy):
  """Sets the global Policy."""
  global _global_policy
  _check_if_mixed_precision_graph_rewrite_is_enabled()
  if not isinstance(policy, Policy):
    policy = Policy(policy)
  _global_policy = policy
  mixed_precision_global_state.using_default_mixed_precision_policy = (
      _global_policy is _default_policy)


# TODO(reedwm): Make this thread local
@contextlib.contextmanager
def policy_scope(policy):
  old_policy = _global_policy
  try:
    set_policy(policy)
    yield
  finally:
    set_policy(old_policy)
