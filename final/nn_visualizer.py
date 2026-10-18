import math
import pygame

try:
    from sound_effects import sound_manager
except ImportError:
    from final.sound_effects import sound_manager

# Minimalist clean palette: Dark Obsidian background, White perceptrons, Green activation signals
COLOR_BG = (10, 13, 20)
COLOR_PANEL_BG = (16, 22, 32)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 255, 136)         # Vibrant Neon Green for activation signals
COLOR_MUTED = (150, 165, 185)


class NNVisualizer:
    """
    Non-interactive, clean, live Neural Network Visualizer.
    Expanded across the full window:
    - Input Layer (left)
    - Hidden Layer (center)
    - Output Layer (right)
    - White perceptrons with biases written on them.
    - Underneath each perceptron: weighted sum (z) and activated response (tanh(z)).
    - Vibrant green activation signals and pulses flowing along synapses.
    - Derived dynamically from loaded weights (not hardcoded).
    """

    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
        self.window = None
        self.surface = None
        self.is_open = False
        self.pulse_timer = 0.0
        self.n_hidden = 8

        # Standard semantic names if input size matches Pong AI (6 inputs)
        self.standard_input_labels = [
            "Ball X (Norm)",
            "Ball Y (Norm)",
            "Ball Vx (/15)",
            "Ball Vy (/15)",
            "Paddle ΔY (Err)",
            "Paddle Y (Pos)",
        ]

        # Standard semantic names if output size matches Pong AI (3 outputs)
        self.standard_output_labels = [
            "STAY",
            "UP",
            "DOWN",
        ]

        # Fonts
        self.fonts = {}
        self._init_fonts()

    def _init_fonts(self):
        if not pygame.font.get_init():
            pygame.font.init()
        self.fonts["layer_title"] = pygame.font.SysFont("Arial", 16, bold=True)
        self.fonts["node_name"] = pygame.font.SysFont("Arial", 12, bold=True)
        self.fonts["node_bias"] = pygame.font.SysFont("Arial", 10, bold=True)
        self.fonts["node_val"] = pygame.font.SysFont("Arial", 11, bold=False)
        self.fonts["node_act"] = pygame.font.SysFont("Arial", 11, bold=True)
        self.fonts["out_name"] = pygame.font.SysFont("Arial", 15, bold=True)
        self.fonts["out_bias"] = pygame.font.SysFont("Arial", 12, bold=True)
        self.fonts["out_val"] = pygame.font.SysFont("Arial", 13, bold=False)
        self.fonts["badge"] = pygame.font.SysFont("Arial", 12, bold=True)

    def show(self):
        """Opens or brings the visualizer window to the front."""
        if self.window is None:
            try:
                self.window = pygame.Window(
                    "Pong AI - Neural Network Architecture",
                    size=(self.width, self.height)
                )
                self.surface = self.window.get_surface()
                self.is_open = True
            except Exception as e:
                print(f"Error creating visualizer window: {e}")
                self.is_open = False
        else:
            self.window.show()
            self.window.focus()
            self.surface = self.window.get_surface()
            self.is_open = True

    def hide(self):
        """Hides the visualizer window without destroying it."""
        if self.window is not None:
            try:
                self.window.hide()
            except Exception:
                pass
        self.is_open = False

    def toggle(self):
        """Toggles visualizer window visibility."""
        if self.is_open:
            self.hide()
        else:
            self.show()

    def destroy(self):
        """Destroys the secondary window."""
        if self.window is not None:
            try:
                self.window.destroy()
            except Exception:
                pass
            self.window = None
            self.surface = None
        self.is_open = False

    def handle_event(self, event, pause_callback=None):
        """
        Handles events directed at the visualizer window.
        Non-interactive: only responds to window close or ESC / Space for pause.
        """
        if not self.is_open or self.window is None:
            return None

        # Check window close from OS titlebar 'X' button
        if event.type == pygame.WINDOWCLOSE:
            if getattr(event, "window", None) == self.window:
                self.hide()
                sound_manager.play_click()
                return "CLOSED"

        if getattr(event, "window", None) == self.window:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.hide()
                    sound_manager.play_click()
                    return "CLOSED"
                elif event.key == pygame.K_SPACE and pause_callback:
                    sound_manager.play_click()
                    pause_callback()
                    return "PAUSE_TOGGLED"

        return None

    def update_and_draw(self, dt: float, brain, inputs, is_paused: bool = False, active_decision: int = None):
        """Renders the entire live visualizer on its window surface."""
        if not self.is_open or self.window is None:
            return

        self.pulse_timer += dt
        surf = self.window.get_surface()
        self.render_visualizer(surf, dt, brain, inputs, is_paused, active_decision)
        self.window.flip()

    def render_visualizer(self, surf, dt: float, brain, inputs, is_paused: bool = False, active_decision: int = None):
        """Core spacious rendering logic for expanded 3-layer architecture."""
        surf.fill(COLOR_BG)

        # 1. Dynamically derive architecture strictly from loaded weights
        w1 = brain.hiddenlayer1.weights
        b1 = brain.hiddenlayer1.biases
        w2 = brain.outputlayer.weights
        b2 = brain.outputlayer.biases

        n_inputs = w1.shape[0]
        n_hidden = w1.shape[1]
        n_outputs = w2.shape[1]
        self.n_hidden = n_hidden

        # Compute forward pass telemetry
        telemetry = brain.get_forward_details(inputs)
        x_vec = telemetry["inputs"]
        z_hidden = telemetry["hidden_weighted_sums"]
        a_hidden = telemetry["hidden_activations"]
        z_output = telemetry["output_weighted_sums"]
        decision = active_decision if active_decision is not None else telemetry["decision"]

        # 2. Expanded 3-Column Layout across the full 1280px width
        x_in = 190
        x_hid = 640
        x_out = 1090

        top_y = 80
        bottom_y = self.height - 70
        avail_h = bottom_y - top_y

        y_inputs = [top_y + (avail_h * i) / max(1, n_inputs - 1) for i in range(n_inputs)]
        y_hidden = [top_y + (avail_h * j) / max(1, n_hidden - 1) for j in range(n_hidden)]
        y_output = [top_y + 80 + ((avail_h - 160) * k) / max(1, n_outputs - 1) for k in range(n_outputs)]

        r_hid = 22

        # 3. Draw Synapses with Green Activation Signals
        self._draw_synapses_input_hidden(surf, x_in, y_inputs, x_hid, y_hidden, r_hid, w1, x_vec, a_hidden)
        self._draw_synapses_hidden_output(surf, x_hid, y_hidden, r_hid, x_out, y_output, 40, w2, a_hidden, decision)

        # 4. Draw Perceptrons in White with Green Activations
        self._draw_input_nodes(surf, x_in, y_inputs, x_vec, n_inputs)
        self._draw_hidden_perceptrons(surf, x_hid, y_hidden, r_hid, b1, z_hidden, a_hidden, n_hidden)
        self._draw_output_perceptrons(surf, x_out, y_output, 40, b2, z_output, decision, n_outputs)

        # 5. Layer Titles (clean and minimal, no bottom line)
        self._draw_layer_titles(surf, x_in, x_hid, x_out)

    # =========================================================================
    # LAYER TITLES
    # =========================================================================
    def _draw_layer_titles(self, surf, x_in, x_hid, x_out):
        t1 = self.fonts["layer_title"].render("INPUT LAYER", True, COLOR_WHITE)
        t2 = self.fonts["layer_title"].render("HIDDEN LAYER (Tanh)", True, COLOR_WHITE)
        t3 = self.fonts["layer_title"].render("OUTPUT LAYER (Argmax)", True, COLOR_WHITE)

        surf.blit(t1, t1.get_rect(center=(x_in, 38)))
        surf.blit(t2, t2.get_rect(center=(x_hid, 38)))
        surf.blit(t3, t3.get_rect(center=(x_out, 38)))

    # =========================================================================
    # SYNAPSES: INPUT -> HIDDEN (GREEN ACTIVATION SIGNALS)
    # =========================================================================
    def _draw_synapses_input_hidden(self, surf, x_in, y_inputs, x_hid, y_hidden, r_hid, w1, x_vec, a_hidden):
        start_x = x_in + 105
        end_x = x_hid - r_hid

        for j in range(len(y_hidden)):
            for i in range(len(y_inputs)):
                w = w1[i, j]
                prod = x_vec[i] * w
                act_intensity = min(1.0, abs(prod))

                start_pt = (start_x, y_inputs[i])
                end_pt = (end_x, y_hidden[j])

                # Synapse line with subtle green modulation based on signal
                line_color = (
                    int(24 + 40 * act_intensity),
                    int(34 + 90 * act_intensity),
                    int(46 + 40 * act_intensity)
                )
                line_w = max(1, min(3, int(1 + abs(w) * 1.5)))
                pygame.draw.line(surf, line_color, start_pt, end_pt, line_w)

                # Green activation signal pulses traveling along synapse
                if act_intensity > 0.03:
                    pulse_progress = (self.pulse_timer * 1.6 + (i * 0.14) + (j * 0.08)) % 1.0
                    px = start_x + (end_x - start_x) * pulse_progress
                    py = y_inputs[i] + (y_hidden[j] - y_inputs[i]) * pulse_progress
                    pulse_r = max(2, min(4, int(2 + act_intensity * 2.0)))
                    pygame.draw.circle(surf, COLOR_GREEN, (round(px), round(py)), pulse_r)

    # =========================================================================
    # SYNAPSES: HIDDEN -> OUTPUT (GREEN ACTIVATION SIGNALS)
    # =========================================================================
    def _draw_synapses_hidden_output(self, surf, x_hid, y_hidden, r_hid, x_out, y_output, r_out, w2, a_hidden, decision):
        start_x = x_hid + r_hid
        end_x = x_out - r_out

        for k in range(len(y_output)):
            is_winner = (k == decision)
            for j in range(len(y_hidden)):
                w = w2[j, k]
                act = a_hidden[j]
                signal = act * w

                start_pt = (start_x, y_hidden[j])
                end_pt = (end_x, y_output[k])

                if is_winner:
                    # Vibrant Green transmission toward the winning decision
                    intensity = min(1.0, max(0.2, abs(signal)))
                    line_col = (
                        int(20 + 190 * intensity),
                        int(70 + 185 * intensity),
                        int(40 + 95 * intensity)
                    )
                    line_w = max(2, min(5, int(1.5 + abs(w) * 2.2)))
                    pygame.draw.line(surf, line_col, start_pt, end_pt, line_w)

                    # Green signal pulse traveling to winner
                    p_prog = (self.pulse_timer * 2.0 + (j * 0.12)) % 1.0
                    px = start_x + (end_x - start_x) * p_prog
                    py = y_hidden[j] + (y_output[k] - y_hidden[j]) * p_prog
                    pygame.draw.circle(surf, COLOR_GREEN, (round(px), round(py)), 3)
                else:
                    pygame.draw.line(surf, (22, 32, 45), start_pt, end_pt, 1)

    # =========================================================================
    # INPUT NODES (WHITE CARDS WITH GREEN ACTIVATION LEVEL)
    # =========================================================================
    def _draw_input_nodes(self, surf, x_in, y_inputs, x_vec, n_inputs):
        node_w = 210
        node_h = 48

        for i in range(n_inputs):
            cy = y_inputs[i]
            rect = pygame.Rect(x_in - node_w // 2, cy - node_h // 2, node_w, node_h)
            val = x_vec[i]

            # Label
            if i < len(self.standard_input_labels):
                name = f"x{i}: {self.standard_input_labels[i]}"
            else:
                name = f"Input x{i}"

            # Card background
            pygame.draw.rect(surf, COLOR_PANEL_BG, rect, border_radius=8)

            # Perceptron color: WHITE border
            pygame.draw.rect(surf, COLOR_WHITE, rect, width=2, border_radius=8)

            # Green activation indicator bar at bottom of card
            bar_pct = min(1.0, abs(val))
            bar_w = int(bar_pct * (node_w - 16))
            if bar_w > 0:
                bar_rect = pygame.Rect(rect.x + 8, rect.bottom - 6, bar_w, 3)
                pygame.draw.rect(surf, COLOR_GREEN, bar_rect, border_radius=2)

            # Text
            name_surf = self.fonts["node_name"].render(name, True, COLOR_WHITE)
            val_surf = self.fonts["node_val"].render(f"value: {val:+.3f}", True, COLOR_MUTED)
            surf.blit(name_surf, (rect.x + 12, rect.y + 6))
            surf.blit(val_surf, (rect.x + 12, rect.y + 26))

    # =========================================================================
    # HIDDEN PERCEPTRONS (WHITE CIRCLES + GREEN ACTIVATION SIGNAL)
    # =========================================================================
    def _draw_hidden_perceptrons(self, surf, x_hid, y_hidden, r_hid, b1, z_hidden, a_hidden, n_hidden):
        for j in range(n_hidden):
            cy = y_hidden[j]
            bias = b1[j]
            z = z_hidden[j]
            act = a_hidden[j]

            # Green activation fill inside perceptron proportional to |tanh(z)|
            act_intensity = min(1.0, abs(act))
            fill_col = (
                int(12 + 35 * act_intensity),
                int(18 + 105 * act_intensity),
                int(26 + 55 * act_intensity)
            )

            # Circle body
            pygame.draw.circle(surf, fill_col, (x_hid, round(cy)), r_hid)

            # Perceptron color: WHITE border
            pygame.draw.circle(surf, COLOR_WHITE, (x_hid, round(cy)), r_hid, width=2)

            # Inside the perceptron:
            # Line 1: Neuron ID in bold White
            id_surf = self.fonts["node_name"].render(f"H{j}", True, COLOR_WHITE)
            surf.blit(id_surf, id_surf.get_rect(center=(x_hid, round(cy - 6))))

            # Line 2: Bias written ON the perceptron in White
            b_surf = self.fonts["node_bias"].render(f"b:{bias:+.2f}", True, COLOR_WHITE)
            surf.blit(b_surf, b_surf.get_rect(center=(x_hid, round(cy + 6))))

            # Underneath each perceptron:
            # Line 1: weighted sum (z) in White
            # Line 2: activated function response (tanh(z)) in Green
            z_surf = self.fonts["node_val"].render(f"z = {z:+.2f}", True, COLOR_WHITE)
            act_surf = self.fonts["node_act"].render(f"tanh = {act:+.2f}", True, COLOR_GREEN)

            surf.blit(z_surf, z_surf.get_rect(center=(x_hid, round(cy + r_hid + 8))))
            surf.blit(act_surf, act_surf.get_rect(center=(x_hid, round(cy + r_hid + 20))))

    # =========================================================================
    # OUTPUT PERCEPTRONS (WHITE CIRCLES + GREEN WINNING SIGNAL)
    # =========================================================================
    def _draw_output_perceptrons(self, surf, x_out, y_output, r_out, b2, z_output, decision, n_outputs):
        for k in range(n_outputs):
            cy = y_output[k]
            bias = b2[k]
            z = z_output[k]
            is_winner = (k == decision)

            if k < len(self.standard_output_labels):
                action_name = self.standard_output_labels[k]
            else:
                action_name = f"Out {k}"

            # Inner fill: Green when chosen winner
            fill_col = (18, 70, 40) if is_winner else (16, 22, 32)
            pygame.draw.circle(surf, fill_col, (x_out, round(cy)), r_out)

            # Green pulsing glow ring if winner
            if is_winner:
                p_r = r_out + 6 + int(3 * math.sin(self.pulse_timer * 7))
                pygame.draw.circle(surf, COLOR_GREEN, (x_out, round(cy)), p_r, width=2)

            # Perceptron color: WHITE border
            border_w = 4 if is_winner else 2
            pygame.draw.circle(surf, COLOR_WHITE, (x_out, round(cy)), r_out, width=border_w)

            # Inside perceptron: Action Name & Bias written on it in White
            name_surf = self.fonts["out_name"].render(action_name, True, COLOR_WHITE)
            b_surf = self.fonts["out_bias"].render(f"b:{bias:+.2f}", True, COLOR_WHITE)
            surf.blit(name_surf, name_surf.get_rect(center=(x_out, round(cy - 9))))
            surf.blit(b_surf, b_surf.get_rect(center=(x_out, round(cy + 10))))

            # Underneath output perceptron:
            # Line 1: weighted sum (z_out) in White
            # Line 2: [ACTIVE] in Green if winner
            z_surf = self.fonts["out_val"].render(f"z = {z:+.2f}", True, COLOR_WHITE)
            surf.blit(z_surf, z_surf.get_rect(center=(x_out, round(cy + r_out + 12))))

            if is_winner:
                w_surf = self.fonts["badge"].render("★ ACTIVE", True, COLOR_GREEN)
                surf.blit(w_surf, w_surf.get_rect(center=(x_out, round(cy + r_out + 28))))
