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
    
    SUPPORTED_ENCODINGS = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1250', 'cp1252']
    
    def __init__(self, grouping_columns: dict, grouping_labels: dict):
        """
        Initialize the CSV processor.
        
        Args:
            grouping_columns: Mapping of group keys to column names.
            grouping_labels: Mapping of group keys to display labels.
        """
        self.grouping_columns = grouping_columns
        self.grouping_labels = grouping_labels
        self.stats_calculator = StatisticsCalculator()
    
    def process(self, file_content: BinaryIO) -> Dict[str, Any]:
        """
        Process uploaded CSV file and return statistics for Likert scale questions.
        
        Args:
            file_content: File-like object containing CSV data.
            
        Returns:
            Dictionary containing overall statistics, grouped statistics, and grouping info.
            
        Raises:
            ValueError: If the CSV file cannot be read with any supported encoding.
        """
        df = self._read_csv(file_content)
        likert_columns = self._find_likert_columns(df)
        
        overall_results = self._calculate_overall_statistics(df, likert_columns)
        grouped_results, available_groupings = self._calculate_grouped_statistics(
            df, likert_columns
        )
        
        return {
            'overall': overall_results,
            'grouped': grouped_results,
            'groupings': available_groupings
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
            column for column in df.columns
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
            numeric_col = pd.to_numeric(df[column], errors='coerce')
            stats_data = self.stats_calculator.calculate(numeric_col)
            
            if stats_data:
                results.append({
                    'question': column,
                    **stats_data
                })
        
        return results
    
    def _calculate_grouped_statistics(
        self, df: pd.DataFrame, likert_columns: List[str]
    ) -> Tuple[Dict, Dict]:
        """
        Calculate statistics grouped by demographic columns.
        
        Args:
            df: DataFrame with survey data.
            likert_columns: List of columns to analyze.
            
        Returns:
            Tuple of (grouped_results, available_groupings) dictionaries.
        """
        grouped_results = {}
        available_groupings = {}
        
        for group_key, group_col in self.grouping_columns.items():
            if group_col not in df.columns:
                continue
                
            unique_values = df[group_col].dropna().unique().tolist()
            
            if not unique_values:
                continue
            
            available_groupings[group_key] = {
                'label': self.grouping_labels[group_key],
                'column': group_col,
                'values': sorted(unique_values)
            }
            
            grouped_results[group_key] = self._calculate_group_statistics(
                df, group_col, unique_values, likert_columns
            )
        
        return grouped_results, available_groupings
    
    def _calculate_group_statistics(
        self,
        df: pd.DataFrame,
        group_col: str,
        unique_values: list,
        likert_columns: List[str]
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
                numeric_col = pd.to_numeric(group_df[column], errors='coerce')
                stats_data = self.stats_calculator.calculate(numeric_col)
                
                if stats_data:
                    group_stats.append({
                        'question': column,
                        **stats_data
                    })
            
            if group_stats:
                group_results[value] = group_stats
        
        return group_results
