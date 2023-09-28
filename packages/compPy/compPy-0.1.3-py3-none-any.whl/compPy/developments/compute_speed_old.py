import numpy as np
from scipy.interpolate import splev, splrep
from scipy.stats import t, norm

import compPy.util.config as config

import pdb


__all__ = ['compute_speed']


#PURPOSE: Subroutine to compute phase speed by cross correlating rows of the velocity
#         space-time diagram (which is input). The time series used for cross correlation
#         is formed by collapsing all the rows of the diagram after shifting by an
#         estimate of the phase speed. This estimate is obtained using only the central
#         rows of the diagram.
#  INPUTS: vel - filtered time-distance velocity map. Either pro or retrograde.
#          sampling - pixel size in Mm
#          cadence - cadence of observations
#
#  KEYWORDS:   debug - obvious...
#
#              ret   - set this if the computed speed is a retrograde
#                      speed (for a better initial guess for the fit).
#
#              force_zero - force the fit to go through (0,0), i.e.
#                           through the reference pixel. By default, it
#                           it is turned off in the wave tracking code,
#                           because it gives higher errors even though
#                           the fit might still be good (i.e. same
#                           slope, but with an offset in x/y).
#
#CALLS: parabola.pro, mpfit.pro, mpfitfunc.pro, lin_func_fit.pro
#
#
#
#HISTORY: - Created by S Tomczyk
#         - Corrected in Feb 2013 by C. Bethge. More accurate phase speeds and
#           errors now.
#         - Added code to deal with even length tracks.
#           Added extra constraint for CC - max CC value has to be
#           above probability of that of random signals.
#           Corrected bugs in phase speed error calculation
#           Added new method for rejection of outliers
#           Added correction to t-factor for phase speed error to account for varying track lengths - R Morton 11/2014
#           Fixed bugs in errors for phase speed fitting -  R Morton 05/2015
#         - v0.3 (RJM 05/2019) Introducing versioning to keep track of code development. Given past major changes, 
#           the first numbered version is as version 0.3.


def lagged_correlation(x, y):
    """
    Calculates lagged correlation

    Parameters:
    x - 1d array
        time-series
    y - 1d array
        time-series
    """
    x_std = (x - x.mean()) / (x.std() * len(x))
    y_std = (y - y.mean()) / y.std()
    return np.correlate(y_std, x_std, mode='same') #/ x.std() / y.std()


def parabola(x, y):
    """
    Analytic minimum position of parabola given 3 data points
    Parameters:
    x - 1d array
        3 x values for parabola
    y - 1d array
        3 y values for parabola
    """
    return x[2] - (y[2]-y[1]) / (y[2] - 2*y[1] + y[0]) - 0.5


def track_cross_corr(vel_xt, track_cen, ranges, lag,
                     low_noise_series=None, debug=True):
    """
    Cross-correlate rows to central row in time-distance map
    Fit parabola to find the location of max value of CC values

    Parameters:
    vel_xt - 2d array
             velocity time-distance
    track_cen - int
                value of track centre
    lag - 1d array
          lag values
    low_noise_series - 1d array
                       a low_noise_series for cross-correlation
    Outputs:
    1d array
    locations of max of cross-correlation values
    """

    cross_corr_max = np.zeros(ranges)
    number_lag_vals = len(lag)
    nt_half = vel_xt.shape[0]//2

    vel_xt_cent = vel_xt[:, track_cen] if low_noise_series is None else low_noise_series

    half_range = ranges//2
    for i in range(-half_range, half_range+1):
        cross_corr_vals = lagged_correlation(vel_xt_cent, vel_xt[:, track_cen+i])
        # only interested in lag values close middle
        cross_corr_vals = cross_corr_vals[nt_half+lag]
        max_lag = min(max(1, np.argmax(cross_corr_vals)), number_lag_vals-2)
        x_lags = lag[max_lag-1:max_lag+2]
        y_cc_vals = 1 - cross_corr_vals[max_lag-1:max_lag+2]
        cross_corr_max[i+half_range] = parabola(x_lags, y_cc_vals)
        
        if debug:
            x = 1  # temporary till debug sorted - means nothing
            # oplot,lag,cross_corr_vals-range/4.+(i+range/2)*0.5, col=50

    return cross_corr_max


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


