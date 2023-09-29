from abc import ABC, abstractmethod
from typing import Callable, List, Optional

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression as SkLearnLinearRegression

from pycellino.decorators.main import support_groups


class RegressionBase(ABC):
    def __init__(self):
        self.model = None

    @abstractmethod
    def fit(self, x, y):
        pass

    @abstractmethod
    def predict(self, x):
        pass

    def fill(
        self,
        df: pd.DataFrame,
        x_column_name: str,
        y_column_name: str,
        min_data_points: int = 5,
        set_negatives_to_zero: bool = False,
        group_columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        df = fill_with_regression(
            df=df,
            model=self,
            x_column_name=x_column_name,
            y_column_name=y_column_name,
            min_data_points=min_data_points,
            set_negatives_to_zero=set_negatives_to_zero,
            group_columns=group_columns)
        return df


@support_groups
def fill_with_regression(
    df: pd.DataFrame,
    model: RegressionBase,
    x_column_name: str,
    y_column_name: str,
    min_data_points: int = 5,
    set_negatives_to_zero: bool = False
) -> pd.DataFrame:
    df = df.sort_values(by=x_column_name)
    xs = df[x_column_name].values.astype(int)
    ys = df[y_column_name].values.astype(float)
    missing_values_mask = np.isnan(ys)
    has_missing_values = missing_values_mask.any()
    has_enough_data_to_train_model = (~missing_values_mask).sum() >= min_data_points
    if has_missing_values and has_enough_data_to_train_model:
        # Train
        x_train = xs[~missing_values_mask]
        y_train = ys[~missing_values_mask]
        model.fit(x=x_train, y=y_train)

        # Predict
        x_pred = xs[missing_values_mask]
        y_pred = model.predict(x=x_pred)
        y_pred = y_pred.astype(df[y_column_name].dtype)

        # Fill missing values
        any_prediction_is_infinite = np.isinf(y_pred).any()
        if any_prediction_is_infinite:
            return df

        all_predictions_are_positive = (y_pred > 0).all()
        if all_predictions_are_positive:
            df.loc[missing_values_mask, y_column_name] = y_pred
        elif set_negatives_to_zero:
            y_pred[y_pred < 0] = 0
            df.loc[missing_values_mask, y_column_name] = y_pred
    return df


class ExponentialRegression(RegressionBase):
    def __init__(self, maxfev: int = 20_000):
        """
        Parameters
        ----------
        maxfev: int
            Maximum number of function calls to find an optimal parameters.
        """
        super().__init__()
        self.maxfev = maxfev
        self.model = lambda x, a, b: a * np.exp(b * x)
        self.parameters = None

    def fit(self, x, y):
        self.parameters = curve_fit(f=self.model, xdata=x, ydata=y, maxfev=self.maxfev)[0]

    def predict(self, x):
        return self.model(x, *self.parameters)


class PowerRegression(RegressionBase):
    def __init__(self, maxfev: int = 20_000):
        """
        Parameters
        ----------
        maxfev: int
            Maximum number of function calls to find an optimal parameters.
        """
        super().__init__()
        self.maxfev = maxfev
        self.model = lambda x, a, b: a * np.power(x, b)
        self.x_norm = lambda x: x / np.max(x) + 1
        self.parameters = None

    def fit(self, x, y):
        self.parameters = curve_fit(f=self.model, xdata=x, ydata=y, maxfev=self.maxfev)[0]

    def predict(self, x):
        return self.model(x, *self.parameters)


class PolynomialRegression(RegressionBase):
    def __init__(self, degree: int = 2):
        super().__init__()
        self.degree = degree

    def fit(self, x, y):
        self.model = np.poly1d(np.polyfit(x, y, deg=self.degree))

    def predict(self, x):
        return self.model(x)


class LinearRegression(RegressionBase):

    def __init__(self):
        super().__init__()
        self.model = SkLearnLinearRegression()

    def fit(self, x, y):
        x = x.reshape(-1, 1)
        y = y.reshape(-1, 1)
        self.model.fit(X=x, y=y)

    def predict(self, x):
        x = x.reshape(-1, 1)
        return self.model.predict(x).flatten()
