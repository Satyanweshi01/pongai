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
            # Dynamically derive architecture dimensions from loaded weights
            self.n_inputs = self.hiddenlayer1.weights.shape[0]
            self.n_hidden = self.hiddenlayer1.weights.shape[1]
            self.n_outputs = self.outputlayer.weights.shape[1]

    def forward(self, inputs):
        # 1. Hidden layer with Tanh activation (smooth, bounded between -1 and 1, no dead units)
        h = np.tanh(self.hiddenlayer1.forward(inputs))

        # 2. Linear logits for output layer (fast, no redundant softmax exponentials)
        out = self.outputlayer.forward(h)

        # 3. Argmax directly selects action: 0 = stay, 1 = up, 2 = down
        return int(np.argmax(out))

    def get_forward_details(self, inputs):
        """
        Returns full telemetry of the forward pass for visualization:
        - raw inputs
        - multiplications per input-to-hidden connection
        - linear sums, biases, weighted sums (z), and tanh activations for hidden layer
        - multiplications, linear sums, biases, logits (z_out), and argmax decision for output layer
        """
        x = np.array(inputs, dtype=np.float64)
        if x.ndim == 1:
            x_vec = x
        else:
            x_vec = x.ravel()

        w1 = self.hiddenlayer1.weights
        b1 = self.hiddenlayer1.biases
        w2 = self.outputlayer.weights
        b2 = self.outputlayer.biases

        # Hidden layer: x_i * w_ij
        # Shape: (n_inputs, n_hidden)
        hidden_products = x_vec[:, None] * w1
        hidden_linear_sums = np.sum(hidden_products, axis=0)
        hidden_weighted_sums = hidden_linear_sums + b1  # z_j
        hidden_activations = np.tanh(hidden_weighted_sums)  # a_j = tanh(z_j)

        # Output layer: a_j * w_jk
        # Shape: (n_hidden, n_outputs)
        output_products = hidden_activations[:, None] * w2
        output_linear_sums = np.sum(output_products, axis=0)
        output_weighted_sums = output_linear_sums + b2  # z_out_k
        decision = int(np.argmax(output_weighted_sums))

        return {
            "inputs": x_vec,
            "hidden_products": hidden_products,
            "hidden_linear_sums": hidden_linear_sums,
            "hidden_biases": b1,
            "hidden_weighted_sums": hidden_weighted_sums,
            "hidden_activations": hidden_activations,
            "output_products": output_products,
            "output_linear_sums": output_linear_sums,
            "output_biases": b2,
            "output_weighted_sums": output_weighted_sums,
            "decision": decision,
        }

