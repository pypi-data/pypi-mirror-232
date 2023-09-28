import numpy as np

from numpy.random import choice

from scipy.stats import theilslopes
from scipy.signal import correlation_lags
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt

import compPy.util.config as config

import time

import more_itertools as mit
from itertools import product


def lagged_correlation(x, y):
    """
    Calculate lagged correlation.

    Parameters:
    x - 1d array
        time-series
    y - 1d array
        time-series
    """
    x_std = (x - x.mean()) / (x.std() * len(x))
    y_std = (y - y.mean()) / y.std()
    return np.correlate(y_std, x_std, mode='same')


def calc_gradient(x, y, weights=None):
    """
    OLS analytic solution for zero intercept (See Bevington & Robinson)
    Is weighted LS is weights set

    Parameters:
    x - x coordinates
    y - y coordinates
    weights - 1 sigma errors

    OUTPUT - best fit values for gradient
    """

    if weights is None:
        weights = np.ones(x.shape[0])

    s_xy = (x*y / weights**2).sum()
    s_xx = (x*x / weights**2).sum()
    s_x = (x / weights**2).sum()
    s_y = (y / weights**2).sum()
    s_w = (1. / weights**2).sum()

    return np.array((0, (s_w*s_xy - s_x*s_y)/(s_w*s_xx - s_x**2)))


def parabola(x, y):
    """
    Analytic minimum position of parabola given 3 data points.

    Parameters:
    x - 1d array
        3 x values for parabola
    y - 1d array
        3 y values for parabola
    """
    return x[2] - (y[2] - y[1]) / (y[2] - 2 * y[1] + y[0]) - 0.5


def gauss_mod(x, a, b, tg, c):
    return a * np.exp(-b * (x - tg)**2) + c


def parabola_func(x, a, b, c):
    return a * x**2 + b * x + c


def track_cross_corr(vel_xt, track_cen, row_vals,
                     debug=True, window_duration=29,
                     row_skip=1, overlap=0, fit_func='3_point'):
    """
    Cross-correlate row to neighbouring row in time-distance map.

    Rows correspond to a height. For two heights at a separation of
    row_skip, and using a windowed period of duration window_duration,
    the lagged cross-correlation is calculated. The windows can
    overlap by an amount specified by overlap.

    For each cross-correlation, a parabola is fit to the peak to find
    the location of max value of CC values.

    Parameters:
    vel_xt - 2d array
             velocity time-distance
    track_cen - int
                value of track centre
    row_vals - 1d array
               integer array of row values
    window_duration - int
                      number of frames used in cross-correlation
    row_skip - determines distance between rows

    overlap - float
              degree of overlap of windows, range is [0, 1)

    fit_func - str
               which functional form to use for fitting parabola

    Outputs:
    cross_cor_loc - shape depends on window size + over lap. (N, 2)
            lag values corresponding to peak of cross-correlation values and
            row index
    cross_cor_val - value of cross-correlation at peak
    """
    allowed_func_calls = ['3_point', '5_point', 'gauss']

    if fit_func not in allowed_func_calls:
        raise ValueError("Fit function name unknown.")

    nt, nx = vel_xt.shape

    win_half = window_duration // 2
    lag_half = 10 if 10 < win_half else win_half

    lag = np.arange(-lag_half, lag_half + 1)
    number_lag_vals = len(lag)

    overlap_step = int(window_duration * overlap)
    overlap_step = window_duration if overlap == 0 else overlap_step
    time_iter = mit.windowed(range(nt),
                             window_duration,
                             step=overlap_step)

    if row_skip > 1:
        row_vals = row_vals[:-(row_skip - 1)]

    cross_corr_loc = []
    cross_corr_val = []

    for i, t1 in product(row_vals, time_iter):

        if not (None in t1):
            ser1 = vel_xt[t1, track_cen].copy()
            ser1 -= ser1.mean()
            ser2 = vel_xt[t1, i + row_skip].copy()
            ser2 -= ser2.mean()

            cc_vals = lagged_correlation(ser1, ser2)
            lags = correlation_lags(ser1.shape[0], ser2.shape[0], mode='same')
            mn_ind = np.where(lags == lag[0])[0][0]
            mx_ind = np.where(lags == lag[-1])[0][0]

            # only interested in lag values close middle
            cc_vals_trim = cc_vals[mn_ind:mx_ind].copy()
            max_lag = min(max(1, np.argmax(cc_vals_trim)),
                          number_lag_vals - 2)

            # Maybe should interpolate this value to sub-pixel max
            cross_corr_val.append(cc_vals_trim.max())

            if fit_func == '3_point':
                x_lags = lag[max_lag - 1:max_lag + 2]
                y_cc_vals = 1 - cc_vals_trim[max_lag - 1:max_lag + 2]

                if y_cc_vals.shape[0] > 2:
                    cross_corr_loc.append([parabola(x_lags, y_cc_vals), i])

            if fit_func == 'gauss':
                x_lags = lag[max_lag - 2:max_lag + 3]
                y_cc_vals = cc_vals_trim[max_lag - 2:max_lag + 3]
                if y_cc_vals.shape[0] > 4:

                    guess = [1, 1, 0, -0.5]
                    popt, pcov = curve_fit(gauss_mod,
                                           x_lags,
                                           y_cc_vals,
                                           sigma=np.ones(x_lags.shape[0]),
                                           p0=guess)
                    cross_corr_loc.append([popt[2],i])

            if fit_func == '5_point':
                x_lags = lag[max_lag - 2:max_lag + 3]
                y_cc_vals = cc_vals_trim[max_lag - 2:max_lag + 3]
                if y_cc_vals.shape[0] > 4:
                    guess = [-1, 0.02, 0]
                    popt2, pcov2 = curve_fit(parabola_func,
                                             x_lags,
                                             y_cc_vals,
                                             sigma=np.ones(x_lags.shape[0]),
                                             p0=guess)
                    cross_corr_loc.append([-popt2[1] / 2 / popt2[0], i])

    return np.array(cross_corr_loc), np.array(cross_corr_val)


