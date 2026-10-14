import numpy as np

np.random.seed(0)


X = [   [1.0, 2.0, 3.0, 2.5], # here we are providing multiple inputs as batch
        [2.0, 5.0, -1.0, 2.0],
        [-1.5, 2.7, 3.3, -0.8]  ]

class Layer_Dense:
    def __init__(self, n_inputs, n_perceptron):
        self.weights = 0.10 * np.random.randn(n_inputs, n_perceptron)
        self.biases = np.zeros((1,n_perceptron)) # this gives [0,0, ...., 0]
    def forward(self,inputs):
        self.output = np.dot(inputs,self.weights) + self.biases

layer1 = Layer_Dense(4,5)
layer2 = Layer_Dense(5,6)

layer1.forward(X) # giving inputs to layer1
print(layer1.output)
layer2.forward(layer1.output) # giving output of the layer1 to the layer2
print(layer2.output)
