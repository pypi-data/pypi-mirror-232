import warnings


import numpy as np
import pytest

import imea


class Test3DShapeMeasurements:
    def test_extract_shape_measurements_3d_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            shape_measurements_2d, shape_measurements_3d = imea.shape_measurements_3d(
                np.zeros((50, 50), dtype='float'), 1, 1, 1)
            assert len(shape_measurements_2d) == 0
            assert len(shape_measurements_3d) == 0

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "not contain" in str(w[-1].message)

    def test_extract_shape_measurements_3d_single_object(self):
        img = np.zeros((50, 50), dtype='float')
        img[10:20, 10:20] = 10.0
        shape_measurements_2d, shape_measurements_3d = imea.shape_measurements_3d(
            img, 1, 1, 1)
        assert len(shape_measurements_2d) == 1
        assert len(shape_measurements_3d) == 1

    def test_extract_shape_measurements_3d_multiple_objects(self):
        img = np.zeros((50, 50), dtype='float')
        img[10:20, 10:20] = 10.0
        img[22:32, 10:20] = 10.0
        img[34:44, 10:20] = 10.0
        shape_measurements_2d, shape_measurements_3d = imea.shape_measurements_3d(
            img, 1, 1, 1)
        assert len(shape_measurements_2d) == 3
        assert len(shape_measurements_3d) == 3
