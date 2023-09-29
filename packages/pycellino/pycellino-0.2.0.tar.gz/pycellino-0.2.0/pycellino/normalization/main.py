import numpy as np
import pandas as pd

from pycellino.decorators.main import support_groups


@support_groups
def norm_zero_shift(df: pd.DataFrame, in_col: str, out_col: str) -> pd.DataFrame:
    df[out_col] = df[in_col] - np.min(df[in_col])
    return df
