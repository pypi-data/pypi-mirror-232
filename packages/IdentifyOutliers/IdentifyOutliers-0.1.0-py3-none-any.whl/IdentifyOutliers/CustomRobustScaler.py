import pandas as pd
from sklearn.preprocessing import RobustScaler
import numpy as np

class CustomRobustScaler:
    """
    CustomRobustScaler provides a combined functionality of scaling data using the
    robust scaler approach while also removing outliers based on the Modified Z-Score.

    The class offers a flexible mechanism to preprocess pandas DataFrames,
    ensuring data normalization and outlier handling.

    Attributes:
    threshold (float): The Modified Z-Score threshold for identifying outliers.
    mad_multiplier (float): The MAD multiplier for identifying outliers based on modified Z-scores. The default is 0.6745.
    
    scaler (RobustScaler): The scaler object for normalization.

    Example:
        scaler = CustomRobustScaler(threshold=3.5)
        df_no_outliers, df_scaled_no_outliers, df_outliers, df_scaled_outliers = scaler.transform(df)
    """

    def __init__(self, threshold=3.5, mad_multiplier=0.6745):
        """
        Initializes the CustomRobustScaler with a Modified Z-Score threshold for outlier detection.
        Args:
            threshold (float): The threshold for identifying outliers based on Modified Z-Score.
                               The default is 3.5, which is a common threshold for Modified Z-Score.
            mad_multiplier (float): The MAD multiplier for identifying outliers based on Modified Z-Score. The default is 0.6745.
        """
        # Initialize the scaler and threshold
        self.scaler = RobustScaler()
        self.threshold = threshold
        self.mad_multiplier = mad_multiplier


    def transform(self, df):
        """
        Applies scaling to the input DataFrame and separates outliers based on the defined threshold.

        The function returns four DataFrames:
        1. The original data without detected outliers.
        2. The scaled data (using RobustScaler) without detected outliers.
        3. The original outliers detected based on Modified Z-Score.
        4. The scaled outliers detected based on Modified Z-Score.

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
        scaled_df = pd.DataFrame(scaled_data, columns=df.columns)

        # Compute Modified Z-Score
        median = df.median()
        mad = (df - median).abs().median()

        # Calculate the modified Z-score
        modified_z_score = self.mad_multiplier * (df - median) / mad

        # Identify outliers
        is_outlier = (modified_z_score.abs() > self.threshold).any(axis=1)

        # Return the original and scaled data without outliers, and outliers
        return df[~is_outlier], scaled_df[~is_outlier], df[is_outlier], scaled_df[is_outlier]

