from sunpy.map import GenericMap
from sunpy.coordinates import sun
from sunpy.map.sources.source_type import source_stretch

from astropy.io import fits
import astropy.units as u
from astropy.visualization import PowerStretch, ManualInterval
from astropy.visualization.mpl_normalize import ImageNormalize

__all__ = ['create_map']


class CoMPMap(GenericMap):
    """
    The Coronal Multi-Channel Polarimeter (CoMP) was a....

    """

    def __init__(self, data, header, **kwargs):

        # Assume pixel units are arcesc if not given
        header['cunit1'] = header.get('cunit1', 'arcsec')
        header['cunit2'] = header.get('cunit2', 'arcsec')
        header['ctype1'] = 'HPLN-TAN'
        header['ctype2'] = 'HPLT-TAN'
        super().__init__(data, header, **kwargs)

        # Fill in some missing info
        self.meta['observatory'] = 'MLSO'
        self.meta['detector'] = 'CoMP'
        self.meta['wavelnth'] = self.meta.get('wavelnth', self.meta['WAVELENG'])
        self.meta['waveunit'] = self.meta.get('waveunit', 'nm')
        # Since CoMP is on Earth, no need to raise the warning in mapbase
        self.meta['dsun_obs'] = self.meta.get('dsun_obs',
                                              sun.earth_distance(self.date).to(u.m).value)

        # not sure if these coordinates are correct
        self.meta['hgln_obs'] = header['solar_p0']  # self.meta.get('hgln_obs', 0.0)
        self.meta['hglt_obs'] = header['solar_b0']

        self.meta['date-obs'] = header['date-obs']+' '+header['time-obs']

        self._nickname = self.detector
        self.obs_key = header['extname']

        self.plot_settings['cmap'] = self._get_cmap_name()
        self._get_plot_norm()

    def _get_cmap_name(self):
        """Build the default color map name."""
        if self.obs_key == 'INTENSITY':
            cmap_string = 'sdoaia193'
        if self.obs_key == 'CORRECTED LOS VELOCITY':
            cmap_string = 'bwr'
        if self.obs_key == 'LINE WIDTH':
            cmap_string = 'plasma'
        return cmap_string.lower()

    def _get_plot_norm(self):
        """Determine which normalisation to use."""
        if self.obs_key == 'INTENSITY':
            self.plot_settings['norm'] = ImageNormalize(
                stretch=source_stretch(self.meta, PowerStretch(0.7)), clip=False)
            # Negative value pixels can appear that lead to ugly looking images.
            # This can be fixed by setting the lower limit of the normalization.
            self.plot_settings['norm'].vmin = 0.0
        if self.obs_key == 'CORRECTED LOS VELOCITY':
            self.plot_settings['norm'] = ImageNormalize(vmin=-4, vmax=4)
        if self.obs_key == 'LINE WIDTH':
            self.plot_settings['norm'] = ImageNormalize(interval=ManualInterval(vmin=0, vmax=50), clip=True)
        return self

    @property
    def observatory(self):
        """
        Returns the observatory.
        """
        return self.meta['observatory']

    @classmethod
    def is_datasource_for(cls, data, header, **kwargs):
        """Determines if header corresponds to an CoMP image"""
        return str(header.get('instrume', '')).startswith('COMP')


def create_map(filenames, key='i'):
    """
    Creates a CoMPMap which is a sub-class of Sunpy maps.

    Parameters
    ----------
    filenames - str
                list of fits files
    key - str
          selects which data product - i, v, or w

    Returns
    -------
    map or list of maps

    """

    if key == 'i':
        obs_keys = 'INTENSITY'
    if key == 'v':
        obs_keys = 'CORRECTED LOS VELOCITY'
    if key == 'w':
        obs_keys = 'LINE WIDTH'

    maps = []

    if type(filenames) != list:
        filenames = [filenames]

    for files in filenames:
        with fits.open(files) as hdul:
            data = hdul[obs_keys].data
            ext_head = hdul[obs_keys].header
            head = hdul[0].header

        missing_cards = ['NAXIS1', 'NAXIS2', 'NAXIS', 'WAVELENG', 'EXTNAME']

        for mc in missing_cards:
            head[mc] = ext_head[mc]

        maps = CoMPMap(data, head)

    return maps
