import compPy.io.in_out as io

import find_files as ff
import os

import pytest
import numpy as np


def test_cadence():
    """
    Test length of cadence list returned
    """
    inpath = '/../data'
    file_names = '*.fts.gz'
    file_list = ff.find_files(file_names, inpath)

    cadence_list = io._compute_cadence(file_list)

    assert len(cadence_list) == len(file_list)-1


def test_start_end_one_large_gap():
    """
    Test it finds the large cadence
    """
    norm_cadence = 10
    interp_lim = 3
    cadence = np.array([1, 1, 1, 1, 7, 1, 1, 1, 1])*norm_cadence
    cadence = cadence.tolist()
    start, end = io._define_start_end(cadence, norm_cadence, interp_lim)
    assert start == 0 and end == 4


def test_start_end_no_large_gaps():
    """
    Test it returns all of the 'files'
    """
    norm_cadence = 10
    interp_lim = 3
    cadence = np.array([1, 1, 1, 1, 2, 1, 1, 1, 1])*norm_cadence
    cadence = cadence.tolist()
    start, end = io._define_start_end(cadence, norm_cadence, interp_lim)
    assert start == 0 and end == 9


def test_start_end_large_gap_at_start():
    """
    Test for return files except first
    """
    norm_cadence = 10
    interp_lim = 3
    cadence = np.array([7, 1, 1, 1, 2, 1, 1, 1, 1])*norm_cadence
    cadence = cadence.tolist()
    start, end = io._define_start_end(cadence, norm_cadence, interp_lim)
    assert start == 1 and end == 9


def test_start_end_return_second_block():
    """
    Test for return of second block of files, i.e. the largest
    """
    norm_cadence = 10
    interp_lim = 3
    cadence = np.array([7, 1, 1, 7, 1, 1, 1, 1, 1])*norm_cadence
    cadence = cadence.tolist()
    start, end = io._define_start_end(cadence, norm_cadence, interp_lim)
    assert start == 4 and end == 9


def test_check_date_short():
    """
    Test for short date string
    """
    with pytest.raises(ValueError)as exc_info:
        io.initial_load_files('2')
    assert exc_info.match("date must be in form YYYYMMDD")


def test_check_date_not_string():
    """
    Test for date not given as string
    """
    with pytest.raises(TypeError)as exc_info:
        io.initial_load_files(20120327)
    assert exc_info.match('date must be a str')


def test_interpolate():
    """
    Basic test of interpolation. Tests whether it fills in correct
    values for a single gap.
    """

    gap_info = {'number_gaps': [1],
                'number_missing_frames': [1],
                'frames_to_skip': [1],
                'gap_start': [1], 'gap_size': [2]
                }
    nx = 10
    ny = 10
    cubes = np.arange(0, nx*ny*3).reshape(10, 10, 3)
    cubes = np.transpose(cubes, [2, 0, 1])

    expected = cubes[1, :, :].copy()
    cubes[1, :, :] = 0
    cubes_d = [cubes, cubes]  # have to pass in list of cubes

    result = io.interpolate_data(cubes_d, gap_info, nx, ny)

    assert np.alltrue(result[0][1, :, :] == expected)