def calc_prop_speed(slope, std_err, sampling, cadence):
    """
    Calculate the propagation speed.

    Use the estimated slope as phase speed of wave.
    """
    fac = sampling / cadence
    phase_speed = 1 / slope * fac
    speed_error = std_err / slope**2 * fac

    return phase_speed, speed_error


def theil_estim_slopes(lag_estimates, wind_dur, lag_half, ret, bootstrap=False):

    """
    Calculates the slopes based on Theil estimator.

    """
    if bootstrap:
        res = bootstrap_slope(lag_estimates, wind_dur)

        slope = res[:, 0].mean()
        up_band = res[:, 3].mean()
        low_band = res[:, 2].mean()
        std_err = calc_std(slope, up_band, low_band, ret)

    else:
        res = theilslopes(lag_estimates[:, 0],
                          lag_estimates[:, 1] - (lag_half + 1),
                          alpha=config.alpha_ts)
        slope = res[0]
        up_band = res[3]
        low_band = res[2]
        std_err = calc_std(slope, up_band, low_band, ret)
    return slope, std_err


def bootstrap_slope(lag_est, wind_dur):
    """
    Bootstrap estimate for slope.

    Bootstraps the confidence intervals for the Theil
    slopes fit to lag values.

    Relevant parameters can be tweaked in config file.
    These are number of bootstrap samples (num_bs) and
    condfidence band size (alpha_ts)
    """
    num_bs = config.num_bs
    win_half = wind_dur // 2
    lag_half = 10 if 10 < win_half else win_half

    num_ind = lag_est.shape[0]
    index_vals = np.arange(num_ind)

    samples = [choice(index_vals,
                      size=num_ind,
                      replace=True) for i in range(num_bs)]

    res_x = []
    for sample in samples:
        res = theilslopes(lag_est[sample, 0],
                          lag_est[sample, 1] - (lag_half + 1),
                          alpha=config.alpha_ts
                          )
        res_x.append(res)

    return np.array(res_x)

def pearson(X, Y):
    """
    The pearson correlation coefficient between x and y
    """

    N = len(X)
    Tx = X.sum()
    Ty = Y.sum()
    
    x_sq = (X*X).sum()
    y_sq = (Y*Y).sum()

    return ((X*Y).sum()-Tx*Ty/N)/np.sqrt((x_sq-Tx*Tx/N)*(y_sq -Ty*Ty/N))


def fast_pearson(X, Y, weight=np.ones(1)):
    """
    Vectorised method for dropping individual points and calculating pearson.

    X - array
    Y - array
    weight - array
    
    Returns: 
        S_drop[i]: the pearson coefficient without the i_th point.
    """
    Tw = weight.sum()
    Tx = (X*weight).sum()
    Ty = (Y*weight).sum()

    s_xy = X*Y*weight
    s_xx = X*X*weight
    s_yy = Y*Y*weight

    T_xy_sq = Tx*Ty
    T_xx_sq = Tx*Tx
    T_yy_sq = Ty*Ty

    # sums with individual points removed
    s_xy_drop = s_xy.sum()-s_xy
    s_xx_drop = s_xx.sum()-s_xx
    s_yy_drop = s_yy.sum()-s_yy
    Tw_drop = Tw-weight

    # squares with individual points removed
    T_xy_sq_drop = T_xy_sq-X*Ty*weight-Y*Tx*weight+s_xy*weight
    T_xx_sq_drop = T_xx_sq-2*X*Tx*weight+s_xx*weight
    T_yy_sq_drop = T_yy_sq-2*Y*Ty*weight+s_yy*weight

    # Calculate pearson with dropped observations
    numera = s_xy_drop-T_xy_sq_drop/Tw_drop
    denom = (s_xx_drop-T_xx_sq_drop/Tw_drop) * (s_yy_drop-T_yy_sq_drop/Tw_drop)
    S_drop = numera/np.sqrt(denom)

    numera = s_xy.sum()-Tx*Ty/Tw
    denom = (s_xx.sum()-T_xx_sq/Tw) * (s_yy.sum()-T_yy_sq/Tw)
    S_all = numera/np.sqrt(denom)

    return S_all, S_drop


