import numpy as np
from numpy.fft import fftn, ifftn, rfftfreq

from compPy.io.save_load import cp_load_cadence

import compPy.util.config as config


def mean_sub(cube):
    """Remove temporal mean."""
    mean_sub_cube = cube - np.mean(cube, axis=0)
    return mean_sub_cube


def define_filter(nt: int, cadence: int, norm: bool = True):
    """
    Define a near Gaussian frequency filter.

    Parameters
    -----------
    nt - int
         number of time-frames
    cadence - int
              cadence of observations
    norm - bool
           whether to normalise filter or not

    Returns
    -------
    A filter that is applied to the frequency domain.

    Notes
    -----
    This is not a perfect Gaussian, so may result in
    ringing in temporal domain. Should remove suppression of low frequencies.
    """
    # Set up filter
    cent_freq = config.filters['centralFrequency']
    width = config.filters['width']

    freq = rfftfreq(nt, d=cadence)

    freq_filter = np.exp(-(freq - cent_freq)**2 / width**2)
    freq_filter[0] = 0.                      # set DC to zero
    freq_filter[(freq < 0.001).nonzero()] = 0.   # set low frequencies to zero
    if norm:
        freq_filter = freq_filter / np.sum(freq_filter)

    return freq_filter


def three_mhz_filt(cube: np.ndarray, date: str):
    """Filter data at 3mHz."""
    nt, ny, nx = cube.shape
    cadence = cp_load_cadence(date)

    freq_filter = define_filter(nt, cadence, norm=False)
    rev_freq_filter = freq_filter[::-1]
    freq_filter = np.concatenate((freq_filter[:-1], rev_freq_filter[:-1]))
    freq_filter = np.transpose(np.tile(freq_filter, (ny, nx, 1)), [2, 0, 1])

    cube_mn_sb = mean_sub(cube)
    ft_cube = fftn(cube_mn_sb)
    filt_ft = ft_cube * freq_filter
    filt_cube = ifftn(filt_ft)

    return filt_cube.real
