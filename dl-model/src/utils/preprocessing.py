import pandas as pd
import numpy as np
import pytz
from datetime import datetime


# This function executes preprocessing steps as described in our chosen paper (Tzortzis et al.)
def preprocess_country_data(data, country_name):
    print(f"Starting preprocessing for {country_name}")
    df = pd.DataFrame(data)
    print(f"Initial shape: {df.shape}")

    df['prediction'] = pd.to_numeric(df['prediction'], errors='coerce')
    df['actual'] = pd.to_numeric(df['actual'], errors='coerce')

    # 1. Remove duplicates
    df = df.drop_duplicates()
    print(f"Shape after removing duplicates: {df.shape}")

    # 2. Remove outliers
    valid_data = detect_outliers_monthly(df)
    df = df[valid_data]
    print(f"Shape after removing outliers: {df.shape}")

    # 3. Convert timestamps to local timezone and sort
    df['timestamp'] = df['time'].apply(
        lambda x: convert_timestamp(x, country_name))
    df = df.sort_values('timestamp')

    df.set_index('timestamp', inplace=True)

    if not df.index.is_unique:
        df = df.groupby(df.index).first()

    # We resample in order to get hourly stamps for every country data
    numeric_columns = ['actual', 'prediction']
    df_numeric = df[numeric_columns].resample('h').mean()

    non_numeric_columns = df.drop(columns=numeric_columns)
    df_non_numeric = non_numeric_columns.resample('h').ffill()

    df = pd.concat([df_numeric, df_non_numeric], axis=1)

    print(f"Timestamps resampled to hourly intervals.")

    # 4. Hybrid imputation for missing values
    df['actual'] = hybrid_interpolation(df['actual'])
    df['prediction'] = hybrid_interpolation(df['prediction'])

    print(f"Final shape after hybrid imputation: {df.shape}")
    return df


def detect_outliers_monthly(df, timestamp_col='time'):
    valid_data = np.zeros(len(df), dtype=bool)

    months = df[timestamp_col].apply(
        lambda x: x.split('.')[1] + '-' + x.split('.')[2][:4])

    # Process each month separately
    for month_year in months.unique():
        current_month = months == month_year
        month_data = df.loc[current_month, 'actual']

        mean = month_data.mean()
        std = month_data.std()
        threshold = 4.5 * std

        month_outliers = np.abs(month_data - mean) > threshold
        valid_data[current_month] = month_outliers

    return ~valid_data


# Function for step 3, converting to local times of each country
def convert_timestamp(time_str, country_name):
    start_time = time_str.split(" - ")[0]
    dt = datetime.strptime(start_time, "%d.%m.%Y %H:%M")

    timezone_map = {
        'Lithuania_23': 'Europe/Vilnius',
        'Lithuania_24': 'Europe/Vilnius',
        'Netherlands_23': 'Europe/Amsterdam',
        'Netherlands_24': 'Europe/Amsterdam',
        'Germany_23': 'Europe/Berlin',
        'Germany_24': 'Europe/Berlin',
        'Finland_23': 'Europe/Helsinki',
        'Finland_24': 'Europe/Helsinki',
        'Austria_23': 'Europe/Vienna',
        'Austria_24': 'Europe/Vienna',
        'Poland_23': 'Europe/Warsaw',
        'Poland_24': 'Europe/Warsaw',
        'Sweden_23': 'Europe/Stockholm',
        'Sweden_24': 'Europe/Stockholm',
        'Hungary_23': 'Europe/Budapest',
        'Hungary_24': 'Europe/Budapest'
    }

    # We use pytz for local timezones
    local_timezone = pytz.timezone(timezone_map[country_name])
    return pytz.utc.localize(dt).astimezone(local_timezone)


# Function for step 4, computes according to the formula given in the paper
def hybrid_interpolation(series, alpha=0.3):
    missing_idx = series.isna()
    if not missing_idx.any():
        return series

    result = series.copy()

    for idx in missing_idx.index[missing_idx]:
        previous_idx = series[:idx].last_valid_index()
        next_idx = series[idx:].first_valid_index()

        if previous_idx is None or next_idx is None:
            continue

        previous_hours = previous_idx.timestamp() / 3600
        next_hours = next_idx.timestamp() / 3600
        current_hours = idx.timestamp() / 3600

        L = np.interp([current_hours], [previous_hours, next_hours],
                      [series[previous_idx], series[next_idx]])[0]

        # We use same hour and day of week from historical data
        historical_values = series[
            (series.index.hour == idx.hour) &
            (series.index.dayofweek == idx.dayofweek)
            ].dropna()

        if len(historical_values) == 0:
            result[idx] = L
            continue

        H = historical_values.mean()

        d_i = min(abs((idx - previous_idx).total_seconds() / 3600),
                  abs((next_idx - idx).total_seconds() / 3600))
        w = np.exp(-alpha * d_i)

        result[idx] = w * L + (1 - w) * H

    return result


# Function to do preprocessing steps on all country datasets
def preprocess_all(datasets):
    countries = ['Lithuania_24', 'Lithuania_23', 'Netherlands_24', 'Netherlands_23', 'Germany_24', 'Germany_23', 'Finland_24', 'Finland_23', 'Austria_24', 'Austria_23',
                 'Poland_24', 'Poland_23', 'Sweden_24', 'Sweden_23', 'Hungary_24', 'Hungary_23']
    processed_data = []

    for country, data in zip(countries, datasets):
        print(f"\nPreprocessing {country}...")
        df = preprocess_country_data(data, country)
        processed_data.append(df)
        print(f"Preprocessing done for {country}, shape: {df.shape}")

    return processed_data

# Function to create sliding window of size window_size and prediction prediction_size
def create_sliding_windows(data, window_size=168, prediction_horizon=24):
    input_data = []
    output_data = []
    for i in range(len(data) - (window_size + prediction_horizon + 1)):
        # Windows from current index to index + window_size
        input_window = data[i:i + window_size]
        # Output window from index + window_size to index + window_size + prediction_horizon
        output_window = data[i + window_size:i + window_size + prediction_horizon]
        input_data.append(input_window)
        output_data.append(output_window)
    
    return input_data, output_data

import numpy as np

def get_window(data, target_country_index, i, window_size, prediction_horizon):
    # Flatten all country data except the target
    input_window = np.concatenate([
        data[country][i:i + window_size]
        for country in range(len(data)) if country != target_country_index
    ])

    out_layer = data[target_country_index][i + window_size:i + window_size + prediction_horizon]

    return input_window, out_layer

# Create sliding windows for multiple countries
def create_multi_country_windows(data, window_size=168, prediction_horizon=24, target_country_index=0):
    input_data = []
    output_data = []
    for i in range(len(data[0]) - window_size - prediction_horizon + 1):
        # Flatten all country data except the target
        input_window, out_layer = get_window(data, target_country_index, i, window_size, prediction_horizon)
        input_data.append(input_window)
        output_data.append(out_layer)
    
    return np.array(input_data), np.array(output_data)
