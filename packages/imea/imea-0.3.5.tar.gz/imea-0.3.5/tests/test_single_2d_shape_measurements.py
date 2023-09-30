import warnings


import numpy as np
import pytest
from skimage import draw

from imea import measure_2d


class Test2DGeodeticlengthThickness:
    def test_geodeticlength_and_thickness_zero(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            assert measure_2d.macro.geodeticlength_and_thickness(
                0.0, 0.0) == (0.0, 0.0)

            assert len(w) == 2
            assert issubclass(w[-1].category, UserWarning)
            assert "zero" in str(w[-1].message)

    def test_geodeticlength_and_thickness_square(self):
        a = 5.0
        area = a**2
        perimeter = 4*a
        assert measure_2d.macro.geodeticlength_and_thickness(
            area, perimeter) == (a, a)

    def test_geodeticlength_and_thickness_rectangle(self):
        a = 5.0
        b = 10.0
        area = a*b
        perimeter = 2*(a+b)
        assert measure_2d.macro.geodeticlength_and_thickness(
            area, perimeter) == (b, a)


class Test2DFractalDimension:
    def test_fractal_dimension_boxcounting_method_square(self):
        bw = np.zeros((100, 100), dtype='bool')
        bw[25:75, 25:75] = True
        true_fractal_dimension = 2.0
        approximated_fractal_dimension = measure_2d.micro.fractal_dimension_boxcounting(
            bw)
        assert np.allclose(approximated_fractal_dimension,
                           true_fractal_dimension, rtol=0.05)

    def test_fractal_dimension_boxcounting_method_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            bw = np.zeros((100, 100), dtype='bool')
            true_fractal_dimension = 0.0
            approximated_fractal_dimension = measure_2d.micro.fractal_dimension_boxcounting(
                bw)
            assert np.allclose(approximated_fractal_dimension,
                               true_fractal_dimension, rtol=0.05)

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)

    def test_fractal_dimension_perimeter_method_circle(self):
        radius = 50
        r, c = draw.circle_perimeter(2*radius, 2*radius, radius)
        contour = np.column_stack((r, c))
        max_feret = radius
        true_fractal_dimension = 1.0
        approximated_fractal_dimension = measure_2d.micro.fractal_dimension_perimeter(
            contour, max_feret)
        assert np.allclose(approximated_fractal_dimension,
                           true_fractal_dimension, rtol=0.05)

    def test_fractal_dimension_perimeter_method_line(self):
        r, c = draw.line(0, 0, 100, 0)
        contour = np.column_stack((r, c))
        max_feret = 10.0
        true_fractal_dimension = 1.0
        approximated_fractal_dimension = measure_2d.micro.fractal_dimension_perimeter(
            contour, max_feret)
        assert np.allclose(approximated_fractal_dimension,
                           true_fractal_dimension,
                           rtol=0.05)