def calc_low_noise_series(lag_estimates, nt, track_len, vel_xt):
    """
    Calculate low noise series to replace central row of xt diagram

    INPUT lag_estimates - 1d array
                          initial estimates for lags between time-series
           nt - int
                number of elements in time-series
           track_len - int
                       length of track
           vel_xt - 2d array
                    velocity time-distance
      """
    gradient_estim = [0., np.median(np.gradient(lag_estimates))]

    time = np.tile(np.arange(nt), (track_len, 1)).T
    shifts = gradient_estim[1]*(np.arange(track_len)-track_len//2) + gradient_estim[0]
    shifted_series = time + np.tile(shifts, (nt, 1))

    low_noise_series = np.zeros(nt)
    for i in range(0, track_len):
        spline = splrep(np.arange(nt), vel_xt[:, i])
        low_noise_series += splev(shifted_series[:,i], spline)  # need to check performance

    return low_noise_series/track_len


def point_to_line(point, l0, l1):
    """
    Calculate perpendicular distance from line to a point

    Parameters
    point -  ndarray
             x, y coordinates of point
    l0 -  ndarray
             x, y coordinates of line start
    l1 -  ndarray
             x, y coordinates of line end
    """

    l_diff = l1 - l0
    norm = l_diff/(l_diff**2).sum()**0.5
    scal_proj = np.dot(point-l0, norm)  # scaler projection

    # Pythagoras
    return (((point-l0)**2).sum() - scal_proj**2)**0.5


def detect_outliers_basic(lag_estimates, lag, track_len, cross_cor_vals=None):
    """
    Crude outlier detection
    Returns 'good' points which lie less than 2x median distance from estimated gradient

    INPUT lag_estimates - 1d array
                          initial estimates for lags between time-series
            lag - 1d array
                  lag values
            track_len - int
                        length of track
            cor_vals - 1d array
                       Cross-correlation values - if provided will also use to determine 'bad' points 
    """
    grad_estim = lag * np.median(np.gradient(lag_estimates))

    # Estimated gradient is compared to the lag estimates to find perpendicular residuals
    perp_distance = np.zeros(track_len)
    for ii in range(track_len):
        point = np.array((lag[ii], lag_estimates[ii]))
        line_start = np.array((lag[0], grad_estim[0]))
        line_end = np.array((lag[track_len-1], grad_estim[track_len-1]))
        perp_distance[ii] = point_to_line(point, line_start, line_end)

    if cross_cor_vals is None:
        cross_cor_vals = np.ones(track_len)

    return ((perp_distance <= 2*np.median(perp_distance)) & (cross_cor_vals >= 0.2)).nonzero()[0]


def detect_outliers(line_best_fit, time_delay, nt, cor_vals,
                    cutoff_t=0.03, cutoff_norm=0.03):
    """
    More statistically significant tests for 'bad' data points
    First assess the residuals:
    - remove values that don't meet correlation test significance
    - calculate standard deviation for residuals
    - remove data points who residuals suggest that data points are
      'outliers' (or erroneous)

      The selection of 'outlies' requires a cutoff value that corresponds to a probability of occurrence. 
      The probability is a user defined limit.
      Assuming we want a 99.7% cutoff (3sigma for a normal distribution), i.e., points removed with a 0.3 percent chance of occurrence.
      We assume data points are sampled from a normal distribution, hence statistics follow t-distribution
      The cutoff value is then given by standard deviation*t.ppf(0.03/2.,v), where t.ppf calculates the
      t values for a two tailed test (hence the divide by 2) for v degrees of freedom. v is n-1 where
      n is the number of samples


      Correlation value has to be greater than that of random series. Cross correlation
      of random series should have sample correlations of mean 0 and variance 1/N
      N is sample number
      Using Normal CDF - erf^-1( p) *sqrt(2)/sqrt(N) you obtain a cutoff value for cross correlation
      A cutoff of 2.5sigma is p=0.987 giving significance level of ~2.58/sqrt(N)
      A cutoff of 3sigma is p=0.997 giving significance level of ~2.99997/sqrt(N)
      A cutoff of 4sigma is p=0.9999 giving significance level of ~3.99996/sqrt(N)
      A cutoff of 5 sigma is p=0.999 999 giving significance level of ~4.9999/sqrt(N)   
    """

    residuals = line_best_fit - time_delay
    good_pi = (cor_vals > 0.2).nonzero()[0]
    ngp = len(good_pi)

    if ngp > 2:
        sigma = residuals.std()
        good_mask = (np.abs(residuals) < t.ppf(1-cutoff_t/2., ngp-1.)*sigma)\
            & (cor_vals > norm.ppf(1-cutoff_norm/2.)/np.sqrt(nt))
        good_p = good_mask.nonzero()[0]
        bad_p = np.invert(good_mask).nonzero()[0]
    else:
        good_p = np.array([])
        bad_p = len(residuals)

    return good_p, bad_p


def calc_phase_speed(good_p, num_finites_vals, param, spatial_coords,
                     time_delay, line_best_fit):
    """
    ##############################################################
    DERVIVATION OF ERROR ON FIT
    From Bevington & Robinson (2003) - Chapter 6 107-111
    Estimate for variance of data and error in gradient
    Assume Chi^2_v is 1 so no information on quality of fit

    Bevington & Robinson miss correction factor for sampled data
    See Acton - Analysis of straight line data (1966)

     ~68% confidence level is given by
    t_factor given by t_cvf((1.-0.683)/2.,num_good_p-1)
    Different t_factors for different confidence levels
     speed_error =((sqrt(total((data[good_p]-line_best_fit[good_p])^2.)/(num_good_p-2)))/
    (sqrt(s_xx)))*t_factor
    ##############################################################
    """
    num_good_p = len(good_p)

    if (num_good_p > 0.3333*num_finites_vals) & (num_good_p > 2):
        phase_speed = 1/param[1]
        x_m = (spatial_coords[good_p]**2).sum()/num_good_p
        s_xx = (spatial_coords[good_p]**2).sum()-x_m
        t_factor = t.ppf(1-(1.-0.683)/2., num_good_p-1)

        #Correction to phase speed error - not the same as error in gradient -RJM
        ssr = ((time_delay[good_p]-line_best_fit[good_p])**2.).sum()
        grad_error = (ssr/(num_good_p-2))**0.5/s_xx**0.5*t_factor
        speed_error = grad_error/param[1]**2
    else:
        phase_speed = float('nan')
        speed_error = float('nan')

    return phase_speed, speed_error


def compute_speed(vel_xt, sampling, cadence, debug=False, ret=False, force_zero=False):
    """
    Compute wave speed from velocity time-distance diagram
    """

    # nt and track_len need to be ints
    nt, track_len = vel_xt.shape

    # deal with even length tracks
    if track_len % 2 == 0:
        track_len = track_len-1
    track_cen = track_len//2

    number_lag_vals = config.numberLagValues

    number_lag_vals = min(number_lag_vals, track_len)  #n umber of points in cross correlation (make odd)
    lag = np.arange(0, number_lag_vals)-np.floor(number_lag_vals / 2)
    lag = lag.astype(int)
    lag_range = min(19, track_len)  # number of points along track for initial guess (make odd)

    # Calculate initial estimates for lag values
    lag_estimates = track_cross_corr(vel_xt, track_cen, lag_range, lag)
    low_noise_series = calc_low_noise_series(lag_estimates, nt, track_len, vel_xt)

    if debug:
        ph = 1
        #plt.plot(lag,/nodata,xr=[-number_lag_vals/2.,number_lag_vals/2.],yr=[-track_len/4.-1,track_len/4.+1],ysty=1,xsty=1,xtit='Lag (Time Steps)',
        #                     ytit='Correlation',chars=1.5)

    lag_estimates_lns = track_cross_corr(vel_xt, track_cen, track_len, lag,
                                 low_noise_series=low_noise_series, debug=debug)

    ###############################################################
    # Fit line with constraints on fit
    good_p = detect_outliers_basic(lag_estimates_lns, lag, track_len)
    param = calc_gradient(lag[good_p], lag_estimates_lns[good_p])

    if ret:
        param[1] = max(-20, min(param[1], -0.01))  # Same as constrained fit
    else:
        param[1] = max(0.01, min(param[1], 20))

    line_best_fit = param[0] + lag*param[1]

    ###############################################################
    # Fit results used to define bounds for which to fit cross-correlation
    # curve with parabola to find maximum
    ###############################################################
    cross_cor_val = np.zeros(track_len)
    tstep_tolerance = 4
    nt_half = nt//2

    for i in range(track_len):
        cross_cor = lagged_correlation(low_noise_series, vel_xt[:, i])
        cross_cor = cross_cor[nt_half+lag]
        low_lim = int(round(line_best_fit[i]-tstep_tolerance+track_len//2))
        upper_lim = int(round(line_best_fit[i]+tstep_tolerance+track_len//2))

        if (low_lim > 1 and upper_lim < number_lag_vals-2):
            imax = np.argmax(cross_cor[low_lim:upper_lim])
            imax = int(round(imax+line_best_fit[i]-tstep_tolerance+track_len//2))

            if debug:
                ph = 1  #Place holder - no purpose
                # Debug option plots the bounds (triangles), the cc max (diamonds)
                # and the maximum from the parabola fit (triangle) 
                #plots, imax-number_lag_vals/2., m -track_len/4. + i*0.5, psym = 4, color=100
                #plots, low_lim-number_lag_vals/2., cross_cor[low_lim] -track_len/4. + i*0.5, psym = 5, color=250
                #plots, upper_lim-number_lag_vals/2., cross_cor[upper_lim] -track_len/4. + i*0.5, psym = 5, color=250
        else:
            imax = np.argmax(cross_cor)
            imax = max(1, min(imax, number_lag_vals-2))
            if debug:
                ph = 1
                #plots, imax-number_lag_vals/2., m -track_len/4. + i*0.5, psym = 4, color=185

        lag_estimates_lns[i] = parabola(lag[imax-1:imax+2], 1.-cross_cor[imax-1:imax+2])
        cross_cor_val[i] = cross_cor[imax]

        if debug:
            ph = 1
            #plots, lag_estimates_lns[i], m -track_len/4. + i*0.5,psym = 5,color=200

    ###############################################################
    # Do the fitting again to find new constrained slope

    good_p = detect_outliers_basic(lag_estimates_lns, lag, track_len, cross_cor_vals=cross_cor_val)

    time_delay = lag_estimates_lns*cadence
    spatial_coords = (np.arange(0, track_len)-track_len//2)*sampling

    if debug:
        ph = 1
      #plot, spatial_coords, time_delay, psym=1,xtit='Position Along Track (Mm)',ytit='Lag (s)',chars=1.5,$
                                      # xr=[-track_len/2,track_len/2]*sampling*1.5,xsty=1,$
                                      # yr=[-track_len,track_len]*4,ysty=1

    param = calc_gradient(spatial_coords[good_p], time_delay[good_p])

    if ret:
        param[1] = max(-20, min(param[1], -0.01))  # Same as constrained fit
    else:
        param[1] = max(0.01, min(param[1], 20))
    line_best_fit = param[0] + spatial_coords*param[1]

    ###############################################################
    #second iteration of line fitting

    good_p, bad_p = detect_outliers(line_best_fit, time_delay, nt, cross_cor_val)
    #pdb.set_trace()
    if len(good_p) > 2:  # Can only fit a straight line with 3 points!

        residuals = line_best_fit - time_delay
        finites_vals = np.isfinite(residuals).nonzero()[0]
        num_finites_vals = len(finites_vals)

        if num_finites_vals == len(residuals):  # ??? check statement
              err = np.abs(residuals[good_p])
        else:
            err = np.ones(len(residuals[good_p]))

        # Set zero errors to minimum value of non-zero errors
        err[(err == 0).nonzero()] = min(err[(err != 0).nonzero()])

        param = calc_gradient(spatial_coords[good_p], time_delay[good_p], weights=err)
        line_best_fit = param[0] + spatial_coords*param[1]

        phase_speed, speed_error = calc_phase_speed(good_p, num_finites_vals, param,
                                                    spatial_coords, time_delay,
                                                    line_best_fit)

        if debug:
            if len(bad_p) == 1:
                if bad_p[0] != -1:
                    ph = 1
                    #oplot,spatial_coords[bad_p],time_delay[bad_p], color=230, psym=2

            else:
                #oplot,spatial_coords[bad_p],time_delay[bad_p], color=230, psym=2
                grad_estim = spatial_coords * np.median(np.gradient(lag_estimates_lns)*cadence/sampling)
                #oplot,spatial_coords,line_best_fit, color = 150,linestyle=2
                #oplot,spatial_coords,grad_estim ,  color = 185

    else:
        phase_speed = float('nan')
        speed_error = float('nan')


    # print,'phase',phase_speed
    # stop
    
    return phase_speed, speed_error
