"""module contains Data Duplicates check."""
from typing import Union, Iterable

import pandas as pd

from deepchecks import Dataset, ensure_dataframe_type
from deepchecks.base.check import CheckResult, SingleDatasetBaseCheck
from deepchecks.base.dataframe_utils import filter_columns_with_validation
from deepchecks.utils import DeepchecksValueError
from deepchecks.string_utils import format_percent


__all__ = ['DataDuplicates']


class DataDuplicates(SingleDatasetBaseCheck):
    """Search for duplicate data in dataset."""

    def __init__(self, columns: Union[str, Iterable[str]] = None, ignore_columns: Union[str, Iterable[str]] = None,
                 n_to_show: int = 5):
        """Initialize the DataDuplicates class.

        Args:
            columns (str, Iterable[str]): List of columns to check, if none given checks all columns Except ignored
              ones.
            ignore_columns (str, Iterable[str]): List of columns to ignore, if none given checks based on columns
              variable.
            n_to_show (int): number of most common duplicated samples to show.
        """
        super().__init__()
        self.columns = columns
        self.ignore_columns = ignore_columns
        self.n_to_show = n_to_show

    def run(self, dataset: Dataset, model=None) -> CheckResult:
        """Run check.

        Args:
            dataset(Dataset): any dataset.

        Returns:
            (CheckResult): percentage of duplicates and display of the top n_to_show most duplicated.
        """
        df: pd.DataFrame = ensure_dataframe_type(dataset)
        df = filter_columns_with_validation(df, self.columns, self.ignore_columns)

        data_columns = list(df.columns)

        n_samples = df.shape[0]

        if n_samples == 0:
            raise DeepchecksValueError('Dataset does not contain any data')

        group_unique_data = df[data_columns].groupby(data_columns, dropna=False).size()
        n_unique = len(group_unique_data)

        percent_duplicate = 1 - (1.0 * int(n_unique)) / (1.0 * int(n_samples))

        if percent_duplicate > 0:
            duplicates_counted = group_unique_data.reset_index().rename(columns={0: 'Number of Duplicates'})
            most_duplicates = duplicates_counted[duplicates_counted['Number of Duplicates'] > 1]. \
                nlargest(self.n_to_show, ['Number of Duplicates'])

            most_duplicates = most_duplicates.set_index('Number of Duplicates')

            text = f'{format_percent(percent_duplicate)} of data samples are duplicates'
            display = [text, most_duplicates]
        else:
            display = None

        return CheckResult(value=percent_duplicate, check=self.__class__, display=display)