import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np


class CustomZscoreScaler:
    """
    CustomZscoreScaler provides a combined functionality of scaling data using the
    standard scaler approach while also removing outliers based on a z-score
    threshold.

    The class offers a flexible mechanism to preprocess pandas DataFrames,
    ensuring data normalization and outlier handling.

    Attributes:
    threshold (float): The z-score threshold for identifying outliers.
    scaler (StandardScaler): The scaler object for normalization.

    Example:
        scaler = CustomZscoreScaler(threshold=3.0)
        
        df_no_outliers, df_scaled_no_outliers, df_outliers, df_scaled_outliers = scaler.transform(df)
    """

    def __init__(self, threshold=3.0):
        """
        Initializes the CustomZscoreScaler with a z-score threshold for outlier detection.

        Args:
            threshold (float): The threshold for identifying outliers based on z-scores.
                               The default is 3.0, indicating data points 3 standard deviations
                               away from the mean are considered outliers.
        """
        # Initialize the scaler and threshold
        self.scaler = StandardScaler()
        self.threshold = threshold

    def transform(self, df):
        """
        Applies scaling to the input DataFrame and separates outliers based on the defined threshold.

        The function returns four DataFrames:
        1. The original data without detected outliers.
        2. The scaled data (using StandardScaler) without detected outliers.
        3. The original outliers detected based on z-scores.
        4. The scaled outliers detected based on z-scores.

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

        # Identify outliers
        is_outlier = (np.abs(scaled_df) > self.threshold).any(axis=1)

        # Return the original and scaled data without outliers, and outliers
        return df[~is_outlier], scaled_df[~is_outlier], df[is_outlier], scaled_df[is_outlier]
