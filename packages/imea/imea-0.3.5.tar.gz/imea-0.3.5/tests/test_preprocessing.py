import warnings


import numpy as np
import pytest

from imea.tools import preprocess


class TestPreprocessing:
    def test_extract_and_preprocess_3d_imgs_empty(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            imgs_3d, bws = preprocess.extract_and_preprocess_3d_imgs(
                np.zeros((50, 50), dtype='float'), 1)
            assert len(imgs_3d) == 0
            assert len(bws) == 0

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "not contain" in str(w[-1].message)

    def test_extract_and_preprocess_3d_imgs_one_object(self):
        img_3d = np.zeros((50, 50), dtype='float')
        img_3d[10:20, 10:20] = 2.0

        imgs_3d, bws = preprocess.extract_and_preprocess_3d_imgs(img_3d, 1)

        assert len(imgs_3d) == 1
        assert len(bws) == 1

    def test_extract_and_preprocess_3d_imgs_multiple_objects(self):
        img_3d = np.zeros((50, 50), dtype='float')
        img_3d[10:20, 10:20] = 2.0
        img_3d[22:32, 10:20] = 3.0
        img_3d[34:44, 10:20] = 4.0

        imgs_3d, bws = preprocess.extract_and_preprocess_3d_imgs(img_3d, 1)

        # check number of objects
        assert len(imgs_3d) == 3
        assert len(bws) == 3

        # check cropping
        for img in imgs_3d:
            assert img.shape != img_3d.shape

        for (img, bw) in zip(imgs_3d, bws):
            assert img.shape == bw.shape

    def test_equalspace_3d_img_zero(self):
        img_empty = np.zeros((50, 50), dtype='float')
        img_3d_equalspace, spatial_resolution = preprocess.equalspace_3d_img(
            img_empty, 1, 1)

        assert np.allclose(img_3d_equalspace, img_empty)
        assert np.allclose(spatial_resolution, 1)

    def test_equalspace_3d_img_nonempty(self):
        dxys = [1, 2]
        dzs = [1, 2]

        for dxy in dxys:
            for dz in dzs:
                img = np.ones((50, 50), dtype='float')
                img_3d_equalspace, spatial_resolution = preprocess.equalspace_3d_img(
                    img, spatial_resolution_xy=dxy, spatial_resolution_z=dz)

                sum_true = np.sum(img.ravel()) * dxy**2 * dz
                sum_calculated = np.sum(
                    img_3d_equalspace.ravel()) * spatial_resolution**3

                assert img.shape == img_3d_equalspace.shape
                assert np.allclose(sum_true, sum_calculated)
                assert np.allclose(spatial_resolution, dxy)
