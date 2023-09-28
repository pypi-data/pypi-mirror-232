import numpy as np

from itertools import product

import compPy.util.config as config
from compPy.util.util import print_progress_bar
from compPy.spectraldensity import spectral_density, smooth_spec_dens
from compPy.do_apod import do_apod
from compPy.io.save_load import cp_save_angles, cp_load_cadence, cp_load_mask

from scipy.fftpack import ifft

import pdb

__all__ = ['compute_waveang']


def min_dist_fit(x: np.ndarray, y: np.ndarray, w: np.ndarray):
    """
     Analytical solution to the minimum distance problem

     Fits a line to a set of points under the constraint that
     1) the line goes through the point x=0, y=0, and
     2) the total perpendicular distance from the set of points to the
        line is minimized.

    Parameters
    ----------
    x: np.ndarray
       vector of x values
    y: np.ndarray
       vector of y values
    w: np.ndarray
       vector of weights

    Returns
    --------
    angle: float
           the angle (degrees) of the line
    error: float
           error on the angle (degrees)

    Notes:
    Unsure about wave angle error calculation - seems dubious. Should probably
    use a bootstrap approach - although that is computationally more expensive.
    """
    #  compute sums
    sx_sq = np.sum(x**2 * w**2)
    sy_sq = np.sum(y**2 * w**2)
    s_xy = np.sum(x * y * w**2)

    if s_xy != 0:
        # compute two possible choices for slope
        arg1 = (-sx_sq + sy_sq) / (2 * s_xy)
        arg2 = np.sqrt((sx_sq - sy_sq)**2 + 4 * s_xy**2) / (2 * s_xy)
        m1 = arg1 - arg2
        m2 = arg1 + arg2

        # find sum of distance squared for two slopes and choose slope
        # which minimizes sum of distance squared
        distsq1 = (m1**2 * sx_sq - 2 * m1 * s_xy + sy_sq) / (1 + m1**2)
        distsq2 = (m2**2 * sx_sq - 2 * m2 * s_xy + sy_sq) / (1 + m2**2)

        m = m1 if distsq1 <= distsq2 else m2
        ang = np.arctan(m)
    else:
        ang = 0 if sx_sq >= sy_sq else np.pi / 2

    #  find error

    if s_xy != 0 or sx_sq != sy_sq:
        d_ang = np.deg2rad(2)     # 2 degree perturbation in radians
        ang_plus = ang + d_ang
        ang_minus = ang - d_ang

        m = np.tan(ang)
        mplus = np.tan(ang_plus)
        mminus = np.tan(ang_minus)

        d0 = (m**2*sx_sq - 2.*m*s_xy + sy_sq)/(1. + m**2)
        dplus = (mplus**2*sx_sq - 2.*mplus*s_xy + sy_sq)/(1. + mplus**2)
        dminus = (mminus**2*sx_sq - 2.*mminus*s_xy + sy_sq)/(1. + mminus**2)

        error = 1./(np.sqrt((dplus + dminus - 2.)/d_ang**2))

    else:
        error = 0.

    ang = np.rad2deg(ang)   # convert to degrees
    error = np.rad2deg(error)

    # if finite(ang) and finite(error) and finite(slope) then status = 1

    return ang, error


def _define_filter(nt, nspec, cadence):
    """
    Define a near Gaussian frequency filter.

    Parameters
    -----------
    nt - int
         number of time-frames
    """
    # Set up filter
    cent_freq = config.filters['centralFrequency']
    width = config.filters['width']

    freq = np.arange(nspec)/float(nspec*2)/cadence

    freq_filter = np.exp(-(freq-cent_freq)**2/width**2)
    freq_filter[0] = 0.                      # set DC to zero
    freq_filter[(freq < 0.001).nonzero()] = 0.   # set low frequencies to zero
    freq_filter = freq_filter/np.sum(freq_filter)

    return freq_filter


def _get_next_pixels(coh_mask):

    coh_box_len = np.int(2*config.coherence['BoxHalfLength']+1)

    (tested_pixels,) = (coh_mask.ravel() == 1).nonzero()
    test_pixels = np.concatenate((tested_pixels-1, tested_pixels+1,
                                  tested_pixels+coh_box_len,
                                  tested_pixels-coh_box_len),
                                 axis=0)

    # test pixels adjacent to contiguous pixels
    (valid_pixels,) = np.where(test_pixels < (coh_box_len**2-1))
    test_pixels = test_pixels[valid_pixels]

    # identify new contiguous pixels
    new_mask = np.zeros((coh_box_len, coh_box_len))

    (new_mask.ravel())[test_pixels] = 1.
    new_mask = new_mask*(1.-np.clip(coh_mask, 0, 1))

    return (new_mask > 0.).nonzero()


