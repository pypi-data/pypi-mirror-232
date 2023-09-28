import numpy as np

from itertools import product

import compPy.util.config as config
from compPy.util.util import print_progress_bar
from compPy.spectraldensity import spectral_density, smooth_spec_dens
from compPy.do_apod import do_apod
from compPy.io.save_load import cp_save_angles, cp_load_cadence, cp_load_mask

from scipy.fftpack import ifft
# from scipy.optimize import minimize
from scipy.ndimage import gaussian_filter
# from scipy.linalg import inv, det

from jax import jit, jacobian, hessian, vmap
import jax.numpy as jnp
from jax.numpy import sin, cos
from jax.scipy.optimize import minimize
from jax.scipy.linalg import inv, det

from functools import partial

import pdb

__all__ = ['compute_waveang']


def model(params: np.ndarray, M: np.ndarray):
    """
    2D Gaussian function.

    Amplitude is fixed as 1 and centred on (0,0).

    Parameters
    ----------
    params - np.ndarray
             sigma and rotation parameters of 2D Gaussian (3 values)
    M - np.ndarray
        2d array containing x and y coordinates
    """
    x, y = M

    A = 1.
    sigma_x, sigma_y = params[0:2]
    thet = params[2]
    mu_x = 0.0
    mu_y = 0.0

    a = cos(thet)**2 / 2. / sigma_x**2 + sin(thet)**2 / 2. / sigma_y**2
    b = -sin(2. * thet) / 4. / sigma_x**2 + sin(2. * thet) / 4. / sigma_y**2
    c = cos(thet)**2 / 2. / sigma_y**2 + sin(thet)**2 / 2. / sigma_x**2

    return A * jnp.exp(- (a * (x - mu_x)**2 +
                          2. * b * (x - mu_x) * (y - mu_y) +
                          c * (y - mu_y)**2))


@partial(jit, static_argnums=(1,))
def neg_loglike_mask(theta: np.ndarray, model: callable, x: np.ndarray,
                     y: np.ndarray, mask: np.ndarray):
    """
    Return Gaussian negative log-likelihood for unknown sigma.

    Parameters
    ----------
    theta - model parameters, theta[0] should always be the estimate for sigma
    x - 1d array
        x values of data
    y - 1d array
        y values of data
    model - function
            model to fit to the data
    mask - boolean array
         - value to ignore are set to False
    """
    sigma = theta[0]  # need to do something about this!
    N = jnp.sum(mask)
    mu = model(theta[1:], x)

    # negative log-likelihood
    ll = -N / 2. * jnp.log(2 * jnp.pi * sigma**2) - \
        (1. / (2 * sigma**2)) * jnp.sum(mask * jnp.square(y - mu))

    return -1 * ll / N   # note - no factor of 2 here


@jit
def min_dist_fit(x: np.ndarray, y: np.ndarray, w: np.ndarray):
    """
     Analytical solution to the minimum distance problem.

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
           the angle (radians) of the line
    error: float
           error on the angle (radians)

    Notes:
    Unsure about wave angle error calculation - seems dubious. Should probably
    use a bootstrap approach - although that is computationally more expensive.
    """
    #  compute sums
    sx_sq = jnp.sum(x**2 * w**2)
    sy_sq = jnp.sum(y**2 * w**2)
    s_xy = jnp.sum(x * y * w**2)

    def calc_slope(s_xy):
        # compute two possible choices for slope
        arg1 = (-sx_sq + sy_sq) / (2 * s_xy)
        arg2 = jnp.sqrt((sx_sq - sy_sq)**2 + 4 * s_xy**2) / (2 * s_xy)
        m1 = arg1 - arg2
        m2 = arg1 + arg2

        # find sum of distance squared for two slopes and choose slope
        # which minimizes sum of distance squared
        distsq1 = (m1**2 * sx_sq - 2 * m1 * s_xy + sy_sq) / (1 + m1**2)
        distsq2 = (m2**2 * sx_sq - 2 * m2 * s_xy + sy_sq) / (1 + m2**2)

        m = jnp.where(distsq1 <= distsq2, m1, m2)
        ang = jnp.arctan(m)
        return ang

    def alt_ang(sxy):
        return jnp.where(sx_sq >= sy_sq, 0, jnp.pi / 2)

    ang = jnp.where(s_xy != 0, calc_slope(s_xy), alt_ang(s_xy))

    #  find error

    # if s_xy != 0 or sx_sq != sy_sq:
    #     d_ang = np.deg2rad(2)     # 2 degree perturbation in radians
    #     ang_plus = ang + d_ang
    #     ang_minus = ang - d_ang

    #     m = np.tan(ang)
    #     mplus = np.tan(ang_plus)
    #     mminus = np.tan(ang_minus)

    #     d0 = (m**2*sx_sq - 2.*m*s_xy + sy_sq)/(1. + m**2)
    #     dplus = (mplus**2*sx_sq - 2.*mplus*s_xy + sy_sq)/(1. + mplus**2)
    #     dminus = (mminus**2*sx_sq - 2.*mminus*s_xy + sy_sq)/(1. + mminus**2)

    #     error = 1./(np.sqrt((dplus + dminus - 2.)/d_ang**2))

    # else:
    error = 0.

    return ang, error


