# MIT License

# Copyright (c) 2017 thunderhoser

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy
from scipy.interpolate import interp1d

def _run_pmm_one_variable(
        input_matrix, max_percentile_level=100):
    """Applies PMM to one variable.
    E = number of examples (realizations over which to average)
    :param input_matrix: numpy array.  The first axis must have length E.  Other
        axes are assumed to be spatial dimensions.  Thus, input_matrix[i, ...]
        is the spatial field for the [i]th example.
    :param max_percentile_level: Maximum percentile.  No output value will
        exceed the [q]th percentile of `input_matrix`, where q =
        `max_percentile_level`.  Similarly, no output value will be less than
        the [100 - q]th percentile of `input_matrix`.
    :return: mean_field_matrix: numpy array of probability-matched means.  Will
        have the same dimensions as `input_matrix`, except without the first
        axis.  For example, if `input_matrix` is E x 32 x 32 x 12, this will be
        32 x 32 x 12.
    """

    # Pool values over all dimensions and remove extremes.
    pooled_values = numpy.ravel(input_matrix)
    pooled_values = numpy.sort(pooled_values)

    max_pooled_value = numpy.percentile(pooled_values, max_percentile_level)
    pooled_values = pooled_values[pooled_values <= max_pooled_value]

    min_pooled_value = numpy.percentile(
        pooled_values, 100 - max_percentile_level)
    pooled_values = pooled_values[pooled_values >= min_pooled_value]

    # Find ensemble mean at each grid point.
    mean_field_matrix = numpy.mean(input_matrix, axis=0)
    mean_field_flattened = numpy.ravel(mean_field_matrix)

    # At each grid point, replace ensemble mean with the same percentile from
    # pooled array.
    pooled_value_percentiles = numpy.linspace(
        0, 100, num=len(pooled_values), dtype=float)
    mean_value_percentiles = numpy.linspace(
        0, 100, num=len(mean_field_flattened), dtype=float)

    sort_indices = numpy.argsort(mean_field_flattened)
    unsort_indices = numpy.argsort(sort_indices)

    interp_object = interp1d(
        pooled_value_percentiles, pooled_values, kind='linear',
        bounds_error=True, assume_sorted=True)

    mean_field_flattened = interp_object(mean_value_percentiles)
    mean_field_flattened = mean_field_flattened[unsort_indices]
    mean_field_matrix = numpy.reshape(
        mean_field_flattened, mean_field_matrix.shape)

    return mean_field_matrix