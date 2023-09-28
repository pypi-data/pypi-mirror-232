import numpy as np

__all__ = ['do_apod']

class do_apod():
    """
        Defines a 1D apodization window
        
        HISTORY: Created by R J Morton - borrowed apod function from R Rutten's plotkowpower
    """
    def __init__(self,nframe,apod_strength=0.2):

        """
        Parameters
        -----------
         nframe: int 
                 length of time-series

         apod: float
               sets strength of apodisation window
        """
        self.nframe = nframe
        self.apod_strength = apod_strength

    def create_apod_window(self):
        """
        Creates apodisation window

        Returns
        ---------
        apod_window: np.ndarray
                     apodisation window function
        cpg: float
             Coherent Power Gain - correction factor needed for
             amplitude/power of time-series after apodisation
        """
        apodt = np.ones(self.nframe)
        apodrimt = np.floor(self.nframe*self.apod_strength)
        apodt[0:apodrimt.astype(int)] = (np.sin(np.pi/2*np.arange(0, apodrimt)/apodrimt))**2
        self.apod_window = apodt*np.roll(np.flip(apodt), 1)

        # Coherent Power Gain
        self.cpg = np.sum(self.apod_window)/self.nframe

    def add_dims(self, extra_dims):
        """
        Duplicates apodisation window over extra dimensions

        Parameters
        ----------
        extra_dims - tuple
                     contains length of extra dimensions

        Use
        ---
        apod_cube = apod_window.add_dims((24,102))
        """

        new_dims = (*extra_dims, self.nframe)
        return np.broadcast_to(self.apod_window[np.newaxis, :],
                               (new_dims))
