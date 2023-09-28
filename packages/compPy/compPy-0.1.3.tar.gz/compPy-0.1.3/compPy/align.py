import numpy as np
from numpy.fft import fft2, ifft2

import matplotlib.pyplot as plt

from copy import deepcopy

import compPy.util.config as config
from compPy.util.util import get_save_dir, write_to_log
from compPy.load_defaults import load_defaults
from compPy.io.save_load import cp_load_fits, cp_save_fits, cp_save_fits_u

from scipy.ndimage import sobel, fourier_shift

from skimage.registration import phase_cross_correlation
# from skimage.feature import register_translation

__all__ = ['dejitter']


def _fg_rigidalign(data, nframes=4, quiet=True, up_sample=100):
    """
    Calculate image shifts between a series of images.

    Image shifts are calculated via FFT. Images are split into subgroups and
    shifts are calculated for subgroups.

    Returns 2d vector of (x,y) shifts

    Parameters
    ----------
       data: ndarray
             image series you want aligning
       nframes: int
                size of subgroups for alignment
       up_sample: int
                  up sampling value related to FFT shift accuracy
                  (see skimage phase_cross_correlation)
       quiet: Boolean
              Turns off messages

    Returns
    -------
        dispvecs: ndarray
                  2d array of displacement vectors in x and y
    """
    if not quiet:
        print('Value of upsampling to be used is ', up_sample)

    nt, nx, ny = data.shape

    # Place to store results
    dispvecs = np.zeros((2, nt))

    frame_index = 0
    frame_index_base = np.arange(0, nframes)  # basic group size

    stride = np.clip(nframes - 1, 1, None)

    for jj in np.arange(0, nt, stride):
        if np.max(frame_index) >= (nt - 1):
            break

        # sets up absolute frame numbers and deals with non-whole groups
        frame_index = frame_index_base + jj
        frame_index = frame_index[frame_index <= (nt - 1)]
        numb_indexs = frame_index.shape[0]

        datatemp = data[frame_index, :, :].copy()
        shift_temp = np.zeros((2, nframes))

        for count, ii in enumerate(np.arange(1, numb_indexs, 1)):

            # Calculate image displacements in group
            shift, _, _ = phase_cross_correlation(datatemp[0, :, :],
                                                  datatemp[ii, :, :],
                                                  upsample_factor=up_sample)
            shift_temp[:, ii] = shift

        if jj > 0:
            # Add displacements of first image in group
            shift_temp[0, :] += dispvecs[0, frame_index[0]]
            shift_temp[1, :] += dispvecs[1, frame_index[0]]

        dispvecs[:, frame_index] = shift_temp[:, 0:numb_indexs]

    return dispvecs


def _plot_diagnostic(offset, date):
    """Plot offsets to file."""
    fig = plt.figure(figsize=(15, 5))
    axis_val = ['x', 'y']
    over = [1, 2]

    for i, lab in zip(over, axis_val):
        ax = fig.add_subplot(1, 2, i)
        ax.plot(offset[i - 1, :])
        ax.set_xlabel('Frame number')
        ax.set_ylabel(lab + ' offset')

    outpath = get_save_dir(date)
    fig.savefig('{0}/offset_vectors_align.png'.format(outpath))
    plt.close()


def shift_frame(image, shifts):
    """"Shift image using Fourier method."""
    fft_im = fft2(image)
    return ifft2(fourier_shift(fft_im, shifts)).real


