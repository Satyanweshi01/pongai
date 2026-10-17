import numpy as np


inputs = [
        [1,2,3,2.5], # here we are providing multiple inputs as batch
        [2.0, 5.0, -1.0, 2.0],
        [-1.5, 2.7, 3.3, -0.8]]

# layer 1 with 3 perceptron

weights1 = [
            [0.2, 0.8, -0.5, 1.0], # weight of perceptron 1
            [0.5, -0.91, 0.26, -0.5], # weight of perceptron 2
            [-0.26, -0.27, 0.17, 0.87] # weight of perceptron 3
        ]
# dot product of these two matrices will cause shape issue
biases1 = [2,3,0.5] # biases for the individual perceptron


layer1_outputs = np.dot(inputs, np.array(weights1).T) + biases1 #here we transposed weights matrix to fix the shape issue 

# layer 2 with 3 perceptron

weights2 = [
            [0.1, -0.14, 0.5], # weight of perceptron 1
            [-0.5, 0.12, -0.33], # weight of perceptron 2
            [-0.44, 0.73, -0.13] # weight of perceptron 3
        ]

biases2 = [-1,2,-0.5] # biases for the individual perceptron

layer2_outputs = np.dot(layer1_outputs, np.array(weights2).T) + biases2
print(layer2_outputs)