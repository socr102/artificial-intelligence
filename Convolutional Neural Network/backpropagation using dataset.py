import math, random
import numpy as np
 
class ANN:
    '''General artificial neural network class.'''
     
    def __init__(self, num_in, num_hiddens, num_out, trainingset):
        '''Create a neural network with a set number of layers and neurons and with initialised weights and biases.'''
        if not all(len(x)==num_in and len(y)==num_out for (x,y) in trainingset.items()):
            raise ValueError()
 
        self._num_in = num_in
        self._num_hiddens = num_hiddens
        self._num_out = num_out
        self._trainingset = trainingset
 
        self._num_layers = len(num_hiddens) + 1
         
        self._weights = dict([
                (1, np.array([
                    [self.weight_init(1, i, j) for j in range(num_hiddens[0])]
                    for i in range(num_in)
                ]))
            ]
            + [
                (l+1, np.array([
                    [self.weight_init(l+1, i, j) for j in range(num_hiddens[l])]
                    for i in range(num_hiddens[l-1])
                ]))
                for l in range(1, len(num_hiddens))
            ]
            + [
                (self._num_layers, np.array([
                    [self.weight_init(self._num_layers, i, j) for j in range(num_out)]
                    for i in range(num_hiddens[-1])
                ]))
            ])
         
        self._biases = dict([
                (l+1, np.array([
                    self.bias_init(l+1, j) for j in range(num_hiddens[l])
                ]))
                for l in range(len(num_hiddens))
            ]
            + [
                (self._num_layers, np.array([
                    self.bias_init(self._num_layers, j) for j in range(num_out)
                ]))
            ])
 
    def weight_init(self, layer, i, j):
        '''How to initialise weights.'''
        return 2*random.random()-1
 
    def bias_init(self, layer, j):
        '''How to initialise biases.'''
        return 2*random.random()-1
         
    def a(self, z):
        '''The activation function.'''
        return 1/(1 + np.vectorize(np.exp)(-z))
 
    def da_dz(self, z):
        '''The derivative of the activation function.'''
        return self.a(z)*(1-self.a(z))
 
    def out(self, x):
        '''Compute the output of the neural network given an input vector.'''
        n = x
        for l in range(1, self._num_layers+1):
            n = self.a(np.dot(n, self._weights[l]) + self._biases[l])
        return n
 
    def cost(self):
        '''The cost function based on the training set.'''
        return sum(sum((self.out(x) - t)**2) for (x,t) in self._trainingset.items())/(2*len(self._trainingset))
 
    def dCxt_dnL(self, x, t):
        '''The derivative of the cost function for a particular input-target pair with respect to the output of the network.'''
        return self.out(x) - t
 
    def get_cost_gradients(self):
        '''Calculate and return the gradient of the cost function with respect to each weight and bias in the network.'''
        dC_dws = dict()
        dC_dbs = dict()
        for l in range(1, self._num_layers+1):
            dC_dws[l] = np.zeros_like(self._weights[l])
            dC_dbs[l] = np.zeros_like(self._biases[l])
         
        for (x,t) in self._trainingset.items():
            #forward pass
            zs = dict()
            ns = dict()
            ns_T = dict()
            ns[0] = np.array(x)
            ns_T[0] = np.array([np.array(x)]).T
            for l in range(1, self._num_layers+1):
                z = np.dot(ns[l-1], self._weights[l]) + self._biases[l]
                zs[l] = z
                n = self.a(z)
                ns[l] = n
                ns_T[l] = np.array([n]).T
 
            #backward pass
            d = self.dCxt_dnL(x, t)*self.da_dz(zs[self._num_layers])
            dC_dws[self._num_layers] += np.dot(ns_T[self._num_layers-1], np.array([d]))
            dC_dbs[self._num_layers] += d
            for l in range(self._num_layers-1, 1-1, -1):
                d = np.dot(d, self._weights[l+1].T)*self.da_dz(zs[l])
                dC_dws[l] += np.dot(ns_T[l-1], np.array([d]))
                dC_dbs[l] += d
 
        for l in range(1, self._num_layers+1):
            dC_dws[l] /= len(self._trainingset)
            dC_dbs[l] /= len(self._trainingset)
 
        return (dC_dws, dC_dbs)
 
    def epoch_train(self, learning_rate):
        '''Train the neural network for one epoch.'''
        (dC_dws, dC_dbs) = self.get_cost_gradients()
        for l in range(1, self._num_layers+1):
            self._weights[l] -= learning_rate*dC_dws[l]
            self._biases[l] -= learning_rate*dC_dbs[l]
     
    def check_gradient(self, epsilon=1e-5):
        '''Check if the gradients are being calculated correctly. This is done according to http://ufldl.stanford.edu/tutorial/supervised/DebuggingGradientChecking/ . This method calculates the difference between each calculated gradient (according to get_cost_gradients()) and an estimated gradient using a small number epsilon. If the gradients are calculated correctly then the returned numbers should all be very small (smaller than 1e-10.'''
        (predicted_dC_dws, predicted_dC_dbs) = self.get_cost_gradients()
 
        approx_dC_dws = dict()
        approx_dC_dbs = dict()
        for l in range(1, self._num_layers+1):
            approx_dC_dws[l] = np.zeros_like(self._weights[l])
            approx_dC_dbs[l] = np.zeros_like(self._biases[l])
             
        for l in range(1, self._num_layers+1):
            (rows, cols) = self._weights[l].shape
            for r in range(rows):
                for c in range(cols):
                    orig = self._weights[l][r][c]
                    self._weights[l][r][c] = orig + epsilon
                    cost_plus = self.cost()
                    self._weights[l][r][c] = orig - epsilon
                    cost_minus = self.cost()
                    self._weights[l][r][c] = orig
                    approx_dC_dws[l][r][c] = (cost_plus - cost_minus)/(2*epsilon)
                     
            (cols,) = self._biases[l].shape
            for c in range(cols):
                orig = self._biases[l][c]
                self._biases[l][c] = orig + epsilon
                cost_plus = self.cost()
                self._biases[l][c] = orig - epsilon
                cost_minus = self.cost()
                self._biases[l][c] = orig
                approx_dC_dbs[l][c] = (cost_plus - cost_minus)/(2*epsilon)
 
        errors_w = dict()
        errors_b = dict()
        for l in range(1, self._num_layers+1):
            errors_w[l] = abs(predicted_dC_dws[l] - approx_dC_dws[l])
            errors_b[l] = abs(predicted_dC_dbs[l] - approx_dC_dbs[l])
        return (errors_w, errors_b)
 
################################################################
nn = ANN(
    2, #number of inputs
    [ 2, 2 ], #number of hidden neurons (each number is a hidden layer)
    2, #number of outputs
    { #training set
        (0,0):(0,0),
        (0,1):(1,0),
        (1,0):(1,0),
        (1,1):(0,1)
    }
)
 
print('Initial cost:', nn.cost())
print('Starting training')
for epoch in range(1, 20000+1):
    nn.epoch_train(0.5)
    if epoch%1000 == 0:
        print(' Epoch:', epoch, ', Current cost:', nn.cost())
print('Training finished')
 
print('Neural net output:')
for (x,t) in sorted(nn._trainingset.items()):
    print(' ', x, ':', nn.out(x))