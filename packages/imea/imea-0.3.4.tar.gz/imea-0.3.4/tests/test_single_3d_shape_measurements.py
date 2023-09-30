import warnings

import numpy as np
import pytest
from scipy import spatial

from imea import measure_3d


class Test3DVolume:
    def test_volume_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            volume = measure_3d.macro.volume(
                np.zeros((50, 50), dtype='float'), 1)
            assert volume == 0

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_volume_nonempty(self):
        volume = measure_3d.macro.volume(np.ones((50, 50), dtype='float'), 1)
        assert np.allclose(volume, 50*50)

    def test_volume_convexhull(self):
        points = np.array([[0, 0, 0],
                           [0, 0, 1],
                           [0, 1, 0],
                           [0, 1, 1],
                           [1, 0, 0],
                           [1, 0, 1],
                           [1, 1, 0],
                           [1, 1, 1]],
                          dtype='float')
        ch = spatial.ConvexHull(points)

        volume_convexhull = measure_3d.macro.volume_convexhull(ch, 1)
        assert np.allclose(volume_convexhull, 1)

    def test_surfacearea_convexhull(self):
        points = np.array([[0, 0, 0],
                           [0, 0, 1],
                           [0, 1, 0],
                           [0, 1, 1],
                           [1, 0, 0],
                           [1, 0, 1],
                           [1, 1, 0],
                           [1, 1, 1]],
                          dtype='float')
        ch = spatial.ConvexHull(points)

        surfacearea = measure_3d.macro.surfacearea_convexhull(ch, 1)
        assert np.allclose(surfacearea, 6)

    class Test3DEquivalentDiameters:

        def test_surfacearea_equivalent_diameter_zero(self):
            assert measure_3d.macro.surfacearea_equivalent_diameter(0) == 0

        def test_surfacearea_equivalent_diameter_nonzero(self):
            true_diameter = 10
            calculated_diameter = measure_3d.macro.surfacearea_equivalent_diameter(
                np.pi * true_diameter**2)
            assert np.allclose(true_diameter, calculated_diameter)

        def test_volume_equivalent_diameter_zero(self):
            assert measure_3d.macro.volume_equivalent_diameter(0) == 0

        def test_volume_equivalent_diameter_nonzero(self):
            true_diameter = 10
            calculated_diameter = measure_3d.macro.volume_equivalent_diameter(
                4/3 * np.pi * (true_diameter/2)**3)
            assert np.allclose(true_diameter, calculated_diameter)


class Test3DConvexHull:

    def test_compute_convexhull(self):
        ch = measure_3d.utils.compute_convexhull(
            np.ones((50, 50), dtype='float'))
        assert ch.points.shape[1] == 3


class Test3DFeretMaxDimensions:

    def test_feret_and_max_dimensions_3d(self):
        points = np.array([[0, 0, 0],
                           [0, 0, 1],
                           [0, 1, 0],
                           [0, 1, 1],
                           [1, 0, 0],
                           [1, 0, 1],
                           [1, 1, 0],
                           [1, 1, 1]],
                          dtype='float') * 100
        ch = spatial.ConvexHull(points)
        feret_3d_max, feret_3d_min, x_max_3d, y_max_3d, z_max_3d\
            = measure_3d.macro.feret_and_max_dimensions_3d(ch, 1)
        assert np.allclose(feret_3d_max, np.sqrt(3) * 100, rtol=0.01)
        assert np.allclose(feret_3d_min, 100, rtol=0.01)
        assert np.allclose(x_max_3d, np.sqrt(3) * 100, rtol=0.01)
        assert np.allclose(y_max_3d, 144, rtol=0.01)
        assert np.allclose(z_max_3d, 131, rtol=0.01)


class Test3DBoundingBox:

    def test_min_3d_bounding_box_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            length, width, height = measure_3d.macro.min_3d_bounding_box(
                np.zeros((50, 50), dtype='float'), 1)
            assert length == 0
            assert width == 0
            assert height == 0

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_min_3d_bounding_box_nonempty(self):
        img = np.zeros((50, 50), dtype='float')
        img[10:20, 10:30] = 10
        length, width, height = measure_3d.macro.min_3d_bounding_box(img, 1)
        assert np.allclose([length, width, height], [20, 10, 10])
