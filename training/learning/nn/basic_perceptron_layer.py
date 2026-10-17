import numpy as np


inputs = [1,2,3,2.5] # common input

weights = [
            [0.2, 0.8, -0.5, 1.0], # weight of perceptron 1
            [0.5, -0.91, 0.26, -0.5], # weight of perceptron 2
            [-0.26, -0.27, 0.17, 0.87] # weight of perceptron 3
        ]
biases = [2,3,0.5] # biases for the individual perceptron

'''
layer_outputs = []
for perceptron_weight, perceptron_bias in zip(weights,biases):
    perceptron_output = 0 # output of a perceptron
    for n_input, weight in zip(inputs, perceptron_weight):
        perceptron_output += n_input*weight
    perceptron_output += perceptron_bias
    layer_outputs.append(perceptron_output)

print(layer_outputs)
'''

layer_outputs = np.dot(weights, inputs) + biases
print(layer_outputs)
#layer_outputs = np.dot(inputs, weights) + biases # not possible because of shape/matrix order mismatch 
#print(layer_outputs)