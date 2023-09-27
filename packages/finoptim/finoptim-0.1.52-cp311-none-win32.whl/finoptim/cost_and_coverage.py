import numpy as np
import pandas as pd

# import the contents of the Rust library into the Python extension
# optional: include the documentation from the Rust module
# __all__ = __all__ + ["PythonClass"]

import finoptim.rust_as_backend as rs
from finoptim.__validations__ import __standardize_prices__, __find_period__, __standardize_usage_data__


from typing import Optional, List, Union


def cost(usage: Union[pd.DataFrame, np.ndarray],
         prices: Union[dict, np.ndarray, pd.DataFrame],
         commitments: Optional[dict] = None,
         savings_plans: Union[None, float, int, np.ndarray] = None,
         reservations: Union[None, np.ndarray, dict] = None,
         period: Optional[str] = None,
         guid: Optional[List[str]] = None) -> float:
    """Compute cost based on usage.

    Args:
        usage (pd.DataFrame):  Cloud usage in hours or days. The DataFrame index must be the time.
        prices (Union[dict, pd.DataFrame]):
        Prices associated with different pricing models.
            If `dict`, keys must be pricing model and values arrays with prices in the same order as usage columns
            If `pd.DataFrame`, columns must be the same as usage and index must be pricing models

            Possible pricing models are : `{OD|RI1Y|RI3Y|SP1Y|SP3Y}`

        commitments (Optional[dict], optional): 
            A dictionnary of the different commitments. The keys must be RI or SP for reserved instances 
            and savings plans, followed by the term, in years. For exemple : 'RI3Y' or 'SP1Y'.
            If commitments is specified, `savings_plans` and `reservations` can be left to `None`.
             Defaults to None.
        savings_plans (Union[None, float, int, np.ndarray], optional):
            Commitments per hour or day, in $ or €. It can be an array as long as your usage, with an entry for each row. Defaults to None.

        reservations (Union[None, np.ndarray, dict], optional):
            Number of reserved instances. It can be an array of the same shape as your usage, if you need to specify reservations levels for every rows.
            Defaults to None.

        period (Optional[str], optional): The time between each row. Defaults to None.
        guid (Optional[List[str]], optional): _description_. Defaults to None.

    Raises:
        Exception: Negative reservation not allowed
        Exception: Can't infer the series period

    Returns:
        float: the cost associated with the usage, prices and input levels of commitments

        the savings plans levels must be the ammount of money spend per time period (hours or days)
    """

    return __general_entries__("cost", usage, prices, commitments, savings_plans, reservations, period, guid)

def underutilization(usage: pd.DataFrame,
             prices: Union[dict, pd.DataFrame],
             commitments: Optional[dict] = None,
             savings_plans: Union[None, float, int, np.ndarray] = None,
             reservations: Union[None, np.ndarray, dict] = None,
             period: Optional[str] = None,
             guid: Optional[List[str]] = None) -> float:
    """Compute under-utilization cost based on usage.

    Args:
        usage (pd.DataFrame):  Cloud usage in hours or days. The DataFrame index must be the time.
        prices (Union[dict, pd.DataFrame]):
        Prices associated with different pricing models.
            If `dict`, keys must be pricing model and values arrays with prices in the same order as usage columns
            If `pd.DataFrame`, columns must be the same as usage and index must be pricing models

            Possible pricing models are : `{OD|RI1Y|RI3Y|SP1Y|SP3Y}`

        commitments (Optional[dict], optional): 
            A dictionnary of the different commitments. The keys must be RI or SP for reserved instances 
            and savings plans, followed by the term, in years. For exemple : 'RI3Y' or 'SP1Y'.
            If commitments is specified, `savings_plans` and `reservations` can be left to `None`.
             Defaults to None.
        savings_plans (Union[None, float, int, np.ndarray], optional):
            Commitments per hour or day, in $ or €. It can be an array as long as your usage, with an entry for each row. Defaults to None.

        reservations (Union[None, np.ndarray, dict], optional):
            Number of reserved instances. It can be an array of the same shape as your usage, if you need to specify reservations levels for every rows.
            Defaults to None.

        period (Optional[str], optional): The time between each row. Defaults to None.
        guid (Optional[List[str]], optional): _description_. Defaults to None.

    Raises:
        __general_entries__: _description_

    Returns:
        float: the under-utilization cost

    Examples
    --------
    ```python
    fp.underutilization(df_real,
            prices=prices,
            commitments={'RI3Y' : {'Moule à gaufres' : 10 * 32}, 'SP3Y' : 426 * 24})

    fp.underutilization(df_days, p, savings_plans=7.6, reservations=np.array([5, 9, 3]))
    """

    raise __general_entries__("underutilization", usage, prices, commitments, savings_plans, reservations, period, guid)

