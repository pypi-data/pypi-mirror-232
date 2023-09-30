# IdentifyOutliers

A Python package for efficient scaling and outlier handling of pandas DataFrames using the standard scaler approach, .

`IdentifyOutliers` is designed to provide a seamless experience in preprocessing pandas DataFrames by ensuring data normalization and outlier handling in one step.

## Features

- **Data Scaling**: Utilizes the standard scaler method for data normalization.
- **Outlier Detection**: Provides an option to set a z-score threshold for outlier detection.
- **Multiple Outputs**: Returns the original data, the scaled data without outliers, a separate DataFrame for detected outliers, and scaled outliers.

## Installation

Install the package using pip:

```bash
pip install IdentifyOutliers
```

## Usage

```python
import pandas as pd
from IdentifyOutliers import CustomZscoreScaler

# Sample DataFrame
data = {
    'A': [1, 2, 3, 100, 5],
    'B': [5, 6, 7, 8, 500]
}
df = pd.DataFrame(data)

# Initialize the scaler with a z-score threshold (default is 3.0)
scaler = CustomZscoreScaler(threshold=3.0)

# Transform the data
df_no_outliers, df_scaled_no_outliers, df_outliers, df_scaled_outliers = scaler.transform(df)

# Print the results
print(df_no_outliers)
#    A  B
# 0  1  5
# 1  2  6
# 2  3  7

print(df_scaled_no_outliers)
#           A         B
# 0 -0.544672 -0.507592
# 1 -0.518980 -0.502526
# 2 -0.493288 -0.497461

print(df_outliers)
#      A    B
# 3  100    8
# 4    5  500

print(df_outliers)
#      A    B
# 3  100    8
# 4    5  500

print(df_scaled_outliers)
#           A         B
# 3  1.998845 -0.492395
# 4 -0.441904  1.999974

```

## Parameters

threshold: The z-score threshold for outlier detection. Data points exceeding threshold standard deviations away from the mean are considered outliers. The default value is 3.0.


## Contributions

Contributions are welcome! Please create an issue or submit a pull request.

## License

This project is licensed under the [MIT License] (https://github.com/amithpdn/IdentifyOutliers/blob/master/LICENSE.TXT).