class Test2DCircles:
    def test_area_equal_diameter_zero(self):
        assert measure_2d.macro.area_equal_diameter(0) == 0

    def test_area_equal_diameter_nonzero(self):
        true_diameter = 20.0
        projection_area = np.pi * (true_diameter/2)**2
        calculated_diameter = measure_2d.macro.area_equal_diameter(
            projection_area)
        assert np.allclose(calculated_diameter, true_diameter, rtol=0.01)

    def test_perimeter_equal_diameter_zero(self):
        assert measure_2d.macro.perimeter_equal_diameter(0) == 0

    def test_perimeter_equal_diameter_nonzero(self):
        true_diameter = 10.0
        perimeter = np.pi * true_diameter
        calculated_diameter = measure_2d.macro.perimeter_equal_diameter(
            perimeter)
        assert np.allclose(calculated_diameter, true_diameter, rtol=0.01)

    def test_max_inclosing_circle_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            bw = np.zeros((100, 100), dtype='bool')
            _, calculated_diameter = measure_2d.macro.max_inclosing_circle(bw)
            assert np.allclose(calculated_diameter, 0)

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_max_inclosing_circle_nonempty(self):
        bw = np.zeros((100, 100), dtype='bool')
        true_radius = 25
        rr, cc = draw.disk((50, 50), true_radius)
        bw[rr, cc] = True
        true_diameter = 2 * true_radius
        _, calculated_diameter = measure_2d.macro.max_inclosing_circle(bw)
        assert np.allclose(calculated_diameter, true_diameter)

    def test_min_enclosing_circle_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            bw = np.zeros((100, 100), dtype='bool')
            _, calculated_diameter = measure_2d.macro.max_inclosing_circle(bw)
            assert np.allclose(calculated_diameter, 0)

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_min_enclosing_circle_nonempty(self):
        bw = np.zeros((100, 100), dtype='bool')
        true_radius = 25
        rr, cc = draw.disk((50, 50), true_radius)
        bw[rr, cc] = True
        true_diameter = 2 * true_radius
        _, calculated_calculated_diameter = measure_2d.macro.max_inclosing_circle(
            bw)
        assert np.allclose(calculated_calculated_diameter, true_diameter)

    def test_circumscribing_and_inscribing_circle(self):
        true_radius = 5000
        centroid = np.array([2*true_radius, 2*true_radius])
        r, c = draw.circle_perimeter(centroid[0], centroid[1], true_radius)
        contour = np.column_stack([r, c])
        true_diameter = 2 * true_radius
        calculated_diameter_circumscribing, calculated_diameter_inscribing \
            = measure_2d.macro.circumscribing_and_inscribing_circle(
                centroid, contour)

        # Circumscribing circle touches from outside
        true_diameter_circumscribing = true_diameter + 1
        # Circumscribing circle touches from inside
        true_diameter_inscribing = true_diameter - 1

        assert np.allclose(calculated_diameter_circumscribing,
                           true_diameter_circumscribing)
        assert np.allclose(calculated_diameter_inscribing,
                           true_diameter_inscribing)


class Test2DMaxDimensions:
    def test_max_2d_dimensions_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            x_max, y_max = measure_2d.macro.max_2d_dimensions(
                np.array([]), np.array([]))
            assert np.allclose([x_max, y_max], [0, 0])

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_max_2d_dimensions_nonempty(self):
        max_chords = np.array([0, 50, 0, 0, 0, 10, 0, 0])
        angles = np.arange(0, 180, 22.5)

        x_max, y_max = measure_2d.macro.max_2d_dimensions(
            max_chords, angles)
        assert np.allclose([x_max, y_max], [50, 10])


class Test2DStatisticalLength:

    def test_nassenstein_diameter_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            nassenstein_diameter, _ = measure_2d.statistical_length.nassenstein(
                np.zeros((50, 50), dtype='bool'))
            assert nassenstein_diameter == 0

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_nassenstein_diameter_nonempty(self):
        bw = np.zeros((50, 50), dtype='bool')
        bw[10:20, 10:20] = True
        nassenstein_diameter, _ = measure_2d.statistical_length.nassenstein(
            bw)
        assert nassenstein_diameter == 10

    def test_feret_diameter_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            feret_diameter, _ = measure_2d.statistical_length.feret(
                np.zeros((50, 50), dtype='bool'))
            assert feret_diameter == 0

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_feret_diameter_nonempty(self):
        bw = np.zeros((50, 50), dtype='bool')
        bw[10:20, 10:20] = True
        feret_diameter, _ = measure_2d.statistical_length.feret(bw)
        assert feret_diameter == 10

    def test_martin_diameter_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            martin_diameter, _ = measure_2d.statistical_length.martin(
                np.zeros((50, 50), dtype='bool'))
            assert martin_diameter == 0

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_martin_diameter_nonempty(self):
        bw = np.zeros((50, 50), dtype='bool')
        bw[10:20, 10:20] = True
        martin_diameter, _ = measure_2d.statistical_length.martin(bw)
        assert martin_diameter == 10

    def test_all_chords_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            all_chords, _ = measure_2d.statistical_length.find_all_chords(
                np.zeros((50, 50), dtype='bool'))
            assert len(all_chords) == 0

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_all_chords_nonempty(self):
        bw = np.zeros((50, 50), dtype='bool')
        bw[10:20, 10:20] = True

        all_chords, _ = measure_2d.statistical_length.find_all_chords(bw)
        assert np.allclose(all_chords, np.array([10]*10))

    def test_max_chord_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            max_chord, _ = measure_2d.statistical_length.find_max_chord(
                np.zeros((50, 50), dtype='bool'))
            assert max_chord == 0

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_max_chord_nonempty(self):
        bw = np.zeros((50, 50), dtype='bool')
        bw[10:20, 10:20] = True

        max_chord, _ = measure_2d.statistical_length.find_max_chord(bw)
        assert max_chord == 10


