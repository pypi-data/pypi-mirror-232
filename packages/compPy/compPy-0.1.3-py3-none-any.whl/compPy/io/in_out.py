import numpy as np

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from itertools import groupby, product

import copy

from datetime import datetime

import compPy.util.config as config
from compPy.load_defaults import load_defaults
from compPy.util.util import print_progress_bar, write_to_log
from compPy.util.util import find_files, get_save_dir, create_save_dir
from compPy.io.save_load import cp_save_fits, cp_save_mask, cp_save_cadence
from compPy.io.save_load import cp_save_fits_u

import compPy
__version__ = compPy.__version__


from scipy.ndimage import map_coordinates
from scipy.ndimage.filters import median_filter

from astropy.io import fits
from astropy.time import Time


__all__ = ['initial_load_files']


def _compute_cadence(file_list):
    """
    Computes list of cadence from fits header times and
    produces diagnostic plot

    Parameters
    ----------
    file_list : list
      list of paths to fits files

    Returns
    --------
    list
    """

    cadence = []
    old_time = 0
    for file in file_list:
        hdr = fits.getheader(file)

        if hdr['INSTRUME'] == 'COMP':
            date_observations = hdr['DATE-OBS']
            time_observations = hdr['TIME-OBS']
            times = '{0}T{1}'.format(date_observations, time_observations)
        else:
            # for uCoMP
            times = hdr['DATE-OBS']

        new_time = Time([times], format='isot')

        if old_time > 0:
            time_diff = int(np.round(new_time.unix - old_time))
            cadence.append(time_diff)

        old_time = new_time.unix

    return cadence


def _define_start_end(date, cadence, normal_cadence,
                      interp_limit, outpath=None):
    """
    Determines the start and end frames in image sequence.

    Parameters
    ----------
    cadence : list
      list of cadences

    normal_cadence : float
      standard cadence of image sequence

    interp_limit: int
      how many frames allowed to interpolate over.

    outpath : str
      path to output directory

    Returns
    --------
    tuple

    """

    criteria = interp_limit*normal_cadence

    groups = [len(list(g)) for _, g in groupby(np.asarray(cadence) < criteria)]

    max_group = np.argmax(groups)

    if max_group == 0:
        start = 0
        end = groups[0]
    else:
        start = np.asarray(groups[:max_group]).sum()
        end = start+groups[max_group]

    mess_str = 'Files to use: Start file {0}, end file {1}\n'.format(start, end)
    write_to_log(date, mess_str)

    if outpath:
        # Diagnostic plot
        fig, ax = plt.subplots()
        ax.plot(cadence)
        ax.plot([start, start], [0, max(cadence)], 'r-', label='start/end', alpha=0.5)
        y_lim = (interp_limit+5)*normal_cadence
        ax.plot([end, end], [0, y_lim], 'r-', alpha=0.5)
        ax.set_ylabel('Cadence (s)')
        ax.set_xlabel('Frame No.')
        ax.set_ylim(0, y_lim)
        ax.xaxis.set_major_locator(MultipleLocator(10))
        ax.xaxis.set_minor_locator(MultipleLocator(2))
        plt.legend()
        plt.savefig('{0}/cadence_plot_python.png'.format(outpath))
        plt.close()

    return (start, end)


def _find_gaps(date, cadence, normal_cadence):
    """
    Find locations in image sequence where cadence is greater than the
    normal cadence, indicating locations for interpolation.

    Parameters
    ----------
    cadence : list
      list of cadences

    normal_cadence : float
      standard cadence of image sequence

    Returns
    --------
    tuple

    """

    (location_of_gaps,) = np.where(cadence > 1.1*normal_cadence)
    # number_gaps = 0 if len(location_of_gaps) == 0 else len(location_of_gaps)
    number_gaps = len(location_of_gaps)

    if number_gaps > 0:
        gap_size = np.ceil(cadence[location_of_gaps]/normal_cadence).astype(int)
        cumulative_gap_size = np.cumsum(np.insert(gap_size, 0, 0)-1)+1

        gap_start = location_of_gaps+1+cumulative_gap_size[:-1]
        gap_start.astype(int)
        number_missing_frames = cumulative_gap_size[-1]
        write_to_log(date, 'Location of missing frames: {}\n'.format(gap_start))
        write_to_log(date, 'Size of gaps: {}\n'.format(gap_size.astype(int)-1))
        write_to_log(date, 'Total missing frames: {}\n'.format(number_missing_frames))

        add = 0
        frames_to_skip = np.zeros(number_missing_frames, dtype=np.int16)
        for ii, (gsize, gstart) in enumerate(zip(gap_size, gap_start)):
            num_skip = np.arange(gsize-1)
            first = ii+add
            last = ii+add+num_skip[-1]+1
            frames_to_skip[first:last] = gstart+num_skip
            add += num_skip[-1]
    else:
        number_missing_frames = 0
        frames_to_skip = np.array([None])
        gap_start = 0
        gap_size = 0

    return {'number_gaps': number_gaps,
            'number_missing_frames': number_missing_frames,
            'frames_to_skip': frames_to_skip,
            'gap_start': gap_start, 'gap_size': gap_size
            }


