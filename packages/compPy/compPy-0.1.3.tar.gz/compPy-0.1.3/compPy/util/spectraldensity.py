import numpy as np
from scipy.ndimage import uniform_filter1d

from copy import deepcopy

import pdb
def spectral_density(spectrum1, spectrum2=np.ones(1)):
    """Calculate spectral density (auto or cross)
       Works for arrays with multiple dimensions

       Parameters
       ------------
       spectrum1: ndarray
                  FFT of time-series.

       spectrum2: ndarray
                  FFT of a second time-series (optional). Can be
                  multi-dimensional array but
                  expects axis=0 is the frequency axis
    """

    # Set second spectrum
    if spectrum2.shape[0] == 1:
        spectrum2 = deepcopy(spectrum1)
        auto = True
    else:
        auto = False

    spec_dens = spectrum1 * spectrum2.conj()

    return spec_dens.real if auto else spec_dens


def smooth_spec_dens(spec_dens, smoothing=15, mimic_idl=True,
                     filter_func=None, **filter_kwargs):
    """
    Calculate smooth spectral density using uniform filter.

    Mimics IDL behaviour for end-points (no smoothing)

    Parameters
    ------------
    spec_dens - ndarray
                spectral density (auto or cross). Can be multi-dimensional
                array but expects axis=0 is the frequency axis

    smoothing - int
                degree of smoothing
    mimic_idl - boolean
    """

    if not filter_func:
        filter_func = uniform_filter1d

    is_complex = np.iscomplexobj(spec_dens)
    nx, ny = spec_dens.shape[1:]

    if not is_complex:
        spec_dens_smooth = filter_func(spec_dens[1:], smoothing, axis=0)
        spec_dens_smooth = np.concatenate((np.zeros((1, nx, ny)),
                                          spec_dens_smooth), axis=0)

    else:
        spec_dens_smooth_real = filter_func(spec_dens[1:].real, smoothing,
                                            axis=0)
        spec_dens_smooth_imag = filter_func(spec_dens[1:].imag, smoothing,
                                            axis=0)
        spec_dens_smooth = spec_dens_smooth_real + 1j * spec_dens_smooth_imag
        spec_dens_smooth = np.concatenate((np.zeros((1, nx, ny),
                                           dtype=np.complex_),
                                          spec_dens_smooth), axis=0)
    # to mimic IDL behaviour
    if mimic_idl:
        spec_dens_smooth[0:smoothing // 2] = spec_dens[0:smoothing // 2]
        spec_dens_smooth[-smoothing // 2:] = spec_dens[-smoothing // 2:]

    return spec_dens_smooth


# class SpectralDensity():
#     """Caclulates a spectral density. 
    
#        Can calculate smoothed spectral density.
       
#        Mimics IDL behaviour for end-points (no smoothing)
    
#        Parameters
#        ------------
#        smoothing - degree of smoothing
#        auto - Default (=1) calculates auto spectral density
    
#     """
    
    
#     def __init__(self, auto=1):
#         self.auto = auto
    
#     def spec_density(self, spectrum1, spectrum2=None):
#         """Calculate spectral density (auto or cross)
#            Works for arrays with multiple dimensions

#            Parameters
#            ------------
#            spectrum1: np.ndarray 
#                       FFT of time-series
           
#            spectrum2: np.ndarray
#                       FFT of a second time-series (optional)
#         """

#         self.spectrum1_ =spectrum1
        
#         #Set second spectrum
#         if self.auto == 1:
#             self.spectrum2_ = self.spectrum1_
#         else:
#             self.spectrum2_ = spectrum2
        
        
#         if self.auto == 1:
#             self.spec_dens_ =( self.spectrum1_ * self.conj() ).real
#         else:
#             self.spec_dens_ = self.spectrum1_ * self.conj()
        
#         return self
    
#     def smooth(self, smoothing=15):
#         """Calculate smooth spectral density.
        
#            Parameters
#            ------------
#            smoothing - degree of smoothing
#         """
#         self.smoothing = smoothing
        
#         if self.auto == 1:
#             self.spec_dens_smooth = uniform_filter1d(self.spec_dens_ ,self.smoothing,axis=0)
#             #to mimic IDL behaviour
#             self.spec_dens_smooth[0:self.smoothing//2]=self.spec_dens_[0:self.smoothing//2]
#             self.spec_dens_smooth[-self.smoothing//2:]=self.spec_dens_[-self.smoothing//2:]
#         else:
#             spec_dens_smooth_Real = uniform_filter1d(self.spec_dens_.real,self.smoothing,axis=0)
#             spec_dens_smooth_Imag = uniform_filter1d(self.spec_dens_.imag,self.smoothing,axis=0)
#             self.spec_dens_smooth=spec_dens_smooth_Real+1j*spec_dens_smooth_Imag
            
#             self.spec_dens_smooth[0:self.smoothing//2]=self.spec_dens_[0:self.smoothing//2]
#             self.spec_dens_smooth[-self.smoothing//2:]=self.spec_dens_[-self.smoothing//2:]
        
#         return self.spec_dens_smooth
                
#     def conj(self):
#         """Calculate conjugate spectrum"""
#         self.conj_spec_=np.conj(self.spectrum2_)
#         return self.conj_spec_