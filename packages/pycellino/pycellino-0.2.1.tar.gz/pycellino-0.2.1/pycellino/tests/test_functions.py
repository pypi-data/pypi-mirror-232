import pandas as pd

from pycellino.functions import group_feature_values


def test_group_feature_values():
    data = [
        ['A1', 'B1', 1],
        ['A1', 'B1', 2],
        ['A1', 'B2', 3],
        ['A2', 'B1', 1],
        ['A2', 'B3', 2],
        ['A2', 'B3', 3],
    ]
    columns = ['CATEGORY_A', 'CATEGORY_B', 'VALUE']
    input_df = pd.DataFrame(data=data, columns=columns)

    feature_groups = {
        'BX': ['B1', 'B2'],
        'BY': ['B3']
    }
    output_df = group_feature_values(
        df=input_df,
        index=['CATEGORY_A'],
        feature_name='CATEGORY_B',
        feature_groups=feature_groups)

    columns = ['CATEGORY_A', 'CATEGORY_B', 'VALUE']
    data = [
        ['A1', 'BX', 6],
        ['A2', 'BX', 1],
        ['A2', 'BY', 5],
    ]
    expected_df = pd.DataFrame(data=data, columns=columns)
    pd.testing.assert_frame_equal(left=output_df, right=expected_df, check_like=True)
