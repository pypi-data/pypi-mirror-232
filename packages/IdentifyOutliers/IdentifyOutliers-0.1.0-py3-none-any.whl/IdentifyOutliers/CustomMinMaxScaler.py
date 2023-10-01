import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np

class CustomMinMaxScaler:
    """
    CustomMinMaxScaler provides a combined functionality of scaling data using the
    Min-Max scaler approach while also removing outliers based on a defined lower 
    and upper bound.

    The class offers a flexible mechanism to preprocess pandas DataFrames,
    ensuring data normalization and outlier handling.

    Attributes:
        lower_bound (float): Lower bound percentile for identifying outliers. The default value is 0.05.
        upper_bound (float): Upper bound percentile for identifying outliers. The default value is 0.95.
        scaler (MinMaxScaler): The scaler object for normalization.

    Example:
        scaler = CustomMinMaxScaler(lower_bound=0.05, upper_bound=0.95)
        df_no_outliers, df_scaled_no_outliers, df_outliers, df_scaled_outliers = scaler.transform(df)
    """

    def __init__(self, lower_bound=0.05, upper_bound=0.95):
        """
        Initializes the CustomMinMaxScaler with lower and upper bound percentiles for outlier detection.

        Args:
            lower_bound (float): The lower percentile bound for identifying outliers.
            upper_bound (float): The upper percentile bound for identifying outliers.
        """
        # Initialize the scaler and thresholds
        self.scaler = MinMaxScaler()
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def transform(self, df):
        """
        Applies scaling to the input DataFrame and separates outliers based on the defined bounds.

        The function returns four DataFrames:
        1. The original data without detected outliers.
        2. The scaled data (using MinMaxScaler) without detected outliers.
        3. The original outliers detected based on bounds.
        4. The scaled outliers detected based on bounds.

        Args:
            df (DataFrame): Input pandas DataFrame to be transformed.

        Returns:
            DataFrame: Original data without outliers.
            DataFrame: Scaled data without outliers.
            DataFrame: Original outliers data.
            DataFrame: Scaled outliers data.
        """
        # Scale data
        scaled_data = self.scaler.fit_transform(df)

        # Create a DataFrame with the scaled data
        scaled_df = pd.DataFrame(scaled_data, columns=df.columns)

        # Determine bounds for outlier detection
        lower_threshold = scaled_df.quantile(self.lower_bound)
        upper_threshold = scaled_df.quantile(self.upper_bound)

        # Identify outliers
        is_outlier = (scaled_df < lower_threshold) | (scaled_df > upper_threshold)

        # Return the original and scaled data without outliers, and outliers
        return df[~is_outlier.any(axis=1)], scaled_df[~is_outlier.any(axis=1)], df[is_outlier.any(axis=1)], scaled_df[is_outlier.any(axis=1)]
