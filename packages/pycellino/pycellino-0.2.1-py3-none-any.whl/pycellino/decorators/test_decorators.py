import pandas as pd

from pycellino.decorators.main import support_groups


def test_support_groups_with_groupby():
    func = support_groups(lambda df: df.sum(numeric_only=True))

    data = [
        ['A', 1],
        ['A', 2],
        ['B', 3],
        ['B', 4],
    ]
    columns = ['CATEGORY', 'VALUE']
    input_df = pd.DataFrame(data=data, columns=columns)

    output_df = func(df=input_df, group_columns=['CATEGORY'])
    output_df = output_df.reset_index()

    data = [
        ['A', 3],
        ['B', 7],
    ]
    columns = ['CATEGORY', 'VALUE']
    expected_df = pd.DataFrame(data=data, columns=columns)

    pd.testing.assert_frame_equal(left=output_df, right=expected_df, check_like=True)