def _get_names(file_list):
    """
    Gets extension names from fits files
    """
    with fits.open(file_list[0]) as hdul:
        res = hdul.info(output=False)

    int_name = res[1][1]
    dop_name = res[3][1]
    wid_name = res[4][1]

    return int_name, dop_name, wid_name

def _mask_data(cube_i, nx, ny, nm_frames, hard_mask, ucomp=False):
    """
    Create mask for data that uses doughnut aperture and
    looks for pixels that have predominantly zero signal

    Parameters
    ----------
    cube_i : ndarray
      intensity data cube

    nx : int
      image dimension

    ny : int
      image dimension

    nm_frames : int
      number of missing frames in data cube

    hard_mask : boolean
        whether to apply aggressive mask

    Returns
    --------
    ndarray

    """
    if ucomp:
        lower_r = config.lowerMaskRadiusU
        upper_r = config.upperMaskRadiusU

    else:
        lower_r = config.lowerMaskRadius
        upper_r = config.upperMaskRadius

    mask = np.zeros((ny, nx))
    x = np.arange(0, nx)-nx/2+0.5
    x = x[:, np.newaxis]*np.ones(ny)

    y = np.arange(0, ny)-ny/2+0.5
    y = y[:, np.newaxis]*np.ones(nx)

    r_polar = (x.T**2 + y**2)**0.5

    temporal_median = np.median(cube_i, axis=0)
    spatial_median = median_filter(temporal_median, size=5)

    mask[(r_polar > lower_r) & (r_polar < upper_r) & (temporal_median > 0) &
         (spatial_median > 0)] = 1.

    cube_i_max = cube_i.max(axis=0)
    mask[np.where(cube_i_max > config.i_max_clip)] = 0

    if hard_mask:
        print('Using hard mask')
        for i, j in product(np.arange(nx), np.arange(ny)):
            if mask[i, j] == 1:
                (zeros,) = (cube_i[:, i, j] == 0).nonzero()
                # set time-series to zero is they have more zeros than
                # the number of missing frames
                if zeros.size > nm_frames:
                    mask[i, j] = 0

    return mask


def _interpolate_data(cubes, gap_info, nx, ny):
    """
    Fill in missing frames via interpolation if necessary
    Should now be able to interpolate over any number of frame gaps…
    …IF DESIRED - 'Authenticity' decreases with increasing interpolation gaps

    Parameters
    ----------
    cubes : list
     list of ndarray cubes, e.g. cube_i, cube_v, cube_w

    gap_info: dict
     information on missing frames from _find_gaps

    nx : int
    ny : int
     spatial dimensions of image

    Returns
    --------
    list of ndarray cubes

    """

    # define the grid coordinates where you want to interpolate
    x_i, y_i = np.meshgrid(np.arange(ny), np.arange(nx))
    ones = np.ones((nx, ny))

    # number_gaps = gap_info['number_gaps']
    gap_start = gap_info['gap_start']
    gap_size = gap_info['gap_size']

    for start, end in zip(gap_start, gap_size):
        z = np.arange(1, end)/end
        for add, zvals in enumerate(z):

            # zvals gives interpolation locations between arr1 and arr2
            coords = ones*zvals, x_i, y_i

            loc = start+end-1
            for i, _ in enumerate(cubes):
                # join arr1, arr2 into a single array of shape (2, ny, nx)
                dum = np.r_['0,3', cubes[i][start-1], cubes[i][loc]]
                # Order=1 set interpolation to linear
                loc2 = start+add
                cubes[i][loc2] = map_coordinates(dum, coords, order=1).T

    return cubes


