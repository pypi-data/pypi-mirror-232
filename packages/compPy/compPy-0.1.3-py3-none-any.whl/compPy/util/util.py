from astropy import constants as const
from astropy import units as u
from astropy.io import fits
import os
import glob

import compPy.util.config as config

_all__ = ['get_save_dir', 'write_to_log', 'calc_scale', 'print_progress_bar']

def calc_scale(header):
    ''' Calculates absolute scale of CoMP data in Mm

    Parameters
    ----------
    header : astropy.io.fits.header.Header
      header file for the data

    Returns
    -------
    astropy.units.quantity.Quantity
    '''
    r_sun_ref = const.R_sun.to('Mm')
    pix_scale = header["CDELT1"]*u.arcsec
    r_sun_obs = header["RSUN"]*u.arcsec

    return r_sun_ref*pix_scale/r_sun_obs


def print_progress_bar(iteration, total, prefix='',
                       suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar

    @params:
    iteration : int
      current iteration
    total : int
      total iterations
    prefix : str (optional)
      prefix string
    suffix  : str (optional)
      suffix string (Str)
    decimals : int (optional)
      positive number of decimals in % complete
    length      - Optional  : character length of bar (Int)
    fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(
                                      100 * (iteration / float(total)))

    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()

def get_save_dir(date):
    """
    Returns path to save directory
    """
    home_dir = config.home
    root_dir = config.root_dir
    save_dir = config.save_dir
    path_comps = [home_dir, root_dir, save_dir, date]
    return '{0}{1}{2}/{3}'.format(*path_comps)

def create_save_dir(path):
    """
    Creates the save directory
    """
    if not os.path.exists(path):
        os.mkdir(path)
    return True


def write_to_log(date, mess_str, new=False):

    outpath = '{0}{1}{2}/{3}'.format(
        config.home, config.root_dir, config.save_dir, date)

    meth = 'w' if new else 'a'

    with open(outpath+'/log_file.txt', meth) as f:
        f.write(mess_str)

    return True


def write_fill_log(date, mess_str, new=False):

    outpath = '{0}{1}{2}/{3}'.format(
        config.home, config.root_dir, config.save_dir, date)

    meth = 'w' if new else 'a'

    with open(outpath+'/fill_log_file.txt', meth) as f:
        f.write(mess_str)

    return True


def find_files(file_spec, path, home=False, silent=False):
    """
    Routine for file finding.

    A routine for finding files with certain names.
    Trying to be a python version of find_files in SOHO-CDS library IDL
    A very basic version that said!

    Parameters
    ----------
    file_spec: string
               filename or file type, e.g. '*.png'
    path: string
          file path to directory that wants searching

    home: Boolean
          If True, filepath pre-appended by home directory, otherwise
          search from current working directory

    silent: Boolean
            If True, suppresses printing of file path to command line
    """

    if home:
        file_dir = config.home
    else:
        file_dir = ''

    if not silent:
        print('Searching '+file_dir+path+'/'+' for ' + file_spec)

    filelist = sorted(glob.glob(file_dir+path+'/'+file_spec))

    return filelist
