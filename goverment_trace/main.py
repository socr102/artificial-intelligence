import numpy as np
from dataset import get_dataset, get_handler
from network import get_net
from torchvision import transforms
import torch
from train import Strategy

class RandomSampling(Strategy):
    def __init__(self, X, Y, idxs_lb, net, handler, args):
        super(RandomSampling, self).__init__(X, Y, idxs_lb, net, handler, args)
    def query(self, n):
        return np.random.choice(np.where(self.idxs_lb==0)[0], n)

print("Running...")
# parameters
USE_CUDNN =  True
NUM_INIT_LB =480
NUM_QUERY = 100
NUM_ROUND = 0
SEED = 1
DATA_NAME = 'game_data'

args_pool = {'game_data':
                {'n_epoch': 100, 'transform': None, 
                 'loader_tr_args':{'batch_size': 64},
                 'loader_te_args':{'batch_size': 64},
                 'optimizer_args':{'lr': 0.01}}
           }
# set seed
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.backends.cudnn.enabled = USE_CUDNN

args = args_pool[DATA_NAME]

# load dataset
X_tr, Y_tr, X_te, Y_te = get_dataset(DATA_NAME)
X_tr = X_tr#[:980]
Y_tr = Y_tr#[:980]

# start experiment
n_pool = len(Y_tr)
n_test = len(Y_te)
print('number of labeled pool: {}'.format(NUM_INIT_LB))
print('number of unlabeled pool: {}'.format(n_pool - NUM_INIT_LB))
print('number of testing pool: {}'.format(n_test))

# generate initial labeled pool
idxs_lb = np.zeros(n_pool, dtype=bool)
idxs_tmp = np.arange(n_pool)
np.random.shuffle(idxs_tmp)
idxs_lb[idxs_tmp[:NUM_INIT_LB]] = True

# load network
net = get_net(DATA_NAME)
handler = get_handler(DATA_NAME)
strategy = RandomSampling(X_tr, Y_tr, idxs_lb, net, handler, args)

# print info
print(DATA_NAME)
print(type(strategy).__name__)

# round 0 accuracy
strategy.set_test_data(x=X_te, y=Y_te)
strategy.train()
P = strategy.predict(X_te, Y_te)
acc = np.zeros(NUM_ROUND+1)
acc[0] = 1.0 * (torch.max(Y_te, 1)[1]==P).sum().item() / len(Y_te)
print('Round 0\ntesting accuracy {}'.format(acc[0]))

for rd in range(1, NUM_ROUND+1):
    print('='*100+'\n' + '='*100) 
    print('Round {}'.format(rd))

    # query
    q_idxs = strategy.query(NUM_QUERY)
    idxs_lb[q_idxs] = True

    # update
    strategy.update(idxs_lb)
    strategy.train()
     
    # round accuracy
    P = strategy.predict(X_te, Y_te)
    acc[rd] = 1.0 * (Y_te==P).sum().item() / len(Y_te)
    print('testing accuracy {}'.format(acc[rd]))



