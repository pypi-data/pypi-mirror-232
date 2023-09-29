import numpy as np
import pandas as pd

from pycellino.imputation.main import (
    ExponentialRegression, LinearRegression, PolynomialRegression,
    PowerRegression)


def test_polynomial_regression():
    data = [
        [0, 0.0],
        [1, 1.0],
        [2, 4.0],
        [3, np.nan],
        [4, np.nan],
        [5, 25.0],
    ]
    columns = ['X', 'Y']
    input_df = pd.DataFrame(data=data, columns=columns)

    regression = PolynomialRegression(degree=2)
    output_df = regression.fill(
        df=input_df,
        x_column_name='X',
        y_column_name='Y',
        min_data_points=4)

    data = [
        [0, 0.0],
        [1, 1.0],
        [2, 4.0],
        [3, 9.0],
        [4, 16.0],
        [5, 25.0],
    ]
    columns = ['X', 'Y']
    expected_df = pd.DataFrame(data=data, columns=columns)

    pd.testing.assert_frame_equal(left=output_df, right=expected_df, check_like=True)


def test_linear_regression():
    data = [
        [0, 0.0],
        [1, 1.0],
        [2, 2.0],
        [3, np.nan],
        [4, np.nan],
        [5, 5.0],
    ]
    columns = ['X', 'Y']
    input_df = pd.DataFrame(data=data, columns=columns)

    regression = LinearRegression()
    output_df = regression.fill(
        df=input_df,
        x_column_name='X',
        y_column_name='Y',
        min_data_points=4)

    data = [
        [0, 0.0],
        [1, 1.0],
        [2, 2.0],
        [3, 3.0],
        [4, 4.0],
        [5, 5.0],
    ]
    columns = ['X', 'Y']
    expected_df = pd.DataFrame(data=data, columns=columns)

    pd.testing.assert_frame_equal(left=output_df, right=expected_df, check_like=True)


def test_power_regression():
    data = [
        [0, 0.0],
        [1, 1.0],
        [2, 8.0],
        [3, np.nan],
        [4, np.nan],
        [5, 125.0],
    ]
    columns = ['X', 'Y']
    input_df = pd.DataFrame(data=data, columns=columns)

    regression = PowerRegression()
    output_df = regression.fill(
        df=input_df,
        x_column_name='X',
        y_column_name='Y',
        min_data_points=4)

    data = [
        [0, 0.0],
        [1, 1.0],
        [2, 8.0],
        [3, 27.0],
        [4, 64.0],
        [5, 125.0],
    ]
    columns = ['X', 'Y']
    expected_df = pd.DataFrame(data=data, columns=columns)

    pd.testing.assert_frame_equal(left=output_df, right=expected_df, check_like=True)


def test_exponential_regression():
    data = [
        [0, np.exp(0)],
        [1, np.exp(1)],
        [2, np.exp(2)],
        [3, np.nan],
        [4, np.nan],
        [5, np.exp(5)],
    ]
    columns = ['X', 'Y']
    input_df = pd.DataFrame(data=data, columns=columns)

    regression = ExponentialRegression()
    output_df = regression.fill(
        df=input_df,
        x_column_name='X',
        y_column_name='Y',
        min_data_points=4)

    data = [
        [0, np.exp(0)],
        [1, np.exp(1)],
        [2, np.exp(2)],
        [3, np.exp(3)],
        [4, np.exp(4)],
        [5, np.exp(5)],
    ]
    columns = ['X', 'Y']
    expected_df = pd.DataFrame(data=data, columns=columns)

    pd.testing.assert_frame_equal(left=output_df, right=expected_df, check_like=True)


def test_exponential_regression_groups():
    data = [
        ['A', 0, np.exp(0)],
        ['A', 1, np.exp(1)],
        ['A', 2, np.exp(2)],
        ['A', 3, np.nan],
        ['A', 4, np.nan],
        ['A', 5, np.exp(5)],
    ]
    columns = ['CATEGORY', 'X', 'Y']
    input_df = pd.DataFrame(data=data, columns=columns)

    regression = ExponentialRegression()
    output_df = regression.fill(
        df=input_df,
        x_column_name='X',
        y_column_name='Y',
        min_data_points=4,
        group_columns=['CATEGORY'])

    data = [
        ['A', 0, np.exp(0)],
        ['A', 1, np.exp(1)],
        ['A', 2, np.exp(2)],
        ['A', 3, np.exp(3)],
        ['A', 4, np.exp(4)],
        ['A', 5, np.exp(5)],
    ]
    columns = ['CATEGORY', 'X', 'Y']
    expected_df = pd.DataFrame(data=data, columns=columns)

    pd.testing.assert_frame_equal(left=output_df, right=expected_df, check_like=True)
