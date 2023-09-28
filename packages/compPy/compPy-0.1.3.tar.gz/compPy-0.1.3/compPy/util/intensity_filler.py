from compPy.util.util import find_files, write_fill_log
from compPy.io.save_load  import cp_save_filler_fits
import compPy.util.config as config
from compPy.load_defaults import load_defaults

import numpy as np

from datetime import datetime

from astropy.io import fits
from astropy.time import Time

import copy


def intensity_filler(date, to_fill=[1]):
    """
    Creates fits files for filling in large gaps.

    Uses last intensity image before gap. Velocity and width
    are left blank.

    Primarily useful for alignment of gapped data. 

    Shouldn't be used regularly (in my opinion).
    """

    # Error handling for date string
    if not type(date) is str:
        raise TypeError('date must be a str')

    if not len(date) == 8:
        raise ValueError("date must be in form YYYYMMDD")

    # Define path
    inpath = '{0}/CoMP/{1}/{2}/{3}'.format(
        config.root_dir, date[0:4], date[4:6], date[6:])


    # ==================================
    # Look for files and extract header information
    file_names = '*.comp.1074.dynamics.' + config.numberWaveLengths + '.fts.gz'
    file_list = find_files(file_names, inpath, home=1)

    if len(file_list) == 0:
        print('No files found')
        return

    date_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    init_mess = 'Log for {}. Ran on {}.\n \n'.format(date, date_string)
    write_fill_log(date, init_mess, new=True)
    
    

    default_vals = load_defaults(date)
    start_file = int(default_vals['start_file'])
    nfiles_to_proc = int(default_vals['num_files_proc'])

    if nfiles_to_proc > len(file_list):
        file_list = file_list[start_file:-1]
    else:
        # manually exclude bad data
        file_list = file_list[start_file:start_file+nfiles_to_proc]


    filler_file = to_fill[0]-1

    # read in filler data + meta
    with fits.open(file_list[filler_file]) as hdul:
        primary_head = hdul[0].header

        inten_filler = hdul["Intensity"].data
        cube_i_head = hdul["Intensity"].header
        cube_v_head = hdul["Corrected LOS velocity"].header
        cube_w_head = hdul['LINE WIDTH'].header

    nx = cube_i_head['NAXIS1']
    ny = cube_i_head['NAXIS2']
    nt = len(to_fill)

    # create new headers and data
    normal_cadence = 30
    prim_head_up = []
    cube_i_head_up = []
    cube_v_head_up = []
    cube_w_head_up = []
    cube_i = np.zeros((nt, ny, nx))

    for i in range(len(to_fill)):
        if i == 0:
            date_time = primary_head['DATE-OBS']+' '+primary_head['TIME-OBS']
            old_time = Time(date_time)
            old_time.delta_ut1_utc = normal_cadence
            head = copy.deepcopy(primary_head)
            head['TIME-OBS'] = str(old_time.ut1.datetime.time())
        else:
            date_time = prim_head_up[-1]['DATE-OBS']+' '+prim_head_up[-1]['TIME-OBS']
            old_time = Time(date_time)
            old_time.delta_ut1_utc = normal_cadence
            head = copy.deepcopy(primary_head)
            head['TIME-OBS'] = str(old_time.ut1.datetime.time())
        prim_head_up.append(head)
        cube_i_head_up.append(cube_i_head)
        cube_v_head_up.append(cube_v_head)
        cube_w_head_up.append(cube_w_head)
        cube_i[i] = inten_filler.copy()

    # these cubes will remain as 0's
    # headers are created as dummys
    cube_v = np.zeros((nt, ny, nx))
    cube_w = np.zeros((nt, ny, nx))

    cube_dict = {'data': {'cube_i': cube_i,
                          'cube_v': cube_v,
                          'cube_w': cube_w
                          },
                 'headers': {'cube_i_head': cube_i_head_up,
                             'cube_v_head': cube_v_head_up,
                             'cube_w_head': cube_w_head_up
                             },
                 'primary_header': prim_head_up
                 }
    
    full_path = config.home+inpath

    cp_save_filler_fits(cube_dict, full_path)

    _message = 'Intensity filler used. Created following files:'
    for hd in prim_head_up:
        _message += '\n'+ hd['TIME-OBS']

    write_fill_log(date, _message)