def full_win_slopes(lag_estimates, cc_vals, row_vals):
    """
    Compute the slope of CC values using Pearson rejection.
    
    Parameters
    -------------

    lag_estimates - np.array
    cc_vals - np.array
    row_vals - np.array

    Returns
    -------
    Value of slope

    """
         
    # remove points with too large lags
    
    lag_est_mod = lag_estimates.copy()
    cc_vals_mod = cc_vals.copy()
    row_vals_mod = row_vals.copy()
    
    flag = np.where(np.abs(lag_est_mod) < 5.0*np.median(np.abs(lag_est_mod)))[0]
    row_vals_mod = row_vals_mod[flag]
    lag_est_mod = lag_est_mod[flag]
    
    # weight
    weight_mod = (np.abs(cc_vals_mod[flag])-0.5)**2
  
    # Remove the point that affects the pearson coefficient
    # the most. Repeat till the coefficient reaches 0.95.
    s = pearson(row_vals_mod, lag_est_mod)
    number = 0
    while (np.abs(s) < 0.95) and len(row_vals_mod) > 6 and number < 100:
        s, s_list = fast_pearson(row_vals_mod, lag_est_mod, weight=weight_mod)
        s_max = np.max(np.abs(s_list))
        index = np.abs(s_list) != s_max
        row_vals_mod = row_vals_mod[index]
        lag_est_mod = lag_est_mod[index]
        weight_mod = weight_mod[index]
        number += 1
 
    # do the linear fit with weight.
    fit_vals = calc_gradient(row_vals_mod, lag_est_mod, weights=1./weight_mod)
  
    return fit_vals[1]

        
def calc_std(slope, up_band, lo_band, ret):
    """
    Calculate standard deviation from Theil Slopes.

    Theil slops provides 2 confidence intervals, low and high. This
    appears to be asymmetric, so here we just take the largest
    difference to define a single value for the slope error.
    """
    if ret:
        std = np.max([np.abs(lo_band) - np.abs(slope),
                      np.abs(slope) - np.abs(up_band)])

    else:
        std = np.max([up_band - slope, slope - lo_band])
    return std


def compute_speed(vel_xt, sampling, cadence, debug=False,
                  ret=False, walsh=False):
    """
    Compute wave speed from velocity time-distance diagram.

    Subroutine to compute phase speed by lagged cross-correlation (CC) between
    rows of the velocity time-distance diagram and determining lag value of CC
    maximum.

    Lag value is determined by fitting the peak of the CC function
    with a polynomial (default).

    Lag values are then fit with a linear function using robust estimator
    (Theil Slopes).

    Parameters
    -----------
    vel_xt - np.ndarray
             time-distance diagram
    sampling - float
               pixel size in physical units
    cadence - float
              cadence of observations
    ret - boolean
          set this if the computed speed is a retrograde speed.
    walsh - boolean
          set to use walsh method. Default is full window.
    """
    bootstrap = config.bootstrap

    # nt and track_len need to be ints
    nt, track_len = vel_xt.shape

    # deal with even length tracks
    if track_len % 2 == 0:
        track_len = track_len - 1
        vel_xt = vel_xt[:, :-1]
    track_cen = track_len // 2

    row_trim = config.row_trim

    row_vals = np.arange(row_trim, track_len - row_trim)
    row_vals = row_vals.astype(int)

    if walsh:
        wind_dur = config.win_dur
        overlap = config.overlap
        win_half = wind_dur // 2
    else:
        wind_dur = nt
        overlap = 0
        win_half = wind_dur // 2

    # sets the number of lag values to used for
    # localisation of max peak. Not expecting peak to
    # be \pm 10*cadence from 0 lag.
    lag_half = 10 if 10 < win_half else win_half

    lag_estimates, cc_vals = track_cross_corr(vel_xt, track_cen, row_vals,
                                     window_duration=wind_dur, overlap=overlap)

    # print('lag', lag_estimates.shape)
    # print('vel_xt', vel_xt.shape)
    # print(track_cen)
    # print(row_vals)
    if walsh:
        slope, std_err = theil_estim_slopes(lag_estimates, wind_dur, lag_half, 
                                            ret, bootstrap=bootstrap)
    else:
        slope = full_win_slopes(lag_estimates[:,0], cc_vals, row_vals)
        std_err = np.nan

    phase_speed, speed_error = calc_prop_speed(slope, std_err,
                                               sampling, cadence)

    if debug:
        plt.scatter(lag_estimates[:, 1] - (lag_half + 1),
                    lag_estimates[:, 0], alpha=0.5, label='CC vals')
        plt.plot(row_vals - (lag_half + 1),
                 res[0] * (row_vals - (lag_half + 1)), label='Robust slope')
        plt.legend()
        time.sleep(config.pause_time)

    return phase_speed, speed_error
