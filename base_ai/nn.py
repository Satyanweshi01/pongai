import numpy as np

def neural_network(inputs): #inputs here should be 1d array of 6 inputs 
    # first hidden layer which consists 4 perceptron
    print(f"inputs: {inputs}")
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
    layer1.relu_forward(inputs)
    #print(layer1.output,"\n\n")

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

    layer2 = Output_Layer_Dense(4,3)
    layer2.softmax_forward(layer1.output)
    print(f"layer output: {layer2.output}")
    decision = np.argmax(layer2.output)
    print(f"the decision: {decision}")
    return decision # here 0 is do nothing, 1 is up motion, 2 is down motion