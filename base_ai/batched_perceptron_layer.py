import numpy as np


inputs = [
        [1,2,3,2.5], # here we are providing multiple inputs as batch
        [2.0, 5.0, -1.0, 2.0],
        [-1.5, 2.7, 3.3, -0.8]]

weights = [
            [0.2, 0.8, -0.5, 1.0], # weight of perceptron 1
            [0.5, -0.91, 0.26, -0.5], # weight of perceptron 2
            [-0.26, -0.27, 0.17, 0.87] # weight of perceptron 3
        ]
# dot product of these two matrices will cause shape issue
biases = [2,3,0.5] # biases for the individual perceptron


layer_outputs = np.dot(inputs, np.array(weights).T) + biases #here we transposed weights matrix to fix the shape issue 
print(layer_outputs)