def compute_waveang(cube_v, date):
    """
    Compute the wave angle from Doppler velocity cubes.

    Parameters
    -----------
    cube_v: np.ndarray
            Doppler velocity cube


    Returns
    ---------
    wave_angle: np.ndarray
                Wave angle values

    """
    nt, ny, nx = cube_v.shape
    cadence = cp_load_cadence(date)

    coh_box_len = np.int(2*config.coherence['BoxHalfLength']+1)
    coh_smooth = np.int(config.coherence['smoothing'])
    coh_half_box_len = np.int(config.coherence['BoxHalfLength'])
    min_number_coherent_pixels = config.coherence['minNumberPixels']
    coh_limit = config.coherence['limit']

    mask = cp_load_mask(date)

    wave_angle = np.zeros([2, ny, nx])
    coherence_measure = np.zeros([2, ny, nx])

    # coordinates of points in box
    xbox = np.broadcast_to(np.arange(0, coh_box_len)-coh_half_box_len,
                           (coh_box_len, coh_box_len)
                           )
    ybox = xbox.T

    nspec = (nt-1)//2+1  # excludes nyquist
    freq_filter = _define_filter(nt, nspec, cadence)

    apod_window = do_apod(nt)
    apod_window.create_apod_window()
    apod_window_cube = apod_window.add_dims((ny, nx))
    apod_window_cube = np.transpose(apod_window_cube, (2, 0, 1))

    mean_sub_cube_v = cube_v-np.mean(cube_v, axis=0)
    spec = (ifft(mean_sub_cube_v*apod_window_cube, axis=0))[0:nspec, :, :]

    # auto_SD_smooth = np.zeros((nspec, ny, nx))
    # auto_SD = SpectralDensity()
    # for ix, iy in product(np.arange(nx), np.arange(ny)):
    #     auto_SD_smooth[:, iy, ix] = auto_SD.spec_density(spec[:, iy, ix]).smooth(smoothing=coh_smooth)

    auto_SD_smooth = smooth_spec_dens(spectral_density(spec),
                                      smoothing=coh_smooth)

    print("Starting processing....")

    rms_spec = np.sum(np.abs(spec), axis=0)

    # cross_SD = SpectralDensity(auto=0)
    for iy, ix in product(np.arange(ny), np.arange(nx)):
        if (mask[iy, ix] == 1) and (rms_spec[iy, ix] > 1e-7):

            # initialize arrays to zero
            coh = np.zeros((coh_box_len, coh_box_len))
            coh_mask = np.zeros((coh_box_len, coh_box_len))

            coh[coh_half_box_len, coh_half_box_len] = 1.
            coh_mask[coh_half_box_len, coh_half_box_len] = 1.

            spec1 = spec[:, iy, ix]
            g1 = auto_SD_smooth[:, iy, ix]

            count = 1
            ncoh = 1
            while count > 0 and ncoh < 100:
                new_pixels = _get_next_pixels(coh_mask)

                count = 0

                for ic in np.arange(0, new_pixels[0].size):
                    icx = new_pixels[1][ic]
                    icy = new_pixels[0][ic]

                    ii = np.int(ix-coh_box_len//2+icx)
                    jj = np.int(iy-coh_box_len//2+icy)

                    # Exceptions here prevent out of bounds values and also
                    # performing correlation with pixels with no signal
                    if (ii < 0) or (ii > nx-1) or (jj < 0) or (jj > ny-1) \
                                or (rms_spec[jj, ii] == 0) \
                                or mask[jj, ii] == 0:
                        coh[icy, icx] = 0
                        # coh_mask[icy,icx]=2
                    else:
                        if coh[icy, icx] == 0:
                            spec2c = spec[:, jj, ii]
                            cross_spec_density = spectral_density(spec1, spectrum2=spec2c)
                            cross_spec_density = smooth_spec_dens(cross_spec_density, smoothing=coh_smooth)
                            g2 = auto_SD_smooth[:, jj, ii]

                            # Don't do calculation with DC component -
                            # it is zero and leads to maths errors
                            # see McIntosh et al. 2008. Sol. Phys.
                            coh[icy, icx] = (freq_filter[1:] *
                                             (np.abs(cross_spec_density[1:]) /
                                              np.sqrt(g1[1:] * g2[1:])
                                              )
                                             ).sum()

                            if coh[icy, icx] > coh_limit:
                                coh_mask[icy, icx] = 1.
                                count = count+1
                            # else:
                                # coh_mask[icy, icx]=2

                (good_pixels,) = (coh_mask.ravel() == 1).nonzero()
                ncoh = len(good_pixels)
            # ================================================================
            #  find angle of coherence island if enough good points
            # ================================================================
            if ncoh > min_number_coherent_pixels:
                (theta, error) = min_dist_fit((xbox.ravel())[good_pixels],
                                              (ybox.ravel())[good_pixels],
                                              (coh.ravel())[good_pixels])
                wave_angle[0, iy, ix] = theta
                wave_angle[1, iy, ix] = error

            print_progress_bar(ix+nx*iy, nx*ny, prefix='',
                               suffix='Complete', length=30)
    res = cp_save_angles(date, wave_angle)
    return wave_angle
