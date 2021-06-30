import torch.nn as nn
import torch.nn.functional as F

def get_net(name):
    if name == 'game_data':
        return Game_Net
#CNN for tabular data
class Game_Net(nn.Module):
    def __init__(self):
        super(Game_Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 4, kernel_size=5, padding=2) # initially out X batch has shape [batch_size, 1, 9, 9]
        self.conv2 = nn.Conv2d(4, 8, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(8, 16, kernel_size=3, padding=1)
        self.conv3_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(64, 400)
        self.fc2 = nn.Linear(400, 50)
        self.fc3 = nn.Linear(50, 2)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(F.max_pool2d(self.conv2(x), 2))
        x = F.relu(F.max_pool2d(self.conv3_drop(self.conv3(x)), 2))
        x = x.view(-1, 64)
        x = F.relu(self.fc1(x))
        e1 = F.relu(self.fc2(x))
        x = F.dropout(e1, training=self.training)
        x = self.fc3(x)
        return x, e1

