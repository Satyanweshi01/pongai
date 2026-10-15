import numpy as np

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

class Output_Layer_Dense:
        def __init__(self, n_inputs, n_perceptron):
            self.weights = 0.10 * np.random.randn(n_inputs, n_perceptron)
            self.biases = np.zeros((1,n_perceptron)) # this gives [0,0, ...., 0]
        def softmax_forward(self,inputs):
            #print(inputs)
            #print(self.weights)
            outputs = np.dot(inputs,self.weights) + self.biases
            exp_values = np.exp(outputs - np.max(outputs, axis= 1, keepdims=True)) # to avoid a overflow
            self.output = exp_values / np.sum(exp_values, axis = 1, keepdims = True)

class NeuralNetwork:
    def __init__(self):
        self.hiddenlayer1 = Layer_Dense(6,4) # first hidden layer which consists 4 perceptron
        print(self.hiddenlayer1.weights,self.hiddenlayer1.biases)
        self.outputlayer = Output_Layer_Dense(4,3) # last output layer which consists 3 perceptron

    def forward(self,inputs):
        self.hiddenlayer1.relu_forward(inputs)
        self.outputlayer.softmax_forward(self.hiddenlayer1.output)
        return np.argmax(self.outputlayer.output) # here 0 is do nothing, 1 is up motion, 2 is down motion