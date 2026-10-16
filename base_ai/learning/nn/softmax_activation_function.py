import numpy as np

layer_outputs = [4.8, 1.21, 2.385]

exp_values = np.exp(layer_outputs)
print(exp_values)
norm_values = exp_values/np.sum(exp_values)
print(norm_values,end="\n\n")




from math import e

layer_outputs = [4.8, 1.21, 2.385]

exp_values = []

for output in layer_outputs:
    exp_values.append(e**output) # this exponential removes all the negative values with losing the impact of those negative values
print(exp_values)

# now normalize the values
summation = sum(exp_values)
norm_values = [i/summation for i in exp_values]
print(norm_values)
print(sum(norm_values))
