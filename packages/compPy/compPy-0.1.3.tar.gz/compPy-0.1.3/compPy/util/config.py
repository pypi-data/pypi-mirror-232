"""
CoMP configuration file.

Default values for individual components of pipeline.

"""

import os.path as osp

# ----------------------------------
# I/O
root_dir = '/analysis'
numberWaveLengths = ''#'.3'
modulePath = '/py_routines/compPy'  # why is this here?
home = osp.expanduser("~")
save_dir = '/CoMP/wave_tracking_output'
proc_dir = '/processed_data'

# ----------------------------------
# Cross-correlation parameters
# Used for alignment of images
crossCorr = {"threshold": 0.04, "maxNumberIterations": 20}

# ----------------------------------
# Sun parameters
radiusSunMm = 695.7  # solar radius in Mm

# ----------------------------------
# Basic mask parameters
upperMaskRadius = 290  # pixel radius just greater than 1.3 Rsun
lowerMaskRadius = 220  # pixel radius just greater than 1.02 Rsun

upperMaskRadiusU = 580  # pixel radius just greater than 1.3 Rsun
lowerMaskRadiusU = 340  # pixel radius just greater than 1.02 Rsun

# -----------------------------------
# for clipping outlier values
# EXPERIMENTAL 
vclip = 50  # in km/s
i_max_clip = 100


# ----------------------------------
# Wave angle calculations
coherence = {"BoxHalfLength": 10,
             "smoothing": 15,
             "limit": 0.5,
             "minNumberPixels": 10}

filters = {"width": 0.0015,
           "centralFrequency": 0.0035}


# ----------------------------------
# Phase speed measurement parameters

# Path length for phase speed measurement. Defines x-t diagrams to be
# used for cross-correlation, maximum useful length appears
# to be around 21. Signal only correlates well over sort distances.
# Make odd.
maxTrackLength = 31 #25

# Fourier filtering can add edge effects.
# So some crude attempt to remove effected time-series from cross correlation
# calculation.
# Keep odd.
row_trim = 1

# Applies Welch-type approach to cross-correlation, i.e. windowed and
# overlapped segments of time-series
win_dur = 51
overlap = 0.5

# Parameters for Theil slopes estimator for gradient of lag vs distance
alpha_ts = 0.6827  # 1 sigma confidence levels
bootstrap = False  # whether to apply bootstrap
num_bs = 300  # number of bootstrap samples

pause_time = 3  # sets the delay time for debugging

# number of lag values to calculate cross-correlation at. Make odd.
# used in old version
numberLagValues = 29

# ----------------------------------
# Density measurements
ratio_file = 'rat.sav' #'ratios_chianti_10.sav'