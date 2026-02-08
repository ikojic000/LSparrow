"""
Statistical calculations service.
"""

from typing import Optional, Dict, Any
import warnings

import numpy as np
from scipy import stats


class StatisticsCalculator:
    """
    Calculator for descriptive statistics on Likert scale data.
    """

    @staticmethod
    def calculate(data) -> Optional[Dict[str, Any]]:
        """
        Calculate statistics for a series of 1-5 scale responses.

        Args:
            data: Pandas Series or array-like containing numeric responses.

        Returns:
            Dictionary containing statistical measures, or None if no valid data.
        """
        # Filter only valid 1-5 values
        valid_data = data[(data >= 1) & (data <= 5)].dropna()

        if len(valid_data) == 0:
            return None

        n = len(valid_data)
        mean = np.mean(valid_data)
        std = np.std(valid_data, ddof=1)  # Sample standard deviation
        median = np.median(valid_data)

        # Skewness and Kurtosis - handle low variance cases
        skewness = np.nan
        kurtosis = np.nan

        if n >= 3 and std > 1e-10:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                skewness = stats.skew(valid_data)
                if not np.isfinite(skewness):
                    skewness = np.nan

        if n >= 4 and std > 1e-10:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                kurtosis = stats.kurtosis(valid_data)
                if not np.isfinite(kurtosis):
                    kurtosis = np.nan

        # Kolmogorov-Smirnov test for normality
        ks_statistic, ks_pvalue = np.nan, np.nan
        if n >= 5 and std > 1e-10:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                ks_statistic, ks_pvalue = stats.kstest(
                    valid_data, "norm", args=(mean, std)
                )
                if not np.isfinite(ks_statistic):
                    ks_statistic, ks_pvalue = np.nan, np.nan

        return {
            "N": n,
            "AS": round(mean, 3),
            "SD": round(std, 3),
            "Median": round(median, 3),
            "Ske": round(skewness, 3) if np.isfinite(skewness) else "-",
            "Kur": round(kurtosis, 3) if np.isfinite(kurtosis) else "-",
            "Max D": round(ks_statistic, 3) if np.isfinite(ks_statistic) else "-",
            "K-S p": round(ks_pvalue, 3) if np.isfinite(ks_pvalue) else "-",
        }

    @staticmethod
    def is_likert_column(series) -> bool:
        """
        Check if a column contains 1-5 scale responses.

        Args:
            series: Pandas Series to check.

        Returns:
            True if the series contains only values between 1 and 5.
        """
        try:
            import pandas as pd

            numeric_series = pd.to_numeric(series, errors="coerce")
            valid_values = numeric_series.dropna()

            if len(valid_values) == 0:
                return False

            # Check if all values are between 1 and 5
            unique_values = valid_values.unique()
            return all(1 <= v <= 5 for v in unique_values) and len(unique_values) <= 5
        except Exception:
            return False
