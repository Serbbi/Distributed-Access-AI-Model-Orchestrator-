# This is code written by Aras S4694996 for the deep learning course. It has been adapted for use in the Scalable Computing course.

from utils.load_data import load_data
from utils.preprocessing import preprocess_all, create_sliding_windows, create_multi_country_windows
from utils.model import train_model, MLPTimeSeriesModel, get_mape
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
import os

# This loads the data for each country directly from the files.
# Each data point contains the following information: time, predicted and actual.
# data_lithuania, data_netherlands, data_germany, data_finland, data_austria, data_poland, data_sweden, data_hungary = load_data()
datasets = load_data()

# Preprocessing data
print("Preprocessing data...")
processed_data = preprocess_all(datasets)
# Returned in preprocessing order:
# Lithuania, Netherlands, Germany, Finland, Austria, Poland, Sweden, Hungary
print("Preprocessing complete.")

# Dictionary mapping indices to countries
countries = {
    0: "Lithuania",
    2: "Netherlands",
    4: "Germany",
    6: "Finland",
    8: "Austria",
    10: "Poland",
    12: "Sweden",
    14: "Hungary"
}

# Used to reverse the look up if needed.
country_to_index = {country: index for index, country in countries.items()}

# This is the data for every country from given year.
# Start at 0 to exclude 2023 data and 1 for to exclude 2024 data.
# We skip by 2 to jump past the 2024-2025 data.
def get_data(data, start = 1):
    ctrs = [
        data[i]["actual"] for i in range(start, len(data), 2)
    ]
    return ctrs

# Will use 2023 data for all countries except target to train the initial model
def create_and_train_all_but_one_model(country, data):
    hidden_layers = [128, 64]
    dropout_rate = 0.1
    output_size = 24
    batch_size = 32

    target = int(country_to_index[country] / 2)

    # Get all country data
    countries_23 = get_data(data)
    # Create windows for all except target country
    input, output = create_multi_country_windows(countries_23, target_country_index=target)

    # Batch data
    inputs_tensor = torch.tensor(input, dtype=torch.float32)
    outputs_tensor = torch.tensor(output, dtype=torch.float32)

    dataset = TensorDataset(inputs_tensor, outputs_tensor)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize the model
    model = MLPTimeSeriesModel(countries=7, window=168, hidden_layers=hidden_layers, output_size=output_size, dropout_rate=dropout_rate)
    train_model(model, dataloader)
    weights = model.save_weights()

    return model, weights

def create_and_train_model_for_target_with_tf(country, weights, data):
    target = int(country_to_index[country] / 2)

    countries_23 = get_data(data)

    # Ensure that the difference in input size is correct for the transfer learning model
    weights["model.0.weight"] = weights["model.0.weight"][:, :168]

    tf_model = MLPTimeSeriesModel(
        countries=1,
        window=168,
        hidden_layers=[128, 64],
        output_size=24,
        dropout_rate=0.1
    )

    # Use weights from previous model
    tf_model.load_state_dict(weights, strict=False)

    # Use the country that was left out to train again.
    input_data, output_data = create_sliding_windows(countries_23[target])

    inputs_tensor = torch.tensor(input_data, dtype=torch.float32)
    outputs_tensor = torch.tensor(output_data, dtype=torch.float32)

    dataset = TensorDataset(inputs_tensor, outputs_tensor)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    # train preinitialized model on new data.
    train_model(tf_model, dataloader)

    return tf_model

# Create output directory if it doesn't exist
output_dir = "../output"
os.makedirs(output_dir, exist_ok=True)

plt.figure(figsize=(20, 30))

# Store all weights for future use.
pretrained_weights = []

# get all countries by year.
countries_23 = get_data(processed_data)
countries_24 = get_data(processed_data, start=0)

for idx, (index, country_name) in enumerate(countries.items()):
    model, weights = create_and_train_all_but_one_model(country_name, processed_data)
    
    # Get the data for the first day of 2024
    countries_24_first_day = [
        processed_data[i]["actual"][-168:] for i in range(0, len(processed_data), 2)
    ]
    countries_excluding_target = [data for i, data in enumerate(countries_24_first_day) if i != idx]

    test_input = np.concatenate(countries_excluding_target)
    test_input_tensor = torch.tensor(test_input, dtype=torch.float32).unsqueeze(0)
    
    # Predict the next 24 hours
    prediction = model.predict(test_input_tensor)[0]
    
    # Actual values
    actual_values = countries_24[idx]

    plt.subplot(8, 1, idx + 1)
    plt.plot(actual_values.values[:24], label="actual")
    plt.plot(prediction, label="prediction", color='red')
    plt.title(f"Actual vs Prediction - {country_name}")
    plt.xlabel("Time of Day in Hours")
    plt.ylabel("Electricity Consumption in MW")
    plt.legend()

    mape = get_mape(actual_values.values[:24], prediction)
    pretrained_weights.append(model.save_weights())
    print(f"{country_name} MAPE: {mape}")

# Save figure instead of showing
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "initial_predictions.png"))
plt.close()  # Closes the figure to prevent memory leaks

plt.figure(figsize=(20, 30))

for idx, (index, country_name) in enumerate(countries.items()):
    weight = pretrained_weights[idx]
    weight["model.0.weight"] = weight["model.0.weight"][:, :168]
    
    tf_model = MLPTimeSeriesModel(
        countries=1,
        window=168,
        hidden_layers=[128, 64],
        output_size=24,
        dropout_rate=0.1
    )
    
    tf_model.load_state_dict(weight, strict=False)
    
    country_23 = countries_23[idx]
    input_data, output_data = create_sliding_windows(country_23)
    
    inputs_tensor = torch.tensor(np.array(input_data), dtype=torch.float32)
    outputs_tensor = torch.tensor(np.array(output_data), dtype=torch.float32)
    
    dataset = TensorDataset(inputs_tensor, outputs_tensor)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    train_model(tf_model, dataloader)
    
    # Get the last window from 2023 for testing
    tf_test_tensor = torch.tensor(np.array(country_23[-168:]), dtype=torch.float32).unsqueeze(0)
    tf_prediction = tf_model.predict(tf_test_tensor)[0]
    
    actual_values = countries_24[idx]
    
    plt.subplot(8, 1, idx + 1)
    plt.plot(actual_values.values[:24], label="actual")
    plt.plot(tf_prediction, label="tf_prediction", color='red')
    plt.title(f"Transfer Learning: Actual vs Prediction - {country_name}")
    plt.xlabel("Time of Day in Hours")
    plt.ylabel("Electricity Consumption in MW")
    plt.legend()
    
    mae = mean_absolute_error(actual_values.values[:24], tf_prediction)
    mse = mean_squared_error(actual_values.values[:24], tf_prediction)
    mape = get_mape(actual_values.values[:24], tf_prediction)
    print(f"\nTransfer Learning Metrics for {country_name}:")
    print(f"RMSE: {np.sqrt(mse):.2f}")
    print(f"{country_name} MAPE: {mape}")

# Save the transfer learning results
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "transfer_learning_predictions.png"))
plt.close()
