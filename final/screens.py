import os
import math
import random
import pygame
from sound_effects import sound_manager

# Pixel font (used ONLY for "Pong AI" Title and "PLAY" Button)
PIXEL_FONT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "assets",
    "karmatic-arcade",
    "ka1.ttf"
)


def get_pixel_font(size: int):
    """Loads the pixel font strictly for the title and play button."""
    if PIXEL_FONT_PATH and os.path.exists(PIXEL_FONT_PATH):
        try:
            return pygame.font.Font(PIXEL_FONT_PATH, size)
        except Exception:
            pass
    return pygame.font.SysFont("Arial", size, bold=True)


def get_old_font(size: int, bold: bool = True):
    """Old standard font (Arial) for all other UI elements."""
    return pygame.font.SysFont("Arial", size, bold=bold)


#colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_BLUE = (0, 140, 255)
COLOR_RED = (255, 50, 50)


class Particle:
    """A floating or bursting neon spark particle."""
    def __init__(self, x, y, vx, vy, color, lifetime=0.6, size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.size = size

    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    def is_alive(self):
        return self.age < self.lifetime

    def draw(self, surface):
        if not self.is_alive():
            return
        life_ratio = max(0.0, 1.0 - (self.age / self.lifetime))
        radius = max(1, int(self.size * life_ratio))
        pygame.draw.circle(surface, self.color, (round(self.x), round(self.y)), radius)



class Title:
    """
    Clean, static "Pong AI" Title using the pixel font.
    "PONG" in Blue, "AI" in Red.
    """
    def __init__(self, center_x=600, center_y=230, font_size=96):
        self.center_x = center_x
        self.center_y = center_y
        self.font_size = font_size
        self.font = get_pixel_font(font_size)

        # Pre-rendered text surfaces
        self.pong_surf = self.font.render("PONG", True, COLOR_BLUE)
        self.ai_surf = self.font.render("AI", True, COLOR_RED)
        self.gap = 30
        self.total_width = self.pong_surf.get_width() + self.gap + self.ai_surf.get_width()
        self.total_height = max(self.pong_surf.get_height(), self.ai_surf.get_height())

        self.pong_x = self.center_x - self.total_width // 2
        self.pong_y = self.center_y - self.pong_surf.get_height() // 2
        self.ai_x = self.pong_x + self.pong_surf.get_width() + self.gap
        self.ai_y = self.center_y - self.ai_surf.get_height() // 2

    def update(self, dt, mouse_pos=None):
        pass

    def draw(self, surface):
        surface.blit(self.pong_surf, (self.pong_x, self.pong_y))
        surface.blit(self.ai_surf, (self.ai_x, self.ai_y))


class PlayButton:
    """
    Arcade Play Button with responsive neon hover animations.
    Strictly uses: Black, White, Blue, and Red.
    """
    def __init__(self, center_x=600, center_y=420, width=240, height=64, text="PLAY", font_size=28):
        self.center_x = center_x
        self.center_y = center_y
        self.base_width = width
        self.base_height = height
        # Clean up any arrow symbols that lack visual glyphs in the pixel font
        if text.startswith("< "):
            text = text[2:]
        elif text.startswith("<"):
            text = text[1:].strip()

        self.text = text
        self.font = get_pixel_font(font_size)

        self.rect = pygame.Rect(
            center_x - width // 2,
            center_y - height // 2,
            width,
            height
        )

        self.is_hovered = False
        self.hover_factor = 0.0
        self.spark_timer = 0.0
        self.particles = []

    def update(self, dt, mouse_pos=None):
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        self.is_hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.is_hovered else 0.0
        self.hover_factor += (target - self.hover_factor) * min(1.0, dt * 12.0)

        # Spawn neon spark particles along button perimeter on hover
        if self.is_hovered:
            self.spark_timer += dt
            if self.spark_timer > 0.06:
                self.spark_timer = 0.0
                edge = random.choice(["top", "bottom", "left", "right"])
                if edge == "top":
                    px = random.uniform(self.rect.left, self.rect.right)
                    py = self.rect.top
                elif edge == "bottom":
                    px = random.uniform(self.rect.left, self.rect.right)
                    py = self.rect.bottom
                elif edge == "left":
                    px = self.rect.left
                    py = random.uniform(self.rect.top, self.rect.bottom)
                else:
                    px = self.rect.right
                    py = random.uniform(self.rect.top, self.rect.bottom)

                pcolor = random.choice([COLOR_BLUE, COLOR_RED, COLOR_WHITE])
                self.particles.append(
                    Particle(px, py, random.uniform(-40, 40), random.uniform(-40, 40), pcolor, lifetime=0.4, size=2)
                )

        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.is_alive()]

    def set_text(self, text):
        if text.startswith("< "):
            text = text[2:]
        elif text.startswith("<"):
            text = text[1:].strip()
        self.text = text

    def handle_event(self, event):
        """Returns True if the button is clicked with the mouse or activated via Enter/Space when hovered."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(event, "pos") and self.rect.collidepoint(event.pos):
                sound_manager.play_click()
                return True
            if self.is_hovered:
                sound_manager.play_click()
                return True
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.is_hovered:
                sound_manager.play_click()
                return True
        return False

    def draw(self, surface):
        # Size expands smoothly by 8px when hovered
        expansion = int(self.hover_factor * 8)
        draw_rect = self.rect.inflate(expansion, expansion)

        # Background: Black transitioning to glowing Red fill on hover
        if self.hover_factor > 0.01:
            bg_surf = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
            fill_alpha = int(220 * self.hover_factor)
            pygame.draw.rect(
                bg_surf,
                (255, 50, 50, fill_alpha),
                (0, 0, draw_rect.width, draw_rect.height),
                border_radius=8
            )
            surface.blit(bg_surf, draw_rect.topleft)
        else:
            pygame.draw.rect(surface, COLOR_BLACK, draw_rect, border_radius=8)

        # Border: Blue in normal state, shifts to White/Red glow on hover
        border_color = (
            round(COLOR_BLUE[0] * (1 - self.hover_factor) + COLOR_WHITE[0] * self.hover_factor),
            round(COLOR_BLUE[1] * (1 - self.hover_factor) + COLOR_WHITE[1] * self.hover_factor),
            round(COLOR_BLUE[2] * (1 - self.hover_factor) + COLOR_WHITE[2] * self.hover_factor),
        )
        border_width = 3 if self.hover_factor < 0.5 else 4
        pygame.draw.rect(surface, border_color, draw_rect, width=border_width, border_radius=8)

        # Draw text: White on normal, Black on hover for ultra-high contrast
        text_color = (
            round(COLOR_WHITE[0] * (1 - self.hover_factor) + COLOR_BLACK[0] * self.hover_factor),
            round(COLOR_WHITE[1] * (1 - self.hover_factor) + COLOR_BLACK[1] * self.hover_factor),
            round(COLOR_WHITE[2] * (1 - self.hover_factor) + COLOR_BLACK[2] * self.hover_factor),
        )

        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        # 1px vertical optical alignment for karmatic-arcade font ascent
        text_rect.centery = draw_rect.centery + 1
        surface.blit(text_surf, text_rect)

        # Draw spark particles
        for p in self.particles:
            p.draw(surface)


class MenuScreen:
    """
    Main Menu containing "Pong AI" title and "PLAY" button.
    Includes ambient neon particles and gameplay tips.
    Color Palette: Strictly Black, White, Blue, and Red.
    """
    def __init__(self, width=1200, height=700):
        self.width = width
        self.height = height

        self.title = Title(center_x=width // 2, center_y=230, font_size=96)
        self.play_button = PlayButton(center_x=width // 2, center_y=410, width=260, height=68, text="PLAY")

        self.hint_font = get_old_font(13, bold=True)

        # Ambient floating neon dust particles in the background
        self.ambient_particles = []
        for _ in range(35):
            self.ambient_particles.append(
                Particle(
                    random.uniform(0, width),
                    random.uniform(0, height),
                    random.uniform(-15, 15),
                    random.uniform(-15, 15),
                    random.choice([COLOR_BLUE, COLOR_RED, COLOR_WHITE]),
                    lifetime=random.uniform(3.0, 7.0),
                    size=random.choice([2, 3])
                )
            )

    def update(self, dt, mouse_pos=None):
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        self.title.update(dt, mouse_pos)
        self.play_button.update(dt, mouse_pos)

        # Update ambient particles
        for p in self.ambient_particles:
            p.update(dt)
            # Wrap around screen edges
            if p.x < 0:
                p.x = self.width
            elif p.x > self.width:
                p.x = 0
            if p.y < 0:
                p.y = self.height
            elif p.y > self.height:
                p.y = 0

            if not p.is_alive():
                p.age = 0.0
                p.x = random.uniform(0, self.width)
                p.y = random.uniform(0, self.height)

    def handle_event(self, event):
        """Returns 'PLAY' if the user initiates gameplay, else None."""
        if self.play_button.handle_event(event):
            return "PLAY"
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            sound_manager.play_click()
            return "PLAY"
        return None

    def draw(self, surface):
        surface.fill(COLOR_BLACK)

        # Ambient background particles
        for p in self.ambient_particles:
            p.draw(surface)

        # Draw Title
        self.title.draw(surface)

        # Draw Play Button with hover effect
        self.play_button.draw(surface)

        # Controls guide footer
        controls_text = self.hint_font.render(
            "CLICK PLAY TO CHOOSE MODE  |  ESC: QUIT",
            True,
            (160, 180, 200)
        )
        ctrl_rect = controls_text.get_rect(center=(self.width // 2, self.height - 40))
        surface.blit(controls_text, ctrl_rect)


class ModeScreen:
    """
    Mode Selection Screen in between Menu and Game:
    - Large "MODE" arcade title
    - Two arcade buttons: "VS AI" and "VS HUMAN"
    - Center "< BACK" button to return to main menu
    - Ambient background neon particles
    - ESC to return to main menu
    """
    def __init__(self, width=1200, height=700):
        self.width = width
        self.height = height

        self.font = get_pixel_font(76)
        self.title_surf = self.font.render("MODE", True, COLOR_WHITE)
        self.title_rect = self.title_surf.get_rect(center=(width // 2, 175))

        # Main button stack
        self.vs_ai_btn = PlayButton(
            center_x=width // 2,
            center_y=295,
            width=320,
            height=62,
            text="VS AI",
            font_size=24
        )
        self.vs_human_btn = PlayButton(
            center_x=width // 2,
            center_y=385,
            width=320,
            height=62,
            text="VS HUMAN",
            font_size=24
        )
        self.back_btn = PlayButton(
            center_x=width // 2,
            center_y=475,
            width=320,
            height=62,
            text="BACK",
            font_size=24
        )

        self.hint_font = get_old_font(13, bold=True)

        # Ambient floating neon dust particles in the background
        self.ambient_particles = []
        for _ in range(35):
            self.ambient_particles.append(
                Particle(
                    random.uniform(0, width),
                    random.uniform(0, height),
                    random.uniform(-15, 15),
                    random.uniform(-15, 15),
                    random.choice([COLOR_BLUE, COLOR_RED, COLOR_WHITE]),
                    lifetime=random.uniform(3.0, 7.0),
                    size=random.choice([2, 3])
                )
            )

    def update(self, dt, mouse_pos=None):
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        self.vs_ai_btn.update(dt, mouse_pos)
        self.vs_human_btn.update(dt, mouse_pos)
        self.back_btn.update(dt, mouse_pos)

        for p in self.ambient_particles:
            p.update(dt)
            if p.x < 0:
                p.x = self.width
            elif p.x > self.width:
                p.x = 0
            if p.y < 0:
                p.y = self.height
            elif p.y > self.height:
                p.y = 0

            if not p.is_alive():
                p.age = 0.0
                p.x = random.uniform(0, self.width)
                p.y = random.uniform(0, self.height)

    def handle_event(self, event):
        """Returns 'VS_AI', 'VS_HUMAN', 'BACK', or None."""
        if self.vs_ai_btn.handle_event(event):
            return "VS_AI"
        if self.vs_human_btn.handle_event(event):
            return "VS_HUMAN"
        if self.back_btn.handle_event(event):
            return "BACK"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            sound_manager.play_click()
            return "BACK"
        return None

    def draw(self, surface):
        surface.fill(COLOR_BLACK)

        # Ambient background particles
        for p in self.ambient_particles:
            p.draw(surface)

        # Draw Mode Title
        surface.blit(self.title_surf, self.title_rect)

        # Draw Buttons
        self.vs_ai_btn.draw(surface)
        self.vs_human_btn.draw(surface)
        self.back_btn.draw(surface)

        # Footer guide
        hint_text = self.hint_font.render(
            "SELECT GAMEPLAY MODE  |  ESC: BACK TO MENU",
            True,
            (160, 180, 200)
        )
        hint_rect = hint_text.get_rect(center=(self.width // 2, self.height - 40))
        surface.blit(hint_text, hint_rect)


class PauseOverlay:
    """
    Interactive Pause Menu Overlay:
    - Dark semi-transparent backdrop
    - "PAUSED" title
    - "RESUME" button
    - "RESTART" button
    - "CHANGE MODE" button
    - "MAIN MENU" button
    """
    def __init__(self, width=1200, height=700):
        self.width = width
        self.height = height

        self.font = get_pixel_font(60)
        self.title_surf = self.font.render("PAUSED", True, COLOR_BLUE)
        self.title_rect = self.title_surf.get_rect(center=(width // 2, 160))

        center_x = width // 2
        self.resume_btn = PlayButton(center_x=center_x, center_y=255, width=280, height=52, text="RESUME", font_size=20)
        self.restart_btn = PlayButton(center_x=center_x, center_y=325, width=280, height=52, text="RESTART", font_size=20)
        self.mode_btn = PlayButton(center_x=center_x, center_y=395, width=280, height=52, text="CHANGE MODE", font_size=18)
        self.menu_btn = PlayButton(center_x=center_x, center_y=465, width=280, height=52, text="MAIN MENU", font_size=20)

        self.hint_font = get_old_font(13, bold=True)
        self.overlay_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        self.overlay_surf.fill((0, 0, 0, 195))

    def update(self, dt, mouse_pos=None):
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()
        self.resume_btn.update(dt, mouse_pos)
        self.restart_btn.update(dt, mouse_pos)
        self.mode_btn.update(dt, mouse_pos)
        self.menu_btn.update(dt, mouse_pos)

    def handle_event(self, event):
        """Returns 'RESUME', 'RESTART', 'MODE', 'MENU', or None."""
        if self.resume_btn.handle_event(event):
            return "RESUME"
        if self.restart_btn.handle_event(event):
            return "RESTART"
        if self.mode_btn.handle_event(event):
            return "MODE"
        if self.menu_btn.handle_event(event):
            return "MENU"
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_p, pygame.K_ESCAPE):
                sound_manager.play_click()
                return "RESUME"
            elif event.key == pygame.K_r:
                sound_manager.play_click()
                return "RESTART"
        return None

    def draw(self, surface):
        surface.blit(self.overlay_surf, (0, 0))
        surface.blit(self.title_surf, self.title_rect)

        self.resume_btn.draw(surface)
        self.restart_btn.draw(surface)
        self.mode_btn.draw(surface)
        self.menu_btn.draw(surface)

        hint = self.hint_font.render(
            "SPACE: RESUME  |  R: RESTART  |  CLICK BUTTONS TO NAVIGATE",
            True,
            (160, 180, 200)
        )
        surface.blit(hint, hint.get_rect(center=(self.width // 2, self.height - 40)))