class Test2DStatisticalLengthDistribution:

    def test_statistical_lengths_distributions_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            feret_diameters, martin_diameters, nassenstein_diameters, max_chords,\
                all_chords, angles = measure_2d.statistical_length.compute_statistical_lengths(
                    np.zeros((50, 50), dtype='bool'))
            assert np.allclose(feret_diameters, np.zeros(20))
            assert np.allclose(martin_diameters, np.zeros(20))
            assert np.allclose(nassenstein_diameters, np.zeros(20))
            assert np.allclose(max_chords, np.zeros(20))
            assert np.allclose(all_chords, np.array([]))

            assert len(w) > 0
            assert issubclass(w[0].category, UserWarning)
            assert "empty" in str(w[0].message)

    def test_statistical_lengths_distributions_nonempty(self):
        bw = np.zeros((200, 200), dtype='bool')
        radius = 50
        diameter = 2 * radius
        rr, cc = draw.disk((100, 100), 50)
        bw[rr, cc] = True
        feret_diameters, martin_diameters, nassenstein_diameters, max_chords,\
            all_chords, angles = measure_2d.statistical_length.compute_statistical_lengths(
                bw)
        radii = np.repeat([diameter], len(angles))
        assert np.allclose(feret_diameters, radii, rtol=0.01)
        assert np.allclose(martin_diameters, radii, rtol=0.01)
        assert np.allclose(nassenstein_diameters, radii, rtol=0.01)
        assert np.allclose(max_chords, radii, rtol=0.01)

    def test_distribution_parameters_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            max_value, min_value, median_value, mean_value, mode,\
                std = measure_2d.statistical_length.distribution_parameters(
                    np.array([]))
            assert max_value is None

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_distribution_parameters_nonempty(self):
        max_value, min_value, median_value, mean_value, mode,\
            std = measure_2d.statistical_length.distribution_parameters(
                np.ones((100)))
        assert np.allclose([max_value, min_value, median_value,
                            mean_value, mode, std], [1, 1, 1, 1, 1, 0])


class Test2DContour:
    def test_find_contour_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            contour = measure_2d.utils.find_contour(
                np.zeros((50, 50), dtype='bool'))
            assert len(contour) == 0

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_find_contour_nonempty(self):
        bw = np.zeros((50, 50), dtype='bool')
        bw[10:20, 10:20] = True
        contour = measure_2d.utils.find_contour(bw)
        assert len(contour) == 36