def coverage(usage: pd.DataFrame,
             prices: Union[dict, np.ndarray, pd.DataFrame],
             commitments: Optional[dict] = None,
             savings_plans: Union[None, float, int, np.ndarray] = None,
             reservations: Union[None, np.ndarray, dict] = None,
             period: Optional[str] = None,
             guid: Optional[List[str]] = None) -> float:
    r"""Compute coverage based on usage.


    How coverage is defined ?

    Coverage is defined as the on demand equivalent cost of the usage running
    reserved or with savings plans, divided by the total on demand equivalent usage.

    .. math::
        c = \frac{(\sum ReservedHours \:+ \: \sum SavingsPlansHours) \times prices_{od} + UnusedSavingsPlans}{ TotalUsage \times prices_{od}}
    
    Thus the coverage can be superior to 1. This isn't necessarily a bad thing, as often the optimal commitments strategy have some under-utilization
        
    Args:
         usage (pd.DataFrame):  Cloud usage in hours or days. The DataFrame index must be the time.
        prices (Union[dict, pd.DataFrame]):
        Prices associated with different pricing models.
            If `dict`, keys must be pricing model and values arrays with prices in the same order as usage columns
            If `pd.DataFrame`, columns must be the same as usage and index must be pricing models

            Possible pricing models are : `{OD|RI1Y|RI3Y|SP1Y|SP3Y}`

        commitments (Optional[dict], optional): 
            A dictionnary of the different commitments. The keys must be RI or SP for reserved instances 
            and savings plans, followed by the term, in years. For exemple : 'RI3Y' or 'SP1Y'.
            If commitments is specified, `savings_plans` and `reservations` can be left to `None`.
             Defaults to None.
        savings_plans (Union[None, float, int, np.ndarray], optional):
            Commitments per hour or day, in $ or €. It can be an array as long as your usage, with an entry for each row. Defaults to None.

        reservations (Union[None, np.ndarray, dict], optional):
            Number of reserved instances. It can be an array of the same shape as your usage, if you need to specify reservations levels for every rows.
            Defaults to None.

        period (Optional[str], optional): The time between each row. Defaults to None.
        guid (Optional[List[str]], optional): _description_. Defaults to None.
    Raises:
        Exception: Negative reservation not allowed
        Exception: Can't infer the series period

    Returns:
        float: the coverage associated with the usage, prices and input levels of commitments

        the savings plans levels must be the ammount of money spend per time period (hours or days)
    """
    return __general_entries__("coverage", usage, prices, commitments, savings_plans, reservations, period, guid)


def under_utilisation(usage, prices, levels) -> float:
    pass


