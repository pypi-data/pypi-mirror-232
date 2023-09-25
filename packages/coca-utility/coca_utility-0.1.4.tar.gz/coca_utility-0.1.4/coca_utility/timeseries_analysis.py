import pandas as pd
from statsmodels.tsa.stattools import adfuller


def adfuller_test(series: pd.Series) -> dict:
    return dict(
        zip(
            ("adf", "pvalue", "usedlag", "nobs", "critical values", "icbest"),
            adfuller(series),
        )
    )
