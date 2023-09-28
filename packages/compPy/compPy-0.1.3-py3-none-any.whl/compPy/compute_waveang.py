import numpy as np
from numpy.fft import rfftfreq

from itertools import product

import compPy.util.config as config
from compPy.util.util import print_progress_bar
from compPy.util.spectraldensity import spectral_density, smooth_spec_dens
from compPy.util.do_apod import do_apod
from compPy.util.filter_funcs import define_filter

from compPy.io.save_load import cp_load_cadence, cp_load_mask
from compPy.io.save_load import cp_save_angles, cp_save_coh, cp_save_mask

from scipy.fftpack import ifft
from scipy.optimize import minimize
from scipy.ndimage import gaussian_filter
from scipy.linalg import inv, det


try:
    from jax import jit, jacobian, hessian
    import jax.numpy as jnp
except ModuleNotFoundError:
    import numpy as jnp

from functools import partial

from typing import Callable


__all__ = ['compute_waveang']


def model(params: np.ndarray, xy_vals: np.ndarray):
    """
    2D Gaussian function.

    Amplitude is fixed as 1 and centred on (0,0).

    Parameters
    ----------
    params - np.ndarray
             sigma and rotation parameters of 2D Gaussian (3 values)
    xy_vals - np.ndarray
              2d array containing x and y coordinates
    """
    x, y = xy_vals

    A = 1.
    sigma_x, sigma_y = params[0:2]
    thet = params[2]
    mu_x = 0.0
    mu_y = 0.0

    a = jnp.cos(thet)**2 / 2. / sigma_x**2 + jnp.sin(thet)**2 / 2. / sigma_y**2
    b = -jnp.sin(2. * thet) / 4. / sigma_x**2 + \
        jnp.sin(2. * thet) / 4. / sigma_y**2
    c = jnp.cos(thet)**2 / 2. / sigma_y**2 + jnp.sin(thet)**2 / 2. / sigma_x**2

    return A * jnp.exp(- (a * (x - mu_x)**2 +
                          2. * b * (x - mu_x) * (y - mu_y) +
                          c * (y - mu_y)**2))


#@partial(jit, static_argnums=(1,))
def neg_loglike_mask(theta: jnp.ndarray, model: Callable, x: jnp.ndarray,
                     y: jnp.ndarray, mask: jnp.ndarray, reg_val: jnp.float32):
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
    mask - binary array
         - value to ignore are set to 0
    """
    sigma = theta[0]  # need to do something about this!
    N = mask.sum()
    mu = model(theta[1:], x)

    # this is Equation 4.6
    ll = -N / 2. * jnp.log(2 * jnp.pi * sigma**2) - \
        (1. / (2 * sigma**2)) * jnp.sum(mask * jnp.square(y - mu)) - \
        theta[1]**2 / 2 / reg_val**2 - \
        theta[2]**2 / 2 / reg_val**2

    return -1 * ll   # note - no factor of 2 here


def min_dist_fit(x: np.ndarray, y: np.ndarray, w: np.ndarray = np.ones(1)):
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
       weights or mask values

    Returns
    --------
    angle: float
           the angle (degrees) of the line
    error: float
           error on the angle (degrees)
    """
    if len(w) == 1:
        w = np.ones(len(x))

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
    if s_xy != 0 and sx_sq != sy_sq:
        n = w.sum()  # this won't work for weights
        sigma_xx = 0.5 * ((sy_sq - sx_sq)**2 + 4 * s_xy**2)**0.5 - \
                   0.5 * (sy_sq - sx_sq)
        sigma_u_sq = 0.5 * sy_sq + 0.5 * sx_sq -  \
                     0.5 * ((sy_sq - sx_sq)**2 + 4 * s_xy**2)**0.5
        s_vv = (n - 1) / (n - 2) * (1 + m**2) * sigma_u_sq
        var_m = (sigma_xx * s_vv + sigma_u_sq * s_vv - m**2 * sigma_u_sq**2) \
                / (n - 1) / sigma_xx**2

        error = 1 / (1 + m**2) * var_m**0.5  # error propagation
    else:
        error = 0.

    return ang, error


def _tile_and_transpose(x: np.ndarray):
    """Tile and transpose array."""
    coh_box_len = int(2 * config.coherence['BoxHalfLength'] + 1)
    return np.transpose(np.tile(x, (coh_box_len, coh_box_len, 1)), [2, 0, 1])


