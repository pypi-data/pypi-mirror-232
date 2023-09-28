import pandas as pd
import compPy.util.config as config


def load_defaults(date):
    """
    Load in date-specific information

    Parameters
    ----------
    date : string

    Returns
    -------
    dictionary

    """
    default_vals = {}
    path = config.home+config.modulePath+'/compPy/find_date_info.csv'
    df = pd.read_csv(path)

    df = df.set_index('date')

    if int(date) not in df.index:
        raise ValueError('Date not included in find_date_info.csv')
    else:
        ds_date = df.loc[int(date)]

    for i, v in ds_date.items():
        default_vals[i] = v

    return default_vals
