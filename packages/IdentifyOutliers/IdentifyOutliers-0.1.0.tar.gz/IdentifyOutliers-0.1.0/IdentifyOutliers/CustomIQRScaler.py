import pandas as pd
from sklearn.preprocessing import MinMaxScaler

class CustomIQRScaler:
    """
    CustomIQRScaler provides a combined functionality of scaling data using the
    Min-Max scaler approach while also removing outliers based on the Interquartile Range (IQR).

    The class offers a flexible mechanism to preprocess pandas DataFrames,
    ensuring data normalization and outlier handling.

    Attributes:
    lower_bound (float): Multiplier applied to Interquartile Range (IQR) for identifying lower bound. The default value is 1.5 or Q1 - 1.5*IRQ.
    upper_bound (float): Multiplier applied to Interquartile Range (IQR) for identifying upper bound. The default value is 1.5 or Q3 + 1.5*IRQ.
    scaler (MinMaxScaler): The scaler object for normalization.

    Example:
        scaler = CustomIQRScaler()
        
        df_no_outliers, df_scaled_no_outliers, df_outliers, df_scaled_outliers = scaler.transform(df)
    """

    def __init__(self, lower_bound=1.5, upper_bound=1.5):
        """
        Initializes the CustomIQRScaler.
        """
        # Initialize the scaler and thresholds
        self.scaler = MinMaxScaler()
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


    def transform(self, df):
        """
        Applies scaling to the input DataFrame and separates outliers based on IQR.

        The function returns four DataFrames:
        1. The original data without detected outliers.
        2. The scaled data (using MinMaxScaler) without detected outliers.
        3. The original outliers detected based on IQR.
        4. The scaled outliers detected based on IQR.

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

        # Calculate the IQR for each column in the DataFrame
        Q1 = df.quantile(0.25)
        Q3 = df.quantile(0.75)
        IQR = Q3 - Q1

        # Determine bounds for outlier detection
        lower_threshold = Q1 - self.lower_bound * IQR
        upper_threshold = Q3 + self.upper_bound * IQR

        # Identify outliers
        is_outlier = (df < lower_threshold) | (df > upper_threshold)

        # Return the original and scaled data without outliers, and outliers
        return df[~is_outlier.any(axis=1)], scaled_df[~is_outlier.any(axis=1)], df[is_outlier.any(axis=1)], scaled_df[is_outlier.any(axis=1)]