def dejitter(inputs, date, save_as_fits=False, verbose=False, **kwargs):
    """
    Align CoMP data files using FFT cross-correlation and shifting.

    We do not update the header information as the exact sky coordinates
    of the image are not known (due to issues with determining sun centre
    at the observatory).

    Parameters
    -----------
    inputs: dictionary
            CoMP cube dictionary generated from initial_load_files or
            cp_load_fits.

    Returns
    ----------
        cubes: dictionary
               updated dictionary with 'cube_i', 'cube_v', 'cube_w' shifted

    """
    if isinstance(inputs, list):
        print('Loading data from fits files.')
        comp_dict = cp_load_fits(date, keys=['i', 'v', 'w'], **kwargs)
    else:
        if not isinstance(inputs, dict):
            raise TypeError("""Input should be a dictionary from
                               cp_load_fits or a list of files""")
        else:
            comp_dict = inputs

    # ********************************************
    # get preset coordinates for sub-images

    default_vals = load_defaults(date)

    cc_coord = np.array([(default_vals['cc_coord_y1'],
                          default_vals['cc_coord_y2']
                          ),
                         (default_vals['cc_coord_x1'],
                          default_vals['cc_coord_x2']
                          )], dtype='int')

    cube_i = comp_dict['data']['cube_i'].copy()

    nt, ny, nx = cube_i.shape

    sobel_image = np.zeros((nt, ny, nx))
    for i in range(nt):
        sobel_image[i] = sobel(cube_i[i])

    # image registration using fg_rigidalign
    print('Starting alignment - may take a little while')

    count = 0
    offset = np.zeros((2, nt))

    while count < config.crossCorr['maxNumberIterations']:
        cube_i_small = sobel_image[:, cc_coord[0, 0]:cc_coord[0, 1],
                                   cc_coord[1, 0]:cc_coord[1, 1]
                                   ].copy()

        temp = _fg_rigidalign(cube_i_small, **kwargs)

        for i in range(nt):
            cube_i[i] = shift_frame(cube_i[i], temp[:, i])
            sobel_image[i] = sobel(cube_i[i])

        offset += temp

        if np.max(np.abs(temp[:])) < config.crossCorr['threshold']:
            break
        count = count + 1
        if verbose: print('Iteration Number:', count)
        if count == config.crossCorr['maxNumberIterations']:
            print('Max number of iterations reached. Try using another ' +
                  'region for alignment')

    _plot_diagnostic(offset, date)

    rms_cc = np.mean(offset**2, axis=1)**0.5

    print('=======================================')
    max_string = 'Maximum CC value {0:.4f}\n'.format(np.max(np.abs(offset)))
    print(max_string)
    write_to_log(date, max_string)

    rms_string = 'RMS CC value - x,y {0:.4f} {1:.4f}\n'.format(rms_cc[0],
                                                               rms_cc[1])
    print(rms_string)
    write_to_log(date, rms_string)

    print('Shifting cubes')
    print('=======================================')

    # apply_shifts to intensity, velocity and width
    # shift_im = np.copy(cube_i)
    # for i in range(nt):
    #    shift_im[i] = ifft2(fourier_shift(fft2(cube_i[i]), offset[:, i])).real

    comp_dict_al = deepcopy(comp_dict)
    comp_dict_al['data']['cube_i'] = cube_i

    cube_v = comp_dict['data']['cube_v'].copy()
    cube_w = comp_dict['data']['cube_w'].copy()

    shift_im = np.copy(cube_v)
    for i in range(nt):
        shift_im[i] = ifft2(fourier_shift(fft2(cube_v[i]), offset[:, i])).real
    comp_dict_al['data']['cube_v'] = shift_im

    shift_im = np.copy(cube_w)
    for i in range(nt):
        shift_im[i] = ifft2(fourier_shift(fft2(cube_w[i]), offset[:, i])).real
    comp_dict_al['data']['cube_w'] = shift_im

    if save_as_fits:
        instrument = comp_dict['primary_header'][0]['INSTRUME']
        if instrument == 'UCoMP':
            cp_save_fits_u(comp_dict_al, date)
        else:
            cp_save_fits(comp_dict_al, date)

    write_to_log(date, ' Data aligned with dejitter./n')

    file_path = get_save_dir(date)
    file_name = '{0}/{1}_offsets_align.npy'.format(file_path, date)
    np.save(file_name, offset)

    return comp_dict_al
