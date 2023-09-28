""" collection of tools for tests """

from io import StringIO

import pandas as pd


def df_from_csvstr(txt, index_col=0):
    """create and return a pandas dataframe from passed string

    >>> txt = '''gid,X,Y,Z
    ...          1,374.793,-47.7918,14.6654
    ...          2,374.793,-46.965,14.6654'''
    >>> df_from_csvstr(txt)
               X        Y        Z
    gid
    1    374.793 -47.7918  14.6654
    2    374.793 -46.9650  14.6654
    """
    exp = StringIO(txt)
    df = pd.read_csv(exp, index_col=index_col)
    return df


if __name__ == "__main__":
    import doctest

    doctest.testmod()