def _create_image_head(header: list) -> list:
    """
    Create headers for missing files.

    header - is list of image headers
    """
    head_up = []
    for head in header:
        if head == 0:
            head = copy.deepcopy(head_up[-1])
        head_up.append(head)
    return head_up


def _create_headers(cube_i_head: list, cube_v_head: list, cube_w_head: list,
                    primary_head: list, normal_cadence: int):
    """
    cube_x_head are lists of image headers
    primary_head is a list of primary headers
    """

    prim_head_up = []  # type: ignore[var-annotated]
    for head in primary_head:
        if head == 0:
            if prim_head_up[-1]['INSTRUME'] == 'COMP':
                date_time = prim_head_up[-1]['DATE-OBS'] + \
                            ' ' + prim_head_up[-1]['TIME-OBS']
            else:
                date_time = prim_head_up[-1]['DATE-OBS']

            old_time = Time(date_time)
            old_time.delta_ut1_utc = normal_cadence
            head = copy.deepcopy(prim_head_up[-1])
            
            if prim_head_up[-1]['INSTRUME'] == 'COMP':
                head['TIME-OBS'] = str(old_time.ut1.datetime.time())
            else:
                head['TIME-OBS'] = old_time.ut1.isot
        prim_head_up.append(head)

    cube_i_head_up = _create_image_head(cube_i_head)
    cube_v_head_up = _create_image_head(cube_v_head)
    cube_w_head_up = _create_image_head(cube_w_head)

    return cube_i_head_up, cube_v_head_up, cube_w_head_up, prim_head_up


