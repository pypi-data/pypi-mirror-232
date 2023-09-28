import pytest

from compPy.load_defaults import load_defaults


def test_value_error():

    random_date = '19990103'
    with pytest.raises(ValueError)as exc_info:
        load_defaults(random_date)
    assert exc_info.match('Date not included in find_date_info.csv')
