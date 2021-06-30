import numpy as np
import torch
from torchvision import datasets
from torch.utils.data import Dataset

def get_dataset(name):
    if name == 'game_data':
        return get_game_data()
#encoding
def to_one_hot(labels_np):
    labels_np = labels_np.squeeze()
    uniq = np.sort(np.unique(labels_np)).tolist()
    result = np.zeros((len(labels_np), len(uniq)))

    for index, label in enumerate(uniq):
        result[labels_np == label, index] = 1
    return result
#get dataset
def get_game_data():
    with open('genmove_trace_file2.csv', 'r') as f:
        X = []
        y = []
        line = 1
        for line in f: 
            X.append([int(x) for x in line[:81]])
            y.append([x for x in line[83:84]])
    X = np.array(X).astype(np.float32).reshape(-1, 1, 9, 9) 
    print(X[0])
    y = np.array(y)
    y = to_one_hot(y).astype(np.long)
    print(y)
    # train-test split: 0.8/0.2
    indices = np.arange(len(X))
    np.random.seed(42)
    test_indices = np.random.choice(indices, size=int(len(X) * 0.2))
    train_mask = np.ones(len(X), dtype=np.bool)
    train_mask[test_indices] = 0
    test_mask = np.zeros(len(X), dtype=np.bool)
    test_mask[test_indices] = 1

    X_train = torch.from_numpy(X[train_mask])
    y_train = torch.from_numpy(y[train_mask])

    X_test = torch.from_numpy(X[test_mask])
    y_test = torch.from_numpy(y[test_mask])

    return X_train, y_train, X_test, y_test

def get_handler(name):
    if name == 'game_data':
        return DataHandler

class DataHandler(Dataset):
    def __init__(self, X, Y, transform=None):
        self.X = X
        self.Y = Y
        self.transform = transform

    def __getitem__(self, index):
        x, y = self.X[index], self.Y[index]
        if self.transform is not None:
            x = self.transform(x)
        return x, y, index

    def __len__(self):
        return len(self.X)