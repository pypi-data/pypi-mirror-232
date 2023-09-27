import warnings

import numpy as np
import pandas as pd

from typing import Union

# import the contents of the Rust library into the Python extension
# optional: include the documentation from the Rust module
# __all__ = __all__ + ["PythonClass"]


def add_one(x: int) -> int:
    """see if documentation works

    Args:
        x (int): your number

    Returns:
        int: number + 1
    """
    return x + 1


def __standardize_prices__(prices) -> pd.DataFrame:

    if isinstance(prices, pd.DataFrame):
        assert (set(prices.index).issubset(
            {'OD', 'RI1Y', 'SP1Y', 'RI3Y', 'SP3Y'}))
        prices_df = prices

    if isinstance(prices, np.ndarray):
        raise Exception("you can't pass prices as np.ndarray, as you need to specify what every price applies to.")

    if isinstance(prices, dict):
        if all([isinstance(p, dict) for p in prices.values()]):
            prices_df = pd.DataFrame(prices)
        if all([(isinstance(p, pd.Series) or isinstance(p, np.ndarray)) for p in prices.values()]):
            prices_df = pd.DataFrame(prices).T
        assert (set(prices_df.index).issubset(
            {'OD', 'RI1Y', 'SP1Y', 'RI3Y', 'SP3Y'}))

    if callable(prices):
        raise NotImplemented("Not Implemented Yet")

    try:
        # here take into account already payed reservations and sps ?
        order = {"RI1Y": 3, "RI3Y": 4, "SP1Y": 1, "SP3Y": 2, "OD": 0}
        prices_df.sort_index(axis='index', inplace=True,
                    key=lambda x: x.map(order))
        return prices_df
    
    except UnboundLocalError:
        raise TypeError("prices must be either pd.DataFrame, dict or Callable")


def __standardize_usage_data__(usage, standardized_prices) -> pd.DataFrame:
    
    if isinstance(usage, list):
        datas = [__standardize_usage_data__(d, standardized_prices) for d in usage]
        return [d[0] for d in datas], datas[0][1], datas[0][-1]

    if isinstance(usage, pd.DataFrame):
        correct_order = np.arange(len(usage.columns))

        if not set(usage.columns).issubset(set(standardized_prices)):
            warnings.warn("""The given prices do not specify one or more guids.
                          Consider passing a pandas DataFrame with guids as columns instead of a dict.\n
                          If the prices are in the same order as the usage, you can ignore this warning.
                          """)
        sps = set([c for c in standardized_prices.index if c[:2] == 'SP'])
        if sps:
            # order to sort instance families by savings plans discount from left to right
            correct_order = standardized_prices.loc[sps.pop()].div(standardized_prices.loc['OD'])
            correct_order = np.argsort(correct_order.values)
        standardized_prices.reindex(columns=standardized_prices.columns[correct_order])
        usage = usage.reindex(columns=usage.columns[correct_order])

    if isinstance(usage, np.ndarray):
        raise Exception("You need to provide a DataFrame with sku as columns and dates as index")

    return usage, standardized_prices, correct_order


def __sort_data__(data: Union[list, pd.DataFrame], price: pd.DataFrame) -> pd.DataFrame:
    pass

def __find_period__(df: pd.DataFrame) -> str:
    if isinstance(df.index, pd.PeriodIndex):
        return df.index.freqstr
    else:
        dates = pd.to_datetime(df.index)
    periods = np.diff(dates, 1)
    if periods.min() != periods.max():
        warnings.warn("Careful, you have missing datas in your usage")
    return dates.inferred_freq