def _define_filter(nt: int, nspec: int, cadence: int):
    """
    Define a near Gaussian frequency filter.

    Parameters
    -----------
    nt - int
         number of time-frames
    nspec - int
            number of frequency ordinates
    cadence - int
              cadence of observations

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

    freq = np.arange(nspec)/float(nspec*2)/cadence

    freq_filter = np.exp(-(freq-cent_freq)**2/width**2)
    freq_filter[0] = 0.                      # set DC to zero
    freq_filter[(freq < 0.001).nonzero()] = 0.   # set low frequencies to zero
    freq_filter = freq_filter/np.sum(freq_filter)

    return freq_filter


def _tile_and_transpose(x: np.ndarray):
    """Tile and transpose array."""
    coh_box_len = int(2*config.coherence['BoxHalfLength'] + 1)
    return np.transpose(np.tile(x, (coh_box_len, coh_box_len, 1)), [2, 0, 1])


def _filter(coh: np.ndarray, xbox: np.ndarray, ybox: np.ndarray):
    """
    Filter data then fit a 2D Gaussian.

    Filters data to suppress outliers then fits a 2D Gaussian
    to coherence islands.

    Parameters
    ----------
    coh - ndarray
          2D array of coherence values
    xbox, ybox - ndarray
                 2d array of x & y values containing coordinates values
    jacobian_ - callable function.
                Calculates the Jacobian of negative log-likelihood.
    hessian_ - callable function.
                Calculates the hessian of negative log-likelihood.

    """
    coh_limit = config.coherence['limit']
    min_num_pix = config.coherence['minNumberPixels']

    coh = jnp.nan_to_num(coh, posinf=0, neginf=0)

    # get filtered indices - does a reasonable job of removing outliers
    ind_filt = gaussian_filter(coh, 2) <= (coh_limit - 0.05)

    coh_filt = jnp.where(ind_filt, 0, coh)
    coh_rav = coh_filt.ravel()

    # indices about coherence limit
    ind = coh_rav > coh_limit

    if ind.sum() > min_num_pix:
        return coh_rav
    else:
        return [None]


@jit
def _fit_gauss2d(xdata, coh_rav, coh_limit):

    x, y = xdata
    mask = jnp.where(coh_rav > coh_limit, 1, 0)
    (theta, _) = min_dist_fit(x, y, mask)

    # calculation is sensitive to guess value of sigma p0[0]
    p0 = jnp.array([0.1, 2, 2, jnp.deg2rad(theta) - jnp.pi / 2])

    res = minimize(neg_loglike_mask, p0, method='BFGS',
                   args=(model, xdata, coh_rav, mask))
    param = res.x

    return param


# @jit
# def calc_stand_err(hess):
#     return jnp.sqrt(jnp.diag(inv(hess)))


# def get_uncertainties(hessian_, param, xdata, mask):

#     # Alternative method for calculation of covariance matrix
#     # jac = jacobian_(param, model, xdata, coh_rav, mask)
#     # U, s, Vh = linalg.svd(jac, full_matrices=False)
#     # tol = np.finfo(float).eps*s[0]*max(jac.shape)
#     # w = s > tol
#     # cov = (Vh[w].T/s[w]**2) @ Vh[w]  # robust covariance matrix
#     # perr = np.sqrt(np.diag(cov))

#     # This is checking is needed if the global min is not found,
#     # i.e. hessian has negative diagonal entry
#     # Is there a way to ensure this?
#     hess = hessian_v(param, model, xdata, coh_rav, mask)
#     if jnp.isnan(hess).sum() == 0 and jnp.isinf(hess).sum() == 0:
#         if det(hess) != 0 and (jnp.diag(hess) < 0).sum() == 0:
#             std_err = 
#         else:
#             std_err = [0]
#     else:
#         std_err = [0]
#     return std_err


def _filter_and_fit_reduced(coh, xbox, ybox):
    """
    Filter data to suppress outliers then use orthogonal regression to find angle.

    Parameters
    ----------
    coh - ndarray
          2D array of coherence values
    xbox, ybox - ndarray
                 2d array of x & y values containing coordinates values

    """
    coh_limit = config.coherence['limit']
    min_num_pix = config.coherence['minNumberPixels']

    coh = np.nan_to_num(coh, posinf=0, neginf=0)

    # get filtered indices - does a reasonable job of removing outliers
    ind_filt = gaussian_filter(coh, 2) <= (coh_limit - 0.05)

    coh_filt = coh.copy()
    coh_filt[ind_filt] = 0
    coh_rav = coh_filt.ravel()

    # indices about coherence limit
    ind = coh_rav > coh_limit
    # xdata = np.vstack((xbox.ravel(),
    #                  ybox.ravel()))

    if ind.sum() > min_num_pix:

        (angle_deg, err) = min_dist_fit((xbox.ravel())[ind],
                                        (ybox.ravel())[ind], 1)
    else:
        angle_deg = 0
        err = 0

    return angle_deg, err


def _correct_angle(param):
    """
    Correct MLE estimate for angle to standard polar coordinate definition.

    Bring all values between -pi/2 and pi/2
    """
    # bring range between -2pi and 2 pi
    ang_temp = param[-1] + 1e-7 # adding 1e-7 suppresses numerical errors
    ang_temp = ang_temp % (jnp.sign(ang_temp)*2*jnp.pi)

    # bring between -pi/2 and pi/2
    if jnp.abs(param[2]) > jnp.abs(param[1]):
        ang_temp = ang_temp-jnp.pi/2

    if jnp.abs(ang_temp) > jnp.pi:
        angle_rad = ang_temp-jnp.sign(ang_temp)*jnp.pi
    else:
        angle_rad = ang_temp

    if jnp.abs(angle_rad) < jnp.pi/2:
        angle_rad *= -1
    else:
        angle_rad = jnp.sign(angle_rad)*jnp.pi - angle_rad

    return angle_rad


def compute_waveang(cube_v, date, full_mode=False, **kwargs):
    """
    Computes the wave angle from Doppler velocity cubes

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

    coh_box_len = int(2*config.coherence['BoxHalfLength']+1)
    coh_smooth = int(config.coherence['smoothing'])
    coh_half_box_len = int(config.coherence['BoxHalfLength'])
    min_number_coherent_pixels = config.coherence['minNumberPixels']

    mask = cp_load_mask(date)

    wave_angle = np.zeros([2, ny, nx])
    coh_measure = np.zeros([2, ny, nx])
    noise_estimate = np.zeros([ny, nx])

    # coordinates of points in box
    x = jnp.arange(0, coh_box_len) - coh_half_box_len
    xbox, ybox = jnp.meshgrid(x, x)
    xdata = jnp.vstack((xbox.ravel(),
                        ybox.ravel()))

    nspec = (nt - 1) // 2 + 1  # excludes nyquist
    freq_filter = _define_filter(nt, nspec, cadence)
    freq_filter = _tile_and_transpose(freq_filter)

    apod_window = do_apod(nt)
    apod_window.create_apod_window()
    apod_window_cube = apod_window.add_dims((ny, nx))
    apod_window_cube = np.transpose(apod_window_cube, (2, 0, 1))

    mean_sub_cube_v = cube_v-np.mean(cube_v, axis=0)
    spec = (ifft(mean_sub_cube_v*apod_window_cube, axis=0))[0:nspec, :, :]

    auto_SD_smooth = smooth_spec_dens(spectral_density(spec),
                                      smoothing=coh_smooth)

    # define Jacobian & hessian for use in parameter estimation
    if full_mode:
        jacobian_ = jit(jacobian(neg_loglike_mask), static_argnums=(1,))
        hessian_ = jit(hessian(neg_loglike_mask), static_argnums=(1,))
    
    print("Starting processing....")

    rms_spec = np.sum(np.abs(spec), axis=0)

    coh_rav_l = []  # store coherence data
    coh_locs = []

    for iy, ix in product(np.arange(ny), np.arange(nx)):
        if (mask[iy, ix] == 1) and (rms_spec[iy, ix] > 1e-7):
            # box locations
            # at the moment doesn't need to account for edge cases
            # may need to change for uCoMP data
            ly = iy - coh_half_box_len
            uy = iy + coh_half_box_len
            lx = ix - coh_half_box_len
            ux = ix + coh_half_box_len

            spec1 = spec[:, iy, ix]
            g1 = auto_SD_smooth[:, iy, ix]

            spec_1 = _tile_and_transpose(spec1)
            g1 = _tile_and_transpose(g1)

            spec2c = spec[:, ly:uy+1, lx:ux+1]

            cross_SD = spectral_density(spec_1, spectrum2=spec2c)
            cross_SD_smooth = smooth_spec_dens(cross_SD, smoothing=coh_smooth)
            g2 = auto_SD_smooth[:, ly:uy+1, lx:ux+1]

            # this is to supress error messages from sqrt
            # Need to check impact of this
            g1[g1 < 1e-7] = 1e-7
            g2[g2 < 1e-7] = 1e-7
            # Don't do calculation with DC component -
            # it is zero and leads to maths errors
            # see McIntosh et al. 2008. Sol. Phys.
            coh = (freq_filter[1:] *
                   (np.abs(cross_SD_smooth[1:]) /
                    np.sqrt(g1[1:] * g2[1:])
                    )
                   ).sum(axis=0)

            coh = jnp.asarray(coh)
            if full_mode:
                res = _filter(coh, xbox, ybox)
                if res[0] is not None:
                    coh_rav_l.append(res)
                    coh_locs.append([iy, ix])
            else:
                wave_angle[:, iy, ix] = _filter_and_fit_reduced(coh, xbox, ybox)

            # ================================================================
            #  find angle of coherence island if enough good points
            # ================================================================
            # if ncoh > min_number_coherent_pixels:
            #     (theta, error) = min_dist_fit((xbox.ravel())[good_pixels],
            #                                   (ybox.ravel())[good_pixels],
            #                                   (coh.ravel())[good_pixels])
            #     wave_angle[0, iy, ix] = theta
            #     wave_angle[1, iy, ix] = error

            print_progress_bar(ix+nx*iy, nx*ny, prefix='',
                               suffix='Complete', length=30)
    # using vmap to fit data
    if full_mode:
        vfit = jit(vmap(_fit_gauss2d, in_axes=(None, 0, None)))
        coh_rav_l = jnp.asarray(coh_rav_l)

        coh_limit = jnp.float32(config.coherence['limit'])

        param = vfit(xdata, coh_rav_l[0:5000], coh_limit)

        angle_rad = []
        for p in param:
            angle_rad.append(_correct_angle(p))

        for i, crds in enumerate(coh_locs):
            wave_angle[:, crds[0], crds[1]] = np.rad2deg([angle_rad[i], 0])  # std_err[i, -1]])
            coh_measure[:, crds[0], crds[1]] = [param[i, 1], param[i, 2]]
            noise_estimate[crds[0], crds[1]] = param[i, 0]
    _ = cp_save_angles(date, wave_angle)

    return wave_angle, coh_measure, noise_estimate