def _filter_and_fit(coh: np.ndarray, xbox: np.ndarray, ybox: np.ndarray,
                    jacobian_: Callable, hessian_: Callable,
                    get_errs: bool = False):
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
    coh_box_len = int(2 * config.coherence['BoxHalfLength'] + 1)
    reg_val = jnp.float32(10)

    coh = np.nan_to_num(coh, posinf=0, neginf=0)

    # get filtered indices - does a reasonable job of removing outliers
    ind_filt = gaussian_filter(coh, 2) <= (coh_limit - 0.05)

    coh_filt = coh.copy()
    coh_filt[ind_filt] = 0
    coh_rav = jnp.asarray(coh_filt.ravel())

    # indices about coherence limit
    ind = coh_rav > coh_limit
    xdata = np.vstack((xbox.ravel(),
                       ybox.ravel()))

    if ind.sum() > min_num_pix:

        (theta, _) = min_dist_fit((xbox.ravel())[ind],
                                  (ybox.ravel())[ind])

        # calculation is sensitive to guess value of sigma p0[0]
        p0 = jnp.array([0.1, 2, 2, theta], dtype='float32')

        mask = np.zeros((coh_box_len * coh_box_len), dtype='float32')
        mask[ind] = 1.
        mask = jnp.asarray(mask)

        res = minimize(neg_loglike_mask, p0, method='BFGS',
                       args=(model, xdata, coh_rav, mask, reg_val),
                       jac=jacobian_)
        param = res.x

        if get_errs:
            hess = hessian_(param, model, xdata, coh_rav, mask)

            # Alternative method for calculation of covariance matrix
            # jac = jacobian_(param, model, xdata, coh_rav, mask)
            # U, s, Vh = linalg.svd(jac, full_matrices=False)
            # tol = np.finfo(float).eps*s[0]*max(jac.shape)
            # w = s > tol
            # cov = (Vh[w].T/s[w]**2) @ Vh[w]  # robust covariance matrix
            # perr = np.sqrt(np.diag(cov))

            # This is checking is needed if the global min is not found,
            # i.e. hessian has negative diagonal entry
            # Is there a way to ensure this?
            if np.isnan(hess).sum() == 0 and np.isinf(hess).sum() == 0:
                if det(hess) != 0 and (np.diag(hess) < 0).sum() == 0:
                    std_err = np.sqrt(np.diag(inv(hess)))
                else:
                    std_err = [0]
            else:
                std_err = [0]
        else:
            std_err = [0]
    else:
        param = [0, 0, 0, 0]
        std_err = [0]

    return param, std_err


