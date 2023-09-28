from compPy.util import util
from astropy.io import fits
from astropy import units as u

import pytest

def test_scale():
    '''
    Correct units are returned
    '''
    file_comp ='/Users/richardmorton/analysis/COMP/2015/01/22/20150122.012603.comp.1079.dynamics.fts.gz'
    head = fits.getheader(file_comp,ext=0)

    assert (util.calc_scale(head)).unit == u.Mm