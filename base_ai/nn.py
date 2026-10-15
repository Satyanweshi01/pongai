import numpy as np

X = [   [1.0, 2.0, 3.0, 2.5, 1.6, 1.4], # here we are providing multiple inputs as batch
        [2.0, 5.0, -1.0, 2.0, 1.2, -2.9], # six inputs
        [-1.5, 2.7, 3.3, -0.8, 0.2, 0.3]  ]

# first hidden layer which consists 4 perceptron
class Layer_Dense:
    def __init__(self, n_inputs, n_perceptron):
        self.weights = 0.10 * np.random.randn(n_inputs, n_perceptron)
        self.biases = np.zeros((1,n_perceptron)) # this gives [0,0, ...., 0]
    def relu_forward(self,inputs):
        output = np.dot(inputs,self.weights) + self.biases
        
        self.output = []
        for i in output:
            suboutput = []
            for j in i:
                suboutput.append(max(0,j))
            self.output.append(suboutput)

layer1 = Layer_Dense(6,4)
layer1.relu_forward(X)
print(layer1.output,"\n\n")

class Output_Layer_Dense:
    def __init__(self, n_inputs, n_perceptron):
        self.weights = 0.10 * np.random.randn(n_inputs, n_perceptron)
        self.biases = np.zeros((1,n_perceptron)) # this gives [0,0, ...., 0]
    def softmax_forward(self,inputs):
        print(inputs)
        print(self.weights)
        outputs = np.dot(inputs,self.weights) + self.biases
        exp_values = np.exp(outputs - np.max(outputs, axis= 1, keepdims=True)) # to avoid a overflow
        self.output = exp_values / np.sum(exp_values, axis = 1, keepdims = True)

layer2 = Output_Layer_Dense(4,3)
layer2.softmax_forward(layer1.output)
print(layer2.output)