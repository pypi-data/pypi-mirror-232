import numpy as np

from compPy.io.save_load import cp_load_mask
from compPy.util.util import calc_scale
import compPy.util.config as config
from compPy.io.in_out import find_files

from astropy import io

from scipy.io import readsav
from scipy import interpolate

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

import datetime
from datetime import datetime, timedelta

from itertools import product

from pathlib import Path


def invert_ratio(func: callable, density: np.ndarray, height: float, 
                 ratios: np.ndarray, grid_size: int = 1000):
    """
    Provide density estimate from observed line ratio.
    
    Samples spline function at a finer grid of density values
    for a particular height. The ratio values from 2D function are 
    compared to obserbed ratio. Location of minimum difference provides
    estimate of density.
    """
    
    # calculate finer grid of density values
    dens_t = np.linspace(density[0], density[-1], grid_size)
    # calculate function values on grid
    est_ratio = func(height, dens_t)
    
    if type(ratios) != np.ndarray:
        ratios = [ratios]
   
    dens_est = []
    for rat_val in ratios:
        # find location of minimum difference between observed ratio and
        # spline function
        diff = np.abs(est_ratio-rat_val)
        dens_est.append(dens_t[np.argmin(diff)])

    return np.array(dens_est)


def find_ratio_sav():
    
    home = Path.home()
    root_dir = config.root_dir[1:]
    ratio_file = config.ratio_file
    file_path = home / root_dir / 'comp/line_ratio' / ratio_file
    
    if not file_path.exists():      
        raise Exception('Expected to find ratio file at {}'.format(file_path.as_posix()))
        
    out = readsav(file_path)
    ratio_arr = out['ratio_array']
    height = out['h']
    density = out['den']

    return ratio_arr, height, density


def calc_den(cubei1074: np.ndarray, cubei1079: np.ndarray,  
             date: str, header: dict, 
             maxoffset: int = 0):
    """
    Calculate the density from ratio of CoMP lines.
    
    Calculates the ratio of the 10747 and 10798 lines and
    uses a pre-computed look-up table of intensity ratios
    created with CHIANTI for a set T and photo-ionisation rate.

    """

    cube_dims = cubei1074.ndim
    
    if cube_dims == 3:
        nt, nx, ny = cubei1074.shape
    else:
        nx, ny = cubei1074.shape
        
    spatial_sampling = calc_scale(header)  # note - this has astropy units
    spatial_sampling = spatial_sampling.value
       
    x_coord = (np.arange(nx) - nx//2)*spatial_sampling
    y_coord = (np.arange(ny) - ny//2)*spatial_sampling
    X, Y = np.meshgrid(x_coord, y_coord)
    r_coord = np.sqrt(X**2 + Y**2)

    # load mask
    mask = cp_load_mask(date)
    
    c1074_temp = cubei1074.copy()
    c1079_temp = cubei1079.copy()
    
    den_map = np.zeros(c1074_temp.shape)
        
    # easier for looping
    if cube_dims == 3:
        c1074_temp = np.transpose(c1074_temp, [1, 2, 0])
        c1079_temp = np.transpose(c1079_temp, [1, 2, 0])
    ratio = c1079_temp/c1074_temp
    
    ratio_arr, height, density = find_ratio_sav()

    # Calculates spline curve for 2D grid of line ratio vs height
    interp_func = interpolate.interp2d(height, density, ratio_arr, kind='cubic')
    
    for i, j in product(range(nx), range(ny)):
        if (mask[i, j] == 1):
            r_val = r_coord[i, j]
            dense = invert_ratio(interp_func, density, r_val, ratio[i, j])
            if cube_dims == 3:
                den_map[:, i, j] = dense
            else:
                den_map[i, j] = dense
 
    return den_map, ratio


def read_dynamics(date: str, line: int = 1074, get_data: bool = True,
                  file_range: list = [0, -1]):
    
    # Define paths
    path_1 = '{0}/CoMP/{1}/{2}/{3}'.format(
        config.root_dir, date[0:4], date[4:6], date[6:])
    path_2 = '/dynamics_{0}'.format(line)
    path = ''.join((path_1, path_2))
    res = find_files('*.fts.gz', path, home=1)

    data = []
    time_arr = []
    headers = []
    for file in res[file_range[0]:file_range[1]]:
        with io.fits.open(file) as hdul:
            time = hdul[0].header['DATE-OBS']+' '+hdul[0].header['TIME-OBS']
            time_arr.append(time)
            if get_data:
                data.append(hdul[1].data)
                headers.append(hdul[0].header)
            
    return time_arr, np.array(data), headers


def plot_times(times: list, series_name=['1074', '1079']):
    """
    Plot observation time against file number.
    
    Enables examination of observation times of data files.
    Use case is comparing observation times of 1074 to 1079
    data.
    
    Parameters
    ----------
    times - list
            a list of lists or arrays containing information on
            observation time. The observation times should be strings with
            the following format %Y-%m-%d  %H:%M:%S.
            
    series_name - list
                  Identfiers for time series. Ideally list of strings.

    """
    # list of lists or arrays
    
    # fix bug in time
    dates = []
    for time_ser in times:
        temp = [x.replace('60', '59') for x in time_ser]
        dates.append([datetime.strptime(x,'%Y-%m-%d  %H:%M:%S') for x in temp])
    
    lims = np.datetime64(dates[0][0] - timedelta(hours=0, minutes=10))

    fig = plt.figure(constrained_layout=True, figsize=(6,3))
    ax = plt.subplot(111)

    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
    # For the minor ticks, use no labels; default NullFormatter.
    ax.yaxis.set_minor_locator(MultipleLocator(5))

    for date, sname in zip(dates, series_name):
        ax.plot(date, np.arange(len(date)), label=sname)
    ax.grid()
    ax.set_xlim(lims)
    plt.legend()
    ax.set_ylabel('File Number');