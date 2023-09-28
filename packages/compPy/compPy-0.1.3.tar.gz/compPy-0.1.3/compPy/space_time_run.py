from compPy.io.save_load import cp_save_pro_ret, cp_save_speeds
from compPy.io.save_load import cp_load_angles, cp_load_mask, cp_load_cadence

# from compPy.compute_speed import compute_speed

from compPy.util.util import print_progress_bar, calc_scale
import compPy.util.config as config

from compPy.compute_speed import compute_speed

from copy import deepcopy

import numpy as np
from numpy.fft import fftfreq

from scipy.signal import medfilt
from scipy.ndimage import map_coordinates, spline_filter
from scipy.fftpack import fftn, ifftn

from itertools import product


__all__ = ['space_time_run']


class Track:

    def __init__(self, max_track_length):
        self.length = 1
        self.max_length = max_track_length
        self.angles = np.zeros(max_track_length)
        self.x_coords = np.zeros(max_track_length)
        self.y_coords = np.zeros(max_track_length)

    def midpoint_vals(self, x, y, angle):
        midpoint = int(self.max_length // 2)
        self.x_coords[midpoint] = x
        self.y_coords[midpoint] = y
        self.angles[midpoint] = angle

    def trim(self):
        # Trim track arrays if necessary
        if self.length < self.max_length:
            vals = (self.x_coords != 0).nonzero()
            self.x_coords = self.x_coords[vals]
            self.y_coords = self.y_coords[vals]

    def check_direction(self, rad):
        """
        Check whether track is outward or inward.

        Swap values (if needed) so prograde corresponds to outward.
        """
        rad_1 = rad[int(round(self.y_coords[-1])),
                    int(round(self.x_coords[-1]))]

        rad_2 = rad[int(round(self.y_coords[0])),
                    int(round(self.x_coords[0]))]
        swap_track = np.sign(rad_1 - rad_2)
        if swap_track == -1:
            self.angles = self.angles[::-1]
            self.x_coords = self.x_coords[::-1]
            self.y_coords = self.y_coords[::-1]


def gauss_filter(ntime, cadence, mu, sigma):
    """
    Define Gaussian filter.

    Parameters
    -----------
    ntime - int
            number of elements in a particular dimension
    cadence - floating-point
              cadence of observations
    mu - float
         mean of filter
    sigma - float
            standard deviation of filter

    Returns
    -------
    ndarray
    """
    freq = fftfreq(ntime, d=cadence)
    freq_filter = np.exp(-(freq - mu)**2 / sigma**2)
    freq_filter += np.exp(-(freq + mu)**2 / sigma**2)
    freq_filter[freq == 0] = 0.  # set dc to zero
    # set low frequencies to zero
    freq_filter[(np.abs(freq) < .001).nonzero()] = 0.
    freq_filter = freq_filter / freq_filter.sum()
    freq_filter[(freq_filter < 1e-10).nonzero()] = 0  # stops underflow errors

    return freq_filter


def radial_values(nx, ny):
    """
    Calculate array of radial values.

    Parameters
    -----------
    nx - int
         number of elements in a particular dimension
    ny - int
         number of elements in a particular dimension

    Returns
    -------
    ndarray of shape (nx,ny)

    """
    x = np.tile(np.arange(0, nx) - (nx / 2.) + 0.5, (ny, 1))
    y = np.tile(np.arange(0, ny) - (ny / 2.) + 0.5, (nx, 1))
    return np.sqrt(x**2 + y.T**2)


def prep_cutouts(velocity, mask, rad, angle, cut_out):
    """
     Creates cut-outs from given coordinates.

     Cut-out regions are selected and then padded with zeros. 
    """
    n_pad = 20

    velocity = velocity[:, cut_out[0]:cut_out[1], cut_out[2]:cut_out[3]]
    velocity = np.pad(velocity, ((0,0),(n_pad, n_pad), (n_pad, n_pad)), constant_values=0)

    mask = mask[cut_out[0]:cut_out[1], cut_out[2]:cut_out[3]]
    mask = np.pad(mask, ((n_pad, n_pad), (n_pad, n_pad)), constant_values=0)

    rad = rad[cut_out[0]:cut_out[1], cut_out[2]:cut_out[3]]
    rad = np.pad(rad, ((n_pad, n_pad), (n_pad, n_pad)), constant_values=0)

    angle = angle[cut_out[0]:cut_out[1], cut_out[2]:cut_out[3]]
    angle = np.pad(angle, ((n_pad, n_pad), (n_pad, n_pad)), constant_values=0)

    ny, nx = velocity[0, :, :].shape
    return velocity, mask, rad, angle, ny, nx


def filter_velocity(velocity_xt: np.ndarray, freq_filter: np.ndarray, 
                    dt: float, dx: float, phase_cut=0.1):
    """
    Filter inward and outward waves.

    Parameters
    ----------
    velocity_xt - ndarray
                  velocity time-distance diagram

    freq_filter - ndarray
                  frequency filter
    dt - float
         cadence
    dx - float
         spatial sampling

    Returns
    -------
    ndarray
    """
    nt, track_len = velocity_xt.shape

    filt_2d = np.tile(freq_filter, (track_len, 1))

    velocity_xt = velocity_xt - velocity_xt.mean()
    # remove temporal mean
    velocity_xt = velocity_xt - np.tile(velocity_xt.mean(axis=0), (nt, 1))
    velocity_fft = ifftn(velocity_xt) * filt_2d.T

    # Doesn't need correct sampling time
    freq = np.tile(fftfreq(nt, dt), (track_len, 1)).T
    wave_num = np.tile(fftfreq(track_len, dx), (nt, 1))
    phase_sign = np.sign(freq * wave_num)
    phase_speed = np.divide(freq, wave_num, 
                            out=np.zeros_like(freq),
                            where=(wave_num != 0))
    # select prograde waves (assume nt even, track_len odd)
    pro_spectrum = velocity_fft.copy()
    pro_spectrum[(phase_sign >= 0).nonzero()] = 0
    # filter phase speeds less than value
    pro_spectrum[(phase_speed >= -1*phase_cut).nonzero()] = 0
    prograde_velocity = fftn(pro_spectrum).real
    
    ret_spectrum = velocity_fft.copy()            # select retrograde waves
    ret_spectrum[(phase_sign <= 0).nonzero()] = 0
    # filter phase speeds less than value
    ret_spectrum[(phase_speed <= phase_cut).nonzero()] = 0
    retrograde_velocity = fftn(ret_spectrum).real

    return {'retrograde': retrograde_velocity, 'prograde': prograde_velocity}


def define_track(track, hemisphere, nx, ny, i, factor, angle, mask):
    """
    Calculate which x and y direction to follow.

    Updates track dictionary.

    Parameter
    ---------
    track - dict
            a track dictionary
    hemisphere - int
                 value ensure signal always steps away from occulting disk
    nx, ny - int
             array dimensions
    i - int
        index along track
    factor - int
            0 or 180 - defines moving up or down the track
    angle - ndarray
            array of angles from compute_waveang
    mask - ndarray
           mask for data


    Returns
    -------
    Boolean - indicates success or failure
    """
    return_value = True

    sign = -1 if factor == 0 else 1
    angle_prev = np.radians(track['angles'][i + sign] + factor)
    x_prev = track['x_coords'][i + sign]
    y_prev = track['y_coords'][i + sign]
    track['x_coords'][i] = max(0, min(x_prev - hemisphere * np.cos(angle_prev), nx - 1))
    track['y_coords'][i] = max(0, min(y_prev - hemisphere * np.sin(angle_prev), ny - 1))

    next_x = max(0, min(int(track['x_coords'][i] + 0.5), nx - 1))
    next_y = max(0, min(int(track['y_coords'][i] + 0.5), ny - 1))

    # pixcheck = np.sqrt((next_x-nx/2.+0.5)**2 + (next_y-ny/2.+0.5)**2)
    # if (pixcheck < low_lim) or (pixcheck > upper_lim):
    if mask[next_y, next_x] == 0:
        track['x_coords'][i] = 0.
        track['y_coords'][i] = 0.
        return_value = False

    if return_value:
        track['length'] += 1
        track['angles'][i] = angle[next_y, next_x]

        # if big difference in adjacent angles, resolve 180 degree ambiguity
        # by choosing angle closest to ang_track(i-1)
        angle_difference = track['angles'][i] - track['angles'][i + sign]
        if abs(angle_difference) > 90:
            track['angles'][i] += -180 if (angle_difference > 0) else 180

    return return_value


def check_direction(temp_track, x_track, y_track, rad):
    """
    Check whether track is outward or inward.

    Swap values (if needed) so prograde corresponds to outward.
    """
    swap_track = np.sign(rad[int(round(y_track[-1])),
                             int(round(x_track[-1]))] -
                         rad[int(round(y_track[0])),
                             int(round(x_track[0]))])
    if swap_track == -1:
        temp_track['angles'] = temp_track['angles'][::-1]
        temp_track['x_coords'] = temp_track['x_coords'][::-1]
        temp_track['y_coords'] = temp_track['y_coords'][::-1]
    return swap_track


def calc_phase_speed(speeds: dict):
    """
    Calculate phase speed using weighted mean.

    """
    pro_err_sq = speeds['prograde_error']**2
    ret_err_sq = speeds['retrograde_error']**2
    relative_speed_pro = speeds['prograde'] / pro_err_sq
    relative_speed_ret = abs(speeds['retrograde']) / ret_err_sq
    relative_error_sq = 1 / pro_err_sq + 1 / ret_err_sq

    speeds['phase_speed'] = (relative_speed_pro +
                             relative_speed_ret) / relative_error_sq
    speeds['phase_speed_error'] = (1./relative_error_sq)**0.5

    return speeds


def space_time_run(cube_v: np.ndarray, header: dict, date: str,
                   name_addon: str = '', debug: bool = False,
                   filter_cubes: bool = False, name_addon_mask: str = '',
                   cut_out=[],
                   **kwargs):
    """
    Compute space-time diagram of velocity time-series over a whole image.

    OUTLINE:  The coordinates of velocity xt tracks are computed for each pixel
    using the wave angle map (calculated with compute_waveang.py).

    Doppler Velocities are interpolated onto a time-distance map using the
    defined coordinates. The FFT of each map is taken and high spatial and
    temporal frequencies are removed.

    The time-distance maps are separated into prograde and retrograde
    components (i.e., where w=ck & w=-ck). Inverse
    Fourier transform is computed and filtered xt tracks are sent to
    compute_speed to compute the propagation speed.

    Parameters:
    date - str
           date of observations
    cube_v - ndarray (3d)
             Aligned + trimmed Doppler velocity cube
    header - dict
             A primary header file
    name_addon - str
                 additional quantifier to be added to load/save files
    name_addon_mask - str
                 additional quantifier to be added to load mask files

    filter_cubes - bool
                   Saves pro/retro - grade velocity maps


    HISTORY: Moved from IDL to Python 03/20 RJM
    """
    if len(name_addon_mask) == 0:
        name_addon_mask = name_addon

    mask = cp_load_mask(date, name_addon=name_addon_mask)
    angle = cp_load_angles(date, name_addon=name_addon)
    angle_err = angle[1]
    angle = angle[0]

    # update mask values so to ignore pixels where wave angle not valid
    # mask[angle_err == 0] = 0
    
    # Define constants & variables from index
    ntime, ny, nx = cube_v.shape
    norm_cadence = cp_load_cadence(date)
    spatial_sampling = calc_scale(header)  # note - this has astropy units
    spatial_sampling = spatial_sampling.value

    max_track_length = config.maxTrackLength
    mid_point = int(max_track_length // 2)

    # number of time points to use (make even)
    nt = ntime if (ntime % 2) == 0 else ntime - 1
    velocity = cube_v[0:nt, :, :].copy()

    if filter_cubes:
        freq_filter = np.ones(nt, dtype='float64')
    else:
        freq_filter = gauss_filter(nt, norm_cadence,
                                   config.filters['centralFrequency'],
                                   config.filters['width'])
    rad = radial_values(nx, ny)
    angle = medfilt(angle, kernel_size=3)  # Median smoothing to reduce noise

    if len(cut_out) > 0:
        velocity, mask, rad, angle, ny, nx = prep_cutouts(velocity, mask, rad, angle, cut_out)

    # Define x and y limits for map
    location_limits = (mask == 1).nonzero()
    xstart = location_limits[1].min()
    xend = location_limits[1].max()
    ystart = location_limits[0].min()
    yend = location_limits[0].max()
    pixels2process = len(location_limits[0])

    # Empty track template
    track = {"length": 1,
             "angles": np.zeros(max_track_length, dtype='float64'),
             "x_coords": np.zeros(max_track_length, dtype='float64'),
             "y_coords": np.zeros(max_track_length, dtype='float64')
             }

    # Define dictionary of arrays to store prograde and retrograde quantities
    zer_arr = np.zeros((ny, nx), dtype='float64') + 999.
    speeds = {'prograde': zer_arr.copy(),
              'retrograde': zer_arr.copy(),
              'phase_speed': zer_arr.copy(),
              'prograde_error': zer_arr.copy(),
              'retrograde_error': zer_arr.copy(),
              'phase_speed_error': zer_arr.copy(),
              'track_len': zer_arr.copy()
              }

    # Pre-filter cube_v for faster interpolation in for loops
    print('Pre-filtering data')
    vel_coeffs = np.zeros((nt, ny, nx), dtype='float64')
    for i in np.arange(nt):
        vel_coeffs[i, :, :] = spline_filter(velocity[i, :, :])

    if filter_cubes:
        pro_cube = np.zeros((nt, ny, nx), dtype='float64')
        ret_cube = np.zeros((nt, ny, nx), dtype='float64')

    # Main section of the routine
    print('Starting processing...')
    count = 0

    for y_coord, x_coord in product(range(ystart, yend), range(xstart, xend)):

        if mask[y_coord, x_coord] == 1:

            print_progress_bar(count, pixels2process,
                               prefix='Calculating speeds:',
                               suffix='Complete', length=30)

            temp_track = deepcopy(track)
            temp_track['x_coords'][mid_point] = x_coord
            temp_track['y_coords'][mid_point] = y_coord
            temp_track['angles'][mid_point] = angle[y_coord, x_coord]

            #  first, move out from cursor coord
            hemisphere = 1 if x_coord <= nx // 2 - 1 else -1
            factor = 0

            for i in range(mid_point + 1, max_track_length):
                res = define_track(temp_track, hemisphere,
                                   nx, ny, i, factor, angle, mask)
                if not res:
                    break

            #  next, move in from cursor coord
            factor = 180
            for i in range(mid_point - 1, -1, -1):
                res = define_track(temp_track, hemisphere,
                                   nx, ny, i, factor, angle, mask)
                if not res:
                    break

            if temp_track['length'] < 4:
                continue  # take at least 5 points in the track

            # Trim track arrays if necessary
            vals = (temp_track['x_coords'] != 0).nonzero()
            x_track = temp_track['x_coords'][vals]
            y_track = temp_track['y_coords'][vals]
 
            # note - temp_track changed in function if required, this works as
            # temp_track is dictionary 
            res = check_direction(temp_track, x_track, y_track, rad)
        
            # re-instate in case change of direction
            vals = (temp_track['x_coords'] != 0).nonzero()
            x_track = temp_track['x_coords'][vals]
            y_track = temp_track['y_coords'][vals]

            velocity_xt = np.zeros((nt, temp_track['length']))

            for i in range(0, nt):
                velocity_xt[i, :] = map_coordinates(vel_coeffs[i, :, :],
                                                    np.vstack((y_track, x_track)),
                                                    prefilter=False)

            velocity_filt = filter_velocity(velocity_xt, freq_filter, norm_cadence, 
                                            spatial_sampling)

            ##############################################################
            # compute phase speeds of prograde, retrograde and combination

            if filter_cubes:
                tl2 = velocity_filt['prograde'].shape[1] // 2
                pro_cube[:, y_coord, x_coord] = velocity_filt['prograde'][:, tl2]
                ret_cube[:, y_coord, x_coord] = velocity_filt['retrograde'][:, tl2]
            else:

                if temp_track['length'] > (config.row_trim * 2 + 3):
                    param = compute_speed(velocity_filt['prograde'],
                                          spatial_sampling, norm_cadence)
                    speeds['prograde'][y_coord, x_coord] = param[0]
                    speeds['prograde_error'][y_coord, x_coord] = param[1]

                    param = compute_speed(velocity_filt['retrograde'],
                                          spatial_sampling, norm_cadence,
                                          ret=True)
                    speeds['retrograde'][y_coord, x_coord] = param[0]
                    speeds['retrograde_error'][y_coord, x_coord] = param[1]
                    speeds['track_len'][y_coord, x_coord] = temp_track['length']
            count = count + 1

    if filter_cubes:
        cp_save_pro_ret(date, pro_cube, ret_cube, name_addon=name_addon)
    else:
        speeds = calc_phase_speed(speeds)
        cp_save_speeds(date, speeds, name_addon=name_addon)

    if filter_cubes:
        return
    else:
        return speeds

