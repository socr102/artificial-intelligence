import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
import sys


class Strategy:
    def __init__(self, X, Y, idxs_lb, net, handler, args):
        self.X = X
        self.Y = Y
        self.idxs_lb = idxs_lb
        self.net = net
        self.handler = handler
        self.args = args
        self.n_pool = len(Y)
        use_cuda = torch.cuda.is_available()
        self.device = torch.device("cuda" if use_cuda else "cpu")
        self.train_losses = []
        self.val_losses = []
        self.train_acc = []
        self.val_acc = []
        self.valX = None
        self.valY = None
    def query(self, n):
        pass
    #test data set
    def set_test_data(self, x, y):
        self.valX = x 
        self.valY = y
    def update(self, idxs_lb):
        self.idxs_lb = idxs_lb

    def _train(self, epoch, loader_tr, optimizer):
        self.clf.train()
        total_number = len(loader_tr)
        update_rate = 5
    
        # Initiate accuracies and losses per epoch
        final_train_accuracy = 0
        final_train_loss = 0
        final_val_loss = 0
        final_val_acc = 0

        for batch_idx, (x, y, idxs) in enumerate(loader_tr):
            x, y = x.to(self.device), y.to(self.device)
            optimizer.zero_grad()
            out, e1 = self.clf(x)
            loss = F.cross_entropy(out, torch.max(y, 1)[1])
            loss.backward()
            optimizer.step()
            if batch_idx % update_rate==0:
                if(batch_idx > 0):
                    erase_line()
                progress = batch_idx / total_number * 100
                acc = accuracy_quick(out, y)
                final_train_accuracy = acc
                final_train_loss = loss
                print('Training\t Progress:\t %f %%\tLoss: %f\t Training Accuracy %0.2f %%' %(progress, loss, acc))

        #Validation Load the test data and compute loss and accuracy
        loader_te = DataLoader(self.handler(self.valX, self.valY, transform=self.args['transform']),
                            shuffle=False, **self.args['loader_te_args'])

        self.clf.eval()
        loss = 0
        n = 0
        predictions = torch.zeros(len(self.valY), dtype=self.valY.dtype)
        with torch.no_grad():
            for x, y, idxs in loader_te:
                x, y = x.to(self.device), y.to(self.device)
                out, e1 = self.clf(x)
                loss += F.cross_entropy(out, torch.max(y, 1)[1])
                n += 1
                pred = out.max(1)[1]
                predictions[idxs] = pred.cpu()
          
        final_val_acc = 100.0 * (torch.max(self.valY, 1)[1]==predictions).sum().item() / len(self.valY)
        final_val_loss =  1.0 * loss/n
        print('\nValidation\n=========\nProgress:\t 100 %%\nValidation Loss: %f\nValidation Accuracy %0.2f %%\n' %( final_val_loss, final_val_acc))
        return final_train_loss, final_val_loss, final_train_accuracy, final_val_acc
             
    def train(self):

        n_epoch = self.args['n_epoch']
        self.clf = self.net().to(self.device)
        optimizer = optim.SGD(self.clf.parameters(), **self.args['optimizer_args'])

        idxs_train = np.arange(self.n_pool)[self.idxs_lb]
        loader_tr = DataLoader(self.handler(self.X[idxs_train], self.Y[idxs_train], transform=self.args['transform']),
                            shuffle=True, **self.args['loader_tr_args'])
        
        for epoch in range(1, n_epoch+1):
            print("="*100 + '\n')
            print('Epoch %d of %d' %(epoch, n_epoch))
            train_loss, val_loss, train_acc, val_acc = self._train(epoch, loader_tr, optimizer)

    def predict(self, X, Y):
        loader_te = DataLoader(self.handler(X, Y, transform=self.args['transform']),
                            shuffle=False, **self.args['loader_te_args'])

        self.clf.eval()
        P = torch.zeros(len(Y), dtype=Y.dtype)
        with torch.no_grad():
            for x, y, idxs in loader_te:
                x, y = x.to(self.device), y.to(self.device)
                out, e1 = self.clf(x)

                pred = out.max(1)[1]
                P[idxs] = pred.cpu()

        return P

    def predict_prob(self, X, Y):
        loader_te = DataLoader(self.handler(X, Y, transform=self.args['transform']),
                            shuffle=False, **self.args['loader_te_args'])

        self.clf.eval()
        probs = torch.zeros([len(Y), len(np.unique(Y))])
        with torch.no_grad():
            for x, y, idxs in loader_te:
                x, y = x.to(self.device), y.to(self.device)
                out, e1 = self.clf(x)
                prob = F.softmax(out, dim=1)
                probs[idxs] = prob.cpu()
        
        return probs

