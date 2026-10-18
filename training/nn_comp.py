import numpy as np

class DenseLayer:
    def __init__(self, n_inputs, n_neurons):
        # Xavier/Glorot initialization suitable for tanh activation
        self.weights = np.random.randn(n_inputs, n_neurons) * np.sqrt(1.0 / n_inputs)
        self.biases = np.zeros(n_neurons)

    def forward(self, inputs):
        return np.dot(inputs, self.weights) + self.biases


class NeuralNetwork:
    def __init__(self, n_inputs=6, n_hidden=8, n_outputs=3):
        self.n_inputs = n_inputs
        self.n_hidden = n_hidden
        self.n_outputs = n_outputs
        self.hiddenlayer1 = DenseLayer(n_inputs, n_hidden)
        self.outputlayer = DenseLayer(n_hidden, n_outputs)

    def clone(self):
        new_net = NeuralNetwork(self.n_inputs, self.n_hidden, self.n_outputs)
        new_net.hiddenlayer1.weights = self.hiddenlayer1.weights.copy()
        new_net.hiddenlayer1.biases = self.hiddenlayer1.biases.copy()
        new_net.outputlayer.weights = self.outputlayer.weights.copy()
        new_net.outputlayer.biases = self.outputlayer.biases.copy()
        return new_net

    def mutate(self, mutation_rate: float = 0.05, sigma: float = 0.1):
        for layer in [self.hiddenlayer1, self.outputlayer]:
            # Mutate weights
            mask_w = np.random.random(layer.weights.shape) < mutation_rate
            layer.weights[mask_w] += np.random.normal(0, sigma, size=np.count_nonzero(mask_w))
            np.clip(layer.weights, -3.0, 3.0, out=layer.weights)

            # Mutate biases (higher mutation probability for biases)
            bias_mutation_rate = max(0.20, mutation_rate * 3)
            mask_b = np.random.random(layer.biases.shape) < bias_mutation_rate
            layer.biases[mask_b] += np.random.normal(0, sigma, size=np.count_nonzero(mask_b))
            np.clip(layer.biases, -3.0, 3.0, out=layer.biases)

    def weights_save(self, name: str):
        np.savez(
            name,
            hiddenlayer1weights=self.hiddenlayer1.weights,
            hiddenlayer1biases=self.hiddenlayer1.biases,
            outputlayerweights=self.outputlayer.weights,
            outputlayerbiases=self.outputlayer.biases
        )

    def weights_load(self, npz_file):
        with np.load(npz_file) as data:
            self.hiddenlayer1.weights = data["hiddenlayer1weights"].copy()
            self.hiddenlayer1.biases = data["hiddenlayer1biases"].ravel().copy()
            self.outputlayer.weights = data["outputlayerweights"].copy()
            self.outputlayer.biases = data["outputlayerbiases"].ravel().copy()

    def forward(self, inputs):
        # 1. Hidden layer with Tanh activation (smooth, bounded between -1 and 1, no dead units)
        h = np.tanh(self.hiddenlayer1.forward(inputs))

        # 2. Linear logits for output layer (fast, no redundant softmax exponentials)
        out = self.outputlayer.forward(h)

        # 3. Argmax directly selects action: 0 = stay, 1 = up, 2 = down
        return int(np.argmax(out))
