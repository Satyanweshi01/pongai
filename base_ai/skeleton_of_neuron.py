# for a single neuron/ perceptron
import numpy as np


inputs = [1,2,3,2.5] # perceptron's inputs
weights = [0.2, 0.8, -0.5, 1.0] # perceptron's internal weights
bias = 2 # perceptron's bias

weighted_sum = inputs[0]*weights[0] + inputs[1]*weights[1] + inputs[2]*weights[2] + inputs[3]*weights[3] + bias # adding inputs with weight in this manner is static and inefficient
# here the activation function is missing

easy_weighted_sum = np.dot(weights,inputs) + bias # doing dot product

print(weighted_sum)
print(easy_weighted_sum)