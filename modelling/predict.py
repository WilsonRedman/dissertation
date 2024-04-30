import math
import pandas as pd
import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torch import nn
from pickle import load
import modelling.difference_preprocessing
import datetime
import pathlib

def predictions():

    # Gets current date
    x = datetime.datetime.now()
    pathName = "modelling\\" + str(x)[:10] + "_data.csv"

    # Checks if stock data is up to date
    if (not (pathlib.Path(pathName).is_file())):
        # If not, it removes any CSV file in the directory
        path = pathlib.Path("modelling").glob("**/*")
        files = [x for x in path if x.is_file()]
        for file in files:
            if (str(file)[-4:] == ".csv"):
                file.unlink()
        # Calls preprocessing to get current stock data
        modelling.difference_preprocessing.collect_data()

    device = "cpu"
    # Loads scaler created during training
    scaler = load(open("modelling/scaler.pkl", "rb"))

    class StockDataset(Dataset):
        def __init__(self):
            # Creates dataset to load the data from the CSV file
            self.df = pd.read_csv(pathName)
            self.df_tickers = self.df[["ticker"]]
            self.df = self.df.drop(columns=["ticker"])

            self.np = scaler.transform(self.df)
            self.df = pd.DataFrame(self.np, columns = self.df.columns)
            self.df = self.df.drop(columns=["close_end"])

            self.dataset = torch.tensor(self.df.to_numpy()).float()
            self.tickers = self.df_tickers.to_numpy().reshape(-1)

        def __len__(self):
            # Defines len function
            return len(self.dataset)
        
        def __getitem__ (self, id):
            # Defines get item function
            return self.dataset[id], self.tickers[id]
        
    # Creates dataset instance
    data = StockDataset()
    dataSize = len(data[0][0])

    # Creates the basic structure for the MLP
    class MLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.flatten = nn.Flatten()
            self.linear_tanh = nn.Sequential(
                nn.Linear(dataSize, dataSize*2),
                nn.Tanh(),
                nn.Linear(dataSize*2, dataSize*2),
                nn.Tanh(),
                nn.Linear(dataSize*2, 1),
            )
        # Defines a forward pass
        def forward(self, x):
            return self.linear_tanh(x)

    model = MLP().to(device)
    # Loads the trained model from checkpoint
    checkpoint = torch.load("modelling/model.pt")
    model.load_state_dict(checkpoint["model_state_dict"])

    model.eval()
    predictions = []
    with torch.no_grad():
        # Loops through each stock
        for i, (x, ticker) in enumerate(data, 0):
            # Converts the inputs to floats
            x= x.float().to(device)

            # Calculates the output
            output = model(x).item()
            # Reverses the Z-score normalisation
            real_out = (output* scaler.scale_[-1]) + scaler.mean_[-1]
            # Stores the result
            predictions.append([ticker, real_out])
    # Sorts the stocks by absolute size
    sorted_predictions = sorted(predictions, key = lambda sublist: abs(sublist[1]), reverse=True)
    # Returns the predictions
    return sorted_predictions

if __name__ == "__main__":
    print(predictions())