def initial_load_files(date: str, hard_mask: bool = False,
                       interp_limit: int = 3, clip: bool = True,
                       ucomp: bool = False) -> dict:
    """
    Load in CoMP data files from fits and interpolates over missing frames.

    Only needs to be run once for each set of CoMP fits files (unless you
    want to modify any of the processing steps)

    Parameters
    -----------
    date: string
      date of observations that you want to load

    hard_mask: boolean, optional
      will mask out all pixels with a zero in the time-series
      i.e. missing data.
      Default=False

    interp_limit: int, optional
      how many sequential missing frames to linearly interpolate over.
      Any more than 3 and it might be worth considering a
      more appropriate interpolation method.
      Default=3

    Returns
    ---------
    comp_dict: dictionary
      contains four np.ndarrays and dictionary that correspond to:
      'cube_i' - Intensity,
      'cube_v' - Doppler velocity
      'cube_w' - Doppler width
      'mask'   - mask of good pixels
      'index'  - contains fits header and other key values for data set
    """
    # ==================================
    # Initial house keeping

    # Error handling for date string
    if not type(date) is str:
        raise TypeError('date must be a str')

    if not len(date) == 8:
        raise ValueError("date must be in form YYYYMMDD")

    # Define paths
    inpath = '{0}/CoMP/{1}/{2}/{3}/dynamics_1074'.format(
        config.root_dir, date[0:4], date[4:6], date[6:])

    outpath = get_save_dir(date)
    ret = create_save_dir(outpath)

    # ==================================
    # Look for files and extract header information
    #if ucomp:
    file_names = '*dynamics*'
    #else:
    #    file_names = '*.comp.1074.dynamics' + config.numberWaveLengths + '.fts.gz'
    file_list = find_files(file_names, inpath, home=1)

    if len(file_list) == 0:
        print('No files found')
        return

    date_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    init_mess = 'Log for {}. Ran on {}.\n \n'.format(date, date_string)
    write_to_log(date, init_mess, new=True)

    default_vals = load_defaults(date)
    start_file = int(default_vals['start_file'])
    nfiles_to_proc = int(default_vals['num_files_proc'])

    if nfiles_to_proc > len(file_list):
        file_list = file_list[start_file:-1]
    else:
        # manually exclude bad data
        file_list = file_list[start_file:start_file+nfiles_to_proc]

    # Extract image dimensions
    hdr = fits.getheader(file_list[0], ext=1)
    nx = hdr['NAXIS1']
    ny = hdr['NAXIS2']

    cadence = _compute_cadence(file_list)
    normal_cadence = int(np.median(cadence))
    write_to_log(date, '\n Cadence of data is {}s \n'.format(normal_cadence))
    cp_save_cadence(normal_cadence, date)

    # define frames to read in and find gaps
    start_frame, end_frame = _define_start_end(date, cadence, normal_cadence,
                                               interp_limit, outpath)

    # Cuts down file list to those values being loaded in
    file_list = file_list[start_frame:end_frame+1]
    cadence = np.asarray(cadence[start_frame:end_frame])

    gap_info = _find_gaps(date, cadence, normal_cadence)

    nt = end_frame-start_frame+gap_info['number_missing_frames']+1


    # Read in files and slot into cube in their place,
    # leaving gaps for missing frames
    cube_i = np.zeros((nt, ny, nx))
    cube_v = np.zeros((nt, ny, nx))
    cube_w = np.zeros((nt, ny, nx))
    time_observations = []
    primary_head = []
    cube_i_head = []
    cube_v_head = []
    cube_w_head = []

    k = 0
    add = 0
    frames_to_skip = gap_info['frames_to_skip']
    number_missing_frames = gap_info['number_missing_frames']

    int_name, dop_name, wid_name = _get_names(file_list)

    #if ucomp:
    #    dop_string = "LOS velocity"
    #else:
    #     dop_string = "Corrected LOS velocity"

    for ii in range(nt):
        if ii != frames_to_skip[k]:
            with fits.open(file_list[ii-add]) as hdul:
                primary_head.append(hdul[0].header)

                cube_i[ii] = hdul[int_name].data
                cube_i_head.append(hdul[int_name].header)

                cube_v[ii] = hdul[dop_name].data
                cube_v_head.append(hdul[dop_name].header)

                cube_w[ii] = hdul[wid_name].data
                cube_w_head.append(hdul[wid_name].header)

                if ucomp:
                    ucomp_time = Time(hdul[0].header['DATE-OBS'], 
                                      format='isot')
                    time_observations.append(str(ucomp_time.datetime.time()))
                else:
                    time_observations.append(hdul[0].header['TIME-OBS'])
        else:
            add += 1
            time_observations.append('ZERO')
            cube_i_head.append(0)
            cube_v_head.append(0)
            cube_w_head.append(0)
            primary_head.append(0)

        if k < number_missing_frames-1:
            if ii == frames_to_skip[k]:
                k = k+1
        print_progress_bar(ii + 1, nt-1, prefix='Reading in data:',
                           suffix='Complete', length=30)

    # Initial masking of data
    mask = _mask_data(cube_i, nx, ny, number_missing_frames, 
                      hard_mask, ucomp=ucomp)
    cp_save_mask(mask, date)

    cube_i = np.nan_to_num(cube_i, posinf=0)
    cube_v = np.clip(cube_v, -config.vclip, config.vclip)

    #cube_i *= mask
    #cube_v *= mask
    #cube_w *= mask

    number_gaps = gap_info['number_gaps']
    if number_gaps > 0:
        print('Interpolating data')
        args = [[cube_i, cube_v, cube_w], gap_info, nx, ny]
        cube_i, cube_v, cube_w = _interpolate_data(*args)

        headers = _create_headers(cube_i_head, cube_v_head,
                                  cube_w_head, primary_head, normal_cadence)
        cube_i_head, cube_v_head, cube_w_head, primary_head = headers

    write_to_log(date, 'Initial processing with CoMPPy v{}'.format(__version__))

    if clip:
        cube_v = np.clip(cube_v, -100, 100)

    cube_dict = {'data': {'cube_i': cube_i,
                          'cube_v': cube_v,
                          'cube_w': cube_w
                          },
                 'headers': {'cube_i_head': cube_i_head,
                             'cube_v_head': cube_v_head,
                             'cube_w_head': cube_w_head
                             },
                 'primary_header': primary_head
                 }

    if ucomp:
        cp_save_fits_u(cube_dict, date)
    else:
        cp_save_fits(cube_dict, date)

    return cube_dict
