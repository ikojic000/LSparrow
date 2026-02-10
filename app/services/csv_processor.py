"""
CSV file processing service.
"""

from typing import Any, BinaryIO, Dict, List, Tuple, Optional

import pandas as pd

from app.services.statistics import StatisticsCalculator
from app.errors.exceptions import UnsupportedEncodingError, NoLikertDataError


class CSVProcessor:
    """
    Processor for CSV files containing survey data.
    """

    SUPPORTED_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1250", "cp1252"]

    def __init__(self):
        """Initialize the CSV processor."""
        self.stats_calculator = StatisticsCalculator()

    def detect_groupable_columns(self, file_content: BinaryIO) -> List[str]:
        """
        Detect non-Likert columns that can be used for grouping.

        A column is groupable if:
        - It is NOT a Likert scale column (1-5 values)
        - It is non-numeric or categorical
        - The dataset has more than one row
        - It is NOT a multi-select column (values containing ";")
        - It does NOT have approximately one unique value per row
          (e.g. IDs, timestamps, emails)

        A column is NOT excluded solely because it has only one unique value.

        Args:
            file_content: File-like object containing CSV data.

        Returns:
            List of column names suitable for grouping.
        """
        df = self._read_csv(file_content)

        if len(df) <= 1:
            return []

        likert_columns = set(self._find_likert_columns(df))

        groupable = []
        for col in df.columns:
            if col in likert_columns:
                continue

            if not self._is_categorical_column(df[col]):
                continue

            if self._is_multiselect_column(df[col]):
                continue

            if self._is_unique_per_row(df[col]):
                continue

            groupable.append(col)

        return groupable

    def _is_categorical_column(self, series: pd.Series) -> bool:
        """
        Check if a column is non-numeric / categorical.

        Returns True if the column's dtype is not numeric (object, category, bool, etc.).
        """
        return not pd.api.types.is_numeric_dtype(series)

    def _is_multiselect_column(self, series: pd.Series, threshold: float = 0.1) -> bool:
        """
        Check if a column contains multi-select values (separated by ";").

        A column is considered multi-select if more than `threshold` fraction
        of its non-null values contain a semicolon.
        """
        non_null = series.dropna().astype(str)
        if len(non_null) == 0:
            return False
        contains_semicolon = non_null.str.contains(";", na=False).sum()
        return (contains_semicolon / len(non_null)) > threshold

    def _is_unique_per_row(self, series: pd.Series, threshold: float = 0.9) -> bool:
        """
        Check if a column has approximately one unique value per row,
        indicating it is an ID-like column (timestamps, emails, etc.).

        Returns True if the ratio of unique values to total non-null values
        is >= `threshold`.
        """
        non_null = series.dropna()
        if len(non_null) == 0:
            return True
        n_unique = non_null.nunique()
        return (n_unique / len(non_null)) >= threshold

    def process(
        self,
        file_content: BinaryIO,
        selected_grouping_columns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Process uploaded CSV file and return statistics for Likert scale questions.

        Args:
            file_content: File-like object containing CSV data.
            selected_grouping_columns: List of column names to group by.
                If None or empty, only overall statistics are calculated.

        Returns:
            Dictionary containing overall statistics, grouped statistics, and grouping info.
        """
        df = self._read_csv(file_content)
        likert_columns = self._find_likert_columns(df)

        overall_results = self._calculate_overall_statistics(df, likert_columns)
        grouped_results, available_groupings = self._calculate_grouped_statistics(
            df, likert_columns, selected_grouping_columns or []
        )

        return {
            "overall": overall_results,
            "grouped": grouped_results,
            "groupings": available_groupings,
        }

    def _read_csv(self, file_content: BinaryIO) -> pd.DataFrame:
        """
        Read CSV file with automatic encoding detection.

        Args:
            file_content: File-like object containing CSV data.

        Returns:
            Pandas DataFrame with the CSV data.

        Raises:
            UnsupportedEncodingError: If the file cannot be read with any supported encoding.
        """
        for encoding in self.SUPPORTED_ENCODINGS:
            try:
                file_content.seek(0)
                return pd.read_csv(file_content, encoding=encoding)
            except Exception:
                continue

        raise UnsupportedEncodingError()

    def _find_likert_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Find columns containing Likert scale (1-5) data.

        Args:
            df: DataFrame to analyze.

        Returns:
            List of column names containing Likert scale data.
        """
        return [
            column
            for column in df.columns
            if self.stats_calculator.is_likert_column(df[column])
        ]

    def _calculate_overall_statistics(
        self, df: pd.DataFrame, likert_columns: List[str]
    ) -> List[Dict]:
        """
        Calculate statistics for all respondents.

        Args:
            df: DataFrame with survey data.
            likert_columns: List of columns to analyze.

        Returns:
            List of dictionaries containing statistics for each question.
        """
        results = []

        for column in likert_columns:
            numeric_col = pd.to_numeric(df[column], errors="coerce")
            stats_data = self.stats_calculator.calculate(numeric_col)

            if stats_data:
                results.append({"question": column, **stats_data})

        return results

    def _calculate_grouped_statistics(
        self,
        df: pd.DataFrame,
        likert_columns: List[str],
        selected_columns: List[str],
    ) -> Tuple[Dict, Dict]:
        """
        Calculate statistics grouped by selected columns.

        Args:
            df: DataFrame with survey data.
            likert_columns: List of columns to analyze.
            selected_columns: List of column names to group by.

        Returns:
            Tuple of (grouped_results, available_groupings) dictionaries.
        """
        grouped_results = {}
        available_groupings = {}

        for idx, col_name in enumerate(selected_columns):
            if col_name not in df.columns:
                continue

            unique_values = df[col_name].dropna().unique().tolist()

            if not unique_values:
                continue

            group_key = f"group_{idx}"

            available_groupings[group_key] = {
                "label": col_name,
                "column": col_name,
                "values": sorted(unique_values, key=str),
            }

            grouped_results[group_key] = self._calculate_group_statistics(
                df, col_name, unique_values, likert_columns
            )

        return grouped_results, available_groupings

    def _calculate_group_statistics(
        self,
        df: pd.DataFrame,
        group_col: str,
        unique_values: list,
        likert_columns: List[str],
    ) -> Dict:
        """
        Calculate statistics for each group value.

        Args:
            df: DataFrame with survey data.
            group_col: Column name to group by.
            unique_values: List of unique values in the group column.
            likert_columns: List of columns to analyze.

        Returns:
            Dictionary mapping group values to their statistics.
        """
        group_results = {}

        for value in unique_values:
            group_df = df[df[group_col] == value]
            group_stats = []

            for column in likert_columns:
                numeric_col = pd.to_numeric(group_df[column], errors="coerce")
                stats_data = self.stats_calculator.calculate(numeric_col)

                if stats_data:
                    group_stats.append({"question": column, **stats_data})

            if group_stats:
                group_results[value] = group_stats

        return group_results