def __general_entries__(
        action: str,
        usage: Union[pd.DataFrame, np.ndarray],
        prices: Union[dict, np.ndarray, pd.DataFrame],
        commitments: Optional[dict] = None,
        savings_plans: Union[None, float, int, np.ndarray] = None,
        reservations: Union[None, np.ndarray, dict] = None,
        period: Optional[str] = None,
        guids_columns: Optional[List[str]] = None) -> float:
    

    prices = __standardize_prices__(prices)

    usage, prices, correct_order = __standardize_usage_data__(usage, prices)

    if period is not None:
        assert (period in {'hours', 'hrs', 'H', 'days', 'D', 'd', 'h'})
        changes = {'days': "D", "hours": "H",
                   "hrs": 'H', 'day': 'D', 'h': 'H', 'd': 'D'}
        try:
            period = changes[period.lower()]
        except KeyError:
            raise Exception(
                "Period not in {'hours'|'hrs'|'H'|'days'|'D'|'d'|'h'}")

    # here detect if long or wide DataFrame
    if guids_columns is not None:
        assert (guids_columns in usage.columns)
        usage = pd.pivot_table()

    X = usage.values.astype(float)
    timespan, n = X.shape
    columns = usage.columns
    if period is None:
        period = __find_period__(usage)
    usage.index = pd.to_datetime(usage.index).to_pydatetime()


    if commitments is not None:
        assert isinstance(prices, pd.DataFrame)
        assert isinstance(commitments, dict)

        assert set(prices.index).issubset(
            {'OD', 'RI1Y', 'SP1Y', 'RI3Y', 'SP3Y'})
        assert set(commitments.keys()).issubset(
            {'OD', 'RI1Y', 'SP1Y', 'RI3Y', 'SP3Y'})
        assert set(commitments).issubset(set(prices.index))
        assert 'OD' in prices.index

        models = [i for i in prices.index]

        # this part is to ensure :
        #   - same order between prices and commitments
        #   - if given commi
        for model, value in commitments.items():
            if model[:2] == 'RI':
                if isinstance(value, dict):
                    commitments[model] = np.array([value.get(guid, 0) for guid in columns])
                    assert not (commitments[model] < 0).any()
                if isinstance(value, list) or isinstance(value, np.ndarray):
                    v = np.array(value)
                    if v.ndim == 1:
                        v = v[correct_order]
                    if v.ndim == 2:
                        v = v[:, correct_order]
                    assert not (v < 0).any()
                    commitments[model] = v

        commitments = np.hstack(
            [np.zeros((timespan, 1 + (n - 1) * ('RI' == k[:2]))) + commitments[k]
                              for k in models if k in commitments])
        match action:
            case "cost":
                return rs.final_cost_coverage_underutilization(
                    X,
                    prices.values,
                    commitments,
                    models,
                    period,
                    "cost"
                )
            case "coverage":
                return rs.final_cost_coverage_underutilization(
                    X,
                    prices.values,
                    commitments,
                    models,
                    period,
                    'coverage'
                )
            case "underutilization":
                return rs.final_cost_coverage_underutilization(
                    X,
                    np.array([prices[i] for i in models]),
                    np.hstack([np.zeros((timespan, 1 + (n - 1) * ('RI' == k[:2]))) +
                              np.array(commitments[k]) for k in models if k in commitments.keys()]),
                    models,
                    period,
                    "underutilization"
                )
    if reservations is None:
        reservations = np.zeros(usage.shape)
    if isinstance(reservations, dict):
        assert isinstance(usage, pd.DataFrame)
        reservations = np.array([reservations.get(guid, 0)
                                for guid in usage.columns])
    else:
        reservations = np.array(reservations)

    match period:
        case 'D':
            reservations *= 24
        case 'H':
            pass
        case _:
            raise Exception(
                "Can't infer time_period, please provide period={'days'|'hours'}")

    match reservations.ndim:
        case 1:
            reservations = np.vstack((reservations, )*timespan)
            assert reservations.shape == usage.shape
        case 2:
            assert reservations.shape == usage.shape
        case _:
            raise Exception("Wrong number of dimensions for reservations")

    savings_plans = np.zeros((timespan, 1)) + savings_plans
    levels = np.array(
        np.hstack((savings_plans, reservations), dtype=np.float64))
    if (levels < 0).any():
        raise Exception("Negative reservation or savings plans not allowed")

    order = {"RI1Y": 3, "RI3Y": 4, "SP1Y": 1, "SP3Y": 2, "OD": 0}
    if isinstance(prices, dict):
        prices = pd.DataFrame(prices).T
        prices.sort_index(axis='index', inplace=True,
                    key=lambda x: x.map(order))
        prices = prices.values

    match action:
        case "cost":
            return rs.cost(X, np.array(prices), levels)
        case "coverage":
            return rs.coverage(X, np.array(prices), levels)
