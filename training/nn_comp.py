import numpy as np

class DenseLayer:
    def __init__(self, n_inputs, n_neurons):
        # Xavier/He-style initialization suitable for tanh activation
        self.weights = np.random.randn(n_inputs, n_neurons) * np.sqrt(2.0 / n_inputs)
        self.biases = np.random.normal(0, 0.05, (1, n_neurons))

    def forward(self, inputs):
        inputs = np.asarray(inputs, dtype=float).reshape(1, -1)
        self.output = np.dot(inputs, self.weights) + self.biases
        return self.output


class NeuralNetwork:
    def __init__(self, n_inputs=6, n_hidden=8, n_outputs=3):
        self.hiddenlayer1 = DenseLayer(n_inputs, n_hidden)
        self.outputlayer = DenseLayer(n_hidden, n_outputs)

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
            self.hiddenlayer1.biases = data["hiddenlayer1biases"].copy()
            self.outputlayer.weights = data["outputlayerweights"].copy()
            self.outputlayer.biases = data["outputlayerbiases"].copy()

    def forward(self, inputs):
        # 1. Hidden layer with Tanh activation (smooth, bounded between -1 and 1, no dead units)
        h = np.tanh(self.hiddenlayer1.forward(inputs))

        # 2. Linear logits for output layer (fast, no redundant softmax exponentials)
        out = self.outputlayer.forward(h)

        # 3. Argmax directly selects action: 0 = stay, 1 = up, 2 = down
        return int(np.argmax(out))
