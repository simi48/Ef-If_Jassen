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
"""TensorSpec factory for sparse tensors."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.framework import dtypes
from tensorflow.python.framework import sparse_tensor
from tensorflow.python.framework import tensor_shape
from tensorflow.python.framework import tensor_spec


def sparse_tensor_spec(shape=None,
                       dtype=dtypes.float32,
                       num_values=None,
                       name=None):
  """Returns a tensor specification for a SparseTensor.

  Returns an object which can be passed to `tf.function` (or other
  functions that expect `TensorSpec`s) to specify shape constraints
  for a `SparseTensor` argument.

  Args:
    shape: The shape of the SparseTensor, or `None` to allow any shape. The
      returned specification object depends only on `shape.ndims`.
    dtype: Data type of values in the SparseTensor.
    num_values: The number of values in the SparseTensor, or `None` to allow any
      number of values.
    name: Optional name prefix for the `TensorSpec`s.

  Returns:
    An object describing the `values`, `indices` and `dense_shape` tensors
    that comprise the `SparseTensor`.
  """
  dtype = dtypes.as_dtype(dtype)
  rank = tensor_shape.TensorShape(shape).rank
  indices = tensor_spec.TensorSpec([num_values, rank], dtypes.int64,
                                   ("%s.indices" % name) if name else None)
  values = tensor_spec.TensorSpec([num_values], dtype, name)
  dense_shape = tensor_spec.TensorSpec(
      [rank], dtypes.int64, ("%s.dense_shape" % name) if name else None)
  return sparse_tensor.SparseTensor(indices, values, dense_shape)
