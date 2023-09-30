import warnings


import numpy as np
import pytest

import imea


class Test2DShapeMeasurements:
    def test_extract_shape_measurements_2d_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            shape_measurements = imea.shape_measurements_2d(
                np.zeros((50, 50), dtype='bool'))
            assert len(shape_measurements) == 0

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "not contain" in str(w[-1].message)

    def test_extract_shape_measurements_2d_single_object(self):
        bw = np.zeros((50, 50), dtype='bool')
        bw[10:20, 10:20] = True
        shape_measurements = imea.shape_measurements_2d(bw)
        assert len(shape_measurements) == 1

    def test_extract_shape_measurements_2d_multiple_objects(self):
        bw = np.zeros((50, 50), dtype='bool')
        bw[10:20, 10:20] = True
        bw[22:32, 10:20] = True
        bw[34:44, 10:20] = True
        shape_measurements = imea.shape_measurements_2d(bw)
        assert len(shape_measurements) == 3