def _filter_and_fit_reduced(coh: np.ndarray, xbox: np.ndarray,
                            ybox: np.ndarray):
    """
    Use of orthogonal regression to find angle.

    Filter data to suppress outliers then fits coherence island using
    orthogonal regression. Much quicker than full method.

    Parameters
    ----------
    coh - ndarray
          2D array of coherence values
    xbox, ybox - ndarray
                 2d array of x & y values containing coordinates values

    Returns
    Angle and error on angle in degrees
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

    if ind.sum() > min_num_pix:

        (angle, err) = min_dist_fit((xbox.ravel())[ind],
                                    (ybox.ravel())[ind])
    else:
        angle = 0
        err = 0

    return angle, err


def _correct_angle(param: np.ndarray):
    """
    Correct MLE estimate for angle to standard polar coordinate definition.

    Bring all values between -pi/2 and pi/2
    """
    # bring range between -2pi and 2 pi
    ang_temp = param[-1] + 1e-7  # adding 1e-7 suppresses numerical errors
    ang_temp = ang_temp % (np.sign(ang_temp) * 2 * np.pi)

    # bring between -pi/2 and pi/2
    if np.abs(param[2]) > np.abs(param[1]):
        ang_temp = ang_temp - np.pi / 2

    if np.abs(ang_temp) > np.pi:
        angle_rad = ang_temp - np.sign(ang_temp) * np.pi
    else:
        angle_rad = ang_temp

    if np.abs(angle_rad) < np.pi / 2:
        angle_rad *= -1
    else:
        angle_rad = np.sign(angle_rad) * np.pi - angle_rad

    return angle_rad


def mask_update(mask: np.ndarray, angles: np.ndarray):
    """
    Update mask based on wave angle result.

    If no neighbouring coherent pixels, then wave angle is
    set to 0. This probably indicates low or no signal in pixels.
    The mask file is updated to reflect this information.

    Parameters:
    mask - ndarray
           old mask
    angles - ndarray
             wave angle measurements

    Returns
    Updated mask
    """
    mask[angles[0] == 0] = 0

    return mask


def compute_waveang(cube_v: np.ndarray, date: str, full_mode: bool = False,
                    name_addon: str = '', update_mask: bool = False, 
                    **kwargs):
    """
    Compute the wave angle from Doppler velocity cubes.

    Parameters
    -----------
    cube_v: np.ndarray
            Doppler velocity cube

    date: str
          date of observations

    full_mode: boolean
               Default calculates wave angles using perpendicular offsets 
               method. Setting to True uses 2D Gaussian fitting method. This
               takes much longer but returns the coherence as well.

    name_addon: str
                additional string to add to saved files.

    update_mask: bool
                 Updates mask based on wave angle measurements.

    Returns
    ---------
    wave_angle: np.ndarray
                Wave angle values

    """

    if full_mode:
        try:
            import jax.numpy as jnp
        except ModuleNotFoundError:
            raise ModuleNotFoundError('Jax not installed. Cannot use full mode.')


    nt, ny, nx = cube_v.shape
    cadence = cp_load_cadence(date)

    coh_box_len = int(2 * config.coherence['BoxHalfLength'] + 1)
    coh_smooth = int(config.coherence['smoothing'])
    coh_half_box_len = int(config.coherence['BoxHalfLength'])

    mask = cp_load_mask(date)

    wave_angle = np.zeros([2, ny, nx])
    coh_measure = np.zeros([2, ny, nx])
    noise_estimate = np.zeros([ny, nx])

    # coordinates of points in box
    x = np.arange(0, coh_box_len) - coh_half_box_len
    xbox, ybox = np.meshgrid(x, x)

    nspec = len(rfftfreq(nt))  # just required for length
    freq_filter = define_filter(nt, cadence)
    freq_filter = _tile_and_transpose(freq_filter)

    apod_window = do_apod(nt)
    apod_window.create_apod_window()
    apod_window_cube = apod_window.add_dims((ny, nx))
    apod_window_cube = np.transpose(apod_window_cube, (2, 0, 1))

    mean_sub_cube_v = cube_v - np.mean(cube_v, axis=0)
    spec = (ifft(mean_sub_cube_v * apod_window_cube, axis=0))[0:nspec, :, :]

    auto_SD_smooth = smooth_spec_dens(spectral_density(spec),
                                      smoothing=coh_smooth)

    # define Jacobian & hessian for use in parameter estimation
    if full_mode:
        jacobian_ = jit(jacobian(neg_loglike_mask), static_argnums=(1,))
        hessian_ = jit(hessian(neg_loglike_mask), static_argnums=(1,))

    print("Starting processing....")

    rms_spec = np.sum(np.abs(spec), axis=0)

    for iy, ix in product(np.arange(ny), np.arange(nx)):
        if (mask[iy, ix] == 1) and (rms_spec[iy, ix] > 1e-7):

            # box locations
            # at the moment doesn't need to account for edge cases
            # may need to change for uCoMP data
            ly = iy - coh_half_box_len
            uy = iy + coh_half_box_len
            lx = ix - coh_half_box_len
            ux = ix + coh_half_box_len

            if (ux >= nx) or (uy >= ny):
                continue 

            spec1 = spec[:, iy, ix]
            g1 = auto_SD_smooth[:, iy, ix]

            spec_1 = _tile_and_transpose(spec1)
            g1 = _tile_and_transpose(g1)

            spec2c = spec[:, ly:uy + 1, lx:ux + 1]

            cross_SD = spectral_density(spec_1, spectrum2=spec2c)
            cross_SD_smooth = smooth_spec_dens(cross_SD, smoothing=coh_smooth)
            g2 = auto_SD_smooth[:, ly:uy + 1, lx:ux + 1]

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
            if full_mode:
                param, std_err = _filter_and_fit(coh, xbox, ybox,
                                                 jacobian_, hessian_,
                                                 **kwargs)
                angle_rad = _correct_angle(param)
                wave_angle[:, iy, ix] = np.rad2deg([angle_rad, std_err[-1]])
                coh_measure[:, iy, ix] = [param[1], param[2]]
                noise_estimate[iy, ix] = param[0]
            else:
                vals = _filter_and_fit_reduced(coh, xbox, ybox)
                wave_angle[:, iy, ix] = np.rad2deg(vals)

            # ================================================================
            #  find angle of coherence island if enough good points
            # ================================================================
            # if ncoh > min_number_coherent_pixels:
            #     (theta, error) = min_dist_fit((xbox.ravel())[good_pixels],
            #                                   (ybox.ravel())[good_pixels],
            #                                   (coh.ravel())[good_pixels])
            #     wave_angle[0, iy, ix] = theta
            #     wave_angle[1, iy, ix] = error

            print_progress_bar(ix + nx * iy, nx * ny, prefix='',
                               suffix='Complete', length=30)
    if update_mask:
        mask = mask_update(mask, wave_angle)
        _ = cp_save_mask(mask, date, name_addon=name_addon)

    _ = cp_save_angles(date, wave_angle, name_addon=name_addon)
    _ = cp_save_coh(date, coh_measure, name_addon=name_addon)

    return wave_angle, coh_measure, noise_estimate