class Test2DBoundingBox:

    def test_min_2d_bounding_box_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            length, width, center, cornerpoints = measure_2d.macro.min_2d_bounding_box(
                np.zeros((50, 50), dtype='bool'))
            assert length == 0
            assert width == 0
            assert np.allclose(center, np.zeros((2)))
            assert np.allclose(cornerpoints, np.zeros((4, 2)))

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_min_2d_bounding_box_nonempty(self):
        bw = np.zeros((50, 50), dtype='bool')
        bw[10:20, 10:20] = True

        length, width, center, cornerpoints = measure_2d.macro.min_2d_bounding_box(
            bw)
        assert np.allclose(length, 10)
        assert np.allclose(width, 10)
        assert np.allclose(center, np.array([15, 15]))
        assert np.allclose(cornerpoints, np.array(
            [[10, 10], [10, 20], [20, 20], [20, 10]]))

    def test_min_2d_bounding_box_rectangle(self):
        bw = np.zeros((50, 50), dtype='bool')
        bw[10:20, 10:40] = True

        length, width, _, _ = measure_2d.macro.min_2d_bounding_box(
            bw)
        assert np.allclose(width, 10)
        assert np.allclose(length, 30)

class Test2DSKimage:

    def testskimage_measurements_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            perimeter, area, area_filled, area_convex, major_axis_length,\
                minor_axis_length, centroid, coords, bw, \
                bw_convex = measure_2d.utils.skimage_measurements(
                    np.zeros((50, 50), dtype='bool'))

            assert np.allclose([perimeter, area, area_filled, area_convex, major_axis_length,
                                minor_axis_length], np.zeros(6))
            assert len(centroid) == 0
            assert len(coords) == 0

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def testskimage_measurements_nonempty(self):
        bw = np.zeros((50, 50), dtype='bool')
        bw[10:20, 10:20] = True

        perimeter, area_projection, area_filled, area_convex, major_axis_length,\
            minor_axis_length, centroid, coords, bw, \
            bw_convex = measure_2d.utils.skimage_measurements(bw)

        assert np.allclose(perimeter, 36)
        assert np.allclose(area_projection, 100)
        assert np.allclose(area_filled, 100)
        assert np.allclose(area_convex, 100)
        assert np.allclose(major_axis_length, 11.5, rtol=0.01)
        assert np.allclose(minor_axis_length, 11.5, rtol=0.01)
        assert np.allclose(centroid, np.array([14.5, 14.5]))
        assert len(coords) == 100
        assert np.allclose(bw.shape, np.array([10, 10]))
        assert np.allclose(bw_convex.shape, np.array([10, 10]))


class Test2DPerimeters:

    def test_convex_perimeter_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            convex_perimeter = measure_2d.macro.convex_perimeter(
                np.zeros((50, 50), dtype='bool'))
            assert convex_perimeter == 0

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "empty" in str(w[-1].message)

    def test_convex_perimeter_nonempty(self):
        bw_convex = np.zeros((50, 50), dtype='bool')
        bw_convex[10:20, 10:20] = True
        convex_perimeter = measure_2d.macro.convex_perimeter(bw_convex)
        assert np.allclose(convex_perimeter, 36)


class Test2DErosion:

    def test_erosions_till_erase_empty(self):
        n_erosions = measure_2d.meso.erosions_till_erase(
            np.zeros((50, 50), dtype='bool'))
        assert n_erosions == 0

    def test_erosions_till_erase_nonempty(self):
        bw = np.zeros((50, 50), dtype='bool')
        bw[10:20, 10:20] = True
        n_erosions = measure_2d.meso.erosions_till_erase(bw)
        assert n_erosions == 6

    def test_erosions_till_erase_complement_empty(self):
        n_erosions = measure_2d.meso.erosions_till_erase_complement(
            np.zeros((50, 50), dtype='bool'), np.zeros((50, 50), dtype='bool'))
        assert n_erosions == 0

    def test_erosions_till_erase_complement_nonempty(self):
        bw_convex = np.zeros((50, 50), dtype='bool')
        bw_convex[10:20, 10:20] = True
        bw = np.copy(bw_convex)
        bw[12:18, 14:20] = False
        n_erosions = measure_2d.meso.erosions_till_erase_complement(
            bw, bw_convex)
        assert n_erosions == 4
