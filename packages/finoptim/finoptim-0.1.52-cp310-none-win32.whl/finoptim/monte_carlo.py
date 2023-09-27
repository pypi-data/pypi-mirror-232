import numpy as np
import pandas as pd
import finoptim.rust_as_backend as rs

from typing import List, Optional, Callable, Union, Dict

from finoptim.__validations__ import __standardize_prices__, __find_period__, __standardize_usage_data__

def generate_cost_coverage_couples(data: pd.DataFrame,
                                   prices: Union[Dict, pd.DataFrame, Callable[[str], Dict]],
                                   n_samples: int,
                                   period: Optional[str] = None,
                                   n_jobs: Optional[int] = 2) -> np.ndarray:

    prices = __standardize_prices__(prices)
    data, prices, _ = __standardize_usage_data__(data, prices)
    return rs.generate_cost_and_coverage(data.values, prices.values, n_samples, n_jobs, 'D')