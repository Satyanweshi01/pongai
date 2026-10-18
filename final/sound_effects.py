import os
import pygame


class SoundManager:
    """
    Manages audio playback for Pong AI using pre-built sound assets.
    Handles collision sounds (paddle and wall), goal scores, button clicks, and countdowns.
    Fails gracefully if no audio device is available on the host.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SoundManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        self.audio_available = False
        self.sounds = {}

        # Sound assets directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.sound_dir = os.path.join(current_dir, "assets", "sounds")

        # Initialize mixer
        self._init_mixer()

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                # Low buffer size (512) for ultra-low latency sound playback
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.audio_available = True
            self._load_sounds()
        except Exception:
            # Audio device unavailable (e.g. headless sandbox or muted system)
            self.audio_available = False

    def _load_sounds(self):
        if not self.audio_available:
            return
        volumes = {
            "click": 0.6,
            "paddle_hit": 0.8,
            "wall_hit": 0.7,
            "score": 0.75,
            "countdown": 0.75,
            "start": 0.85
        }
        for sound_name, vol in volumes.items():
            path = os.path.join(self.sound_dir, f"{sound_name}.wav")
            if os.path.exists(path):
                try:
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(vol)
                    self.sounds[sound_name] = snd
                except Exception:
                    pass

    def play(self, sound_name: str):
        if not self.audio_available:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def play_click(self):
        self.play("click")

    def play_paddle_hit(self):
        self.play("paddle_hit")

    def play_wall_hit(self):
        self.play("wall_hit")

    def play_score(self):
        self.play("score")

    def play_countdown(self):
        self.play("countdown")

    def play_start(self):
        self.play("start")


# Global sound manager instance
sound_manager = SoundManager()
