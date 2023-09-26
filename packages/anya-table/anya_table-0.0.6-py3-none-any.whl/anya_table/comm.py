import pandas as pd

def getCats(values, n_bins=9):
    """
    Assign category code to numeric values
    Arguments:
      - values (pd.Series): series of values
      - n_bins (int): number of categories, defautls to 9
    Outputs:
      - cats (list): list of resulted category codes
    """
    cats, _  = pd.cut(values, bins=n_bins, include_lowest=True, right=False, retbins=True)
    cats = cats.cat.codes + 1
    return cats
