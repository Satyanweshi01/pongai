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

def relu_activate(inputs):
    output = []
    for i in inputs:
        if i > 0:
            output.append(i)
        else:
            output.append(0)
        # output.append(max(0,i))




def create_data(points, classes):
    X = np.zeros((points*classes, 2))
    y = np.zeros(points*classes, dtype='uint8')
    for class_number in range(classes):
        ix = range(points*class_number, points*(class_number+1))
        r = np.linspace(0.0,1, points)
        t = np.linspace(class_number*4, (class_number+1)*4, points) + np.random.randn(points)*0.2
        X[ix] = np.c_[r*np.sin(t*2.5), r*np.cos(t*2.5)]
        y[ix] = class_number
    return X,y