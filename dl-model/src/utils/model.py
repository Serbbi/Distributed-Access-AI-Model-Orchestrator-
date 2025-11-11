import numpy as np
import torch
import torchvision.ops
import torch.nn as nn

class MLPTimeSeriesModel(nn.Module):
    # window: the number of points to look back on. Each point should consist of data
    #         the 7 countries in a matrix. So input dim is 7 * timesteps * 24 
    #         to account for a different
    # hidden_layers: list of hidden layer sizes sizes
    # output_size: Since we are predicted 24 hours ahead, the output size is 24
    # dropout_rate: Dropout rate for the model
    def __init__(self, countries, window, hidden_layers, output_size, dropout_rate):
        super(MLPTimeSeriesModel, self).__init__()
        self.window = window * countries
        self.hidden_layers = hidden_layers
        self.output_size = output_size
        self.dropout_rate = dropout_rate
        self.model = self.create_model()

    def create_model(self):
        # We add an output layer to the model to match desired output size.
        layer_schema = self.hidden_layers + [self.output_size]
        
        mlp_model = torchvision.ops.MLP(
            in_channels=self.window,
            hidden_channels=layer_schema,
            # ToDo: check if this is the right activation function
            activation_layer=torch.nn.ReLU,
            dropout=self.dropout_rate
        )
        return mlp_model
    
    # Input should match model input size dimension.
    def forward_pass(self, input):
        return self.model(input)
    
    # Predict using previous window
    def predict(self, previous):
        self.eval()
        # ToDo: not sure if I should squeeze the arrays. Could impact output
        input = torch.tensor(previous, dtype=torch.float32)
        
        with torch.no_grad():
            prediction = self.forward_pass(input)
        
        return prediction.numpy()
    
    def save_weights(self):
        return self.state_dict()


def train_model(model, dataloader, epochs=10, learning_rate=0.001):
    # ToDo: check if this is the right loss function
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    for epoch in range(epochs):
        model.train()
        for batch_inputs, batch_outputs in dataloader:
            batch_inputs = batch_inputs.view(batch_inputs.size(0), -1)

            predictions = model.forward_pass(batch_inputs)
            
            loss = criterion(predictions, batch_outputs)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

def get_mape(actual, prediction):
    return np.mean(np.abs((actual - prediction) / actual)) * 100
