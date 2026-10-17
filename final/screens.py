
import pygame

pygame.init()

# Screen setup
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("ui test")

clock = pygame.time.Clock()
title_font = pygame.font.Font(None, 256)
font = pygame.font.Font(None, 50)

class Title:
    def __init__(
        self,
        x,
        y,
        text,
        font,
        color=(255, 255, 255),
        hover_color=(0, 0, 0),
        background_color=(0, 0, 0),
        hover_background_color=(255, 255, 255),
        hover_speed=8,
        centered=True,
    ):
        self.x = x
        self.y = y
        self.text = text
        self.font = font

        self.color = color
        self.hover_color = hover_color
        self.background_color = background_color
        self.hover_background_color = hover_background_color

        self.hover_speed = hover_speed
        self.centered = centered

        self.current_color = list(color)
        self.current_background = list(background_color)

        self.rect = pygame.Rect(x, y, 0, 0)
        self.is_hovered = False

    def update(self, dt, mouse_pos=None):
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        self.is_hovered = self.rect.collidepoint(mouse_pos)

        target_color = (
            self.hover_color if self.is_hovered else self.color
        )

        target_background = (
            self.hover_background_color
            if self.is_hovered
            else self.background_color
        )

        factor = min(self.hover_speed * dt, 1.0)

        for i in range(3):
            self.current_color[i] += (
                target_color[i] - self.current_color[i]
            ) * factor

            self.current_background[i] += (
                target_background[i] - self.current_background[i]
            ) * factor

    def draw(self, surface):
        text_surface = self.font.render(
            self.text,
            True,
            tuple(round(c) for c in self.current_color),
        )

        if self.centered:
            self.rect = text_surface.get_rect(
                center=(self.x, self.y)
            )
        else:
            self.rect = text_surface.get_rect(
                topleft=(self.x, self.y)
            )

        # Draw background behind the title
        pygame.draw.rect(
            surface,
            tuple(round(c) for c in self.current_background),
            self.rect,
        )

        surface.blit(text_surface, self.rect)
class Button:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        color=(255, 255, 255),
        border_color=(0, 0, 0),
        hover_color=(0, 0, 0),
        border_width=3,
        border_radius=0,
        hover_speed=8,
        text="",
        font=None,
        text_color=(0, 0, 0),
        hover_text_color=(255, 255, 255),
    ):
        self.rect = pygame.Rect(x, y, width, height)

        self.color = color
        self.border_color = border_color
        self.hover_color = hover_color

        self.border_width = border_width
        self.border_radius = border_radius
        self.hover_speed = hover_speed

        self.text = text
        self.font = font
        self.text_color = text_color
        self.hover_text_color = hover_text_color

        self.current_color = list(color)
        self.current_text_color = list(text_color)

        self.is_hovered = False

    def update(self, dt, mouse_pos=None):
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        self.is_hovered = self.rect.collidepoint(mouse_pos)

        target_color = (
            self.hover_color if self.is_hovered else self.color
        )

        target_text_color = (
            self.hover_text_color
            if self.is_hovered
            else self.text_color
        )

        # Smooth background color animation
        factor = min(self.hover_speed * dt, 1.0)

        for i in range(3):
            self.current_color[i] += (
                target_color[i] - self.current_color[i]
            ) * factor

            # Smooth text color animation
            self.current_text_color[i] += (
                target_text_color[i] - self.current_text_color[i]
            ) * factor

    def draw(self, surface):
        # Draw button background
        pygame.draw.rect(
            surface,
            tuple(round(c) for c in self.current_color),
            self.rect,
            border_radius=self.border_radius,
        )

        # Draw button border
        if self.border_width > 0:
            pygame.draw.rect(
                surface,
                self.border_color,
                self.rect,
                width=self.border_width,
                border_radius=self.border_radius,
            )

        # Draw animated text
        if self.text and self.font:
            text_color = tuple(
                round(c) for c in self.current_text_color
            )

            text_surface = self.font.render(
                self.text,
                True,
                text_color,
            )

            text_rect = text_surface.get_rect(
                center=self.rect.center
            )

            surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True

        return False

if  __name__ == "__main__":
	title = Title(
    x=600,
    y=200,
    text="Pong AI",
    font=title_font,
    color=(255, 255, 255),
    hover_color=(0, 0, 0),
    background_color=(0, 0, 0),
    hover_background_color=(255, 255, 255),
    hover_speed=8,
    centered=True,)

	# Create button
	button = Button(
		x=500,
		y=350,
		width=200,
		height=70,
		color=(0, 0, 0),                 # Black background
		border_color=(255, 255, 255),   # White border
		hover_color=(255, 255, 255),   # White background on hover
		border_width=3,
		border_radius=0,
		hover_speed=8,
		text="Play!",
		font=font,
		text_color=(255, 255, 255),     # White text
		hover_text_color=(0, 0, 0),     # Black text on hover
	)

	# Main loop
	running = True

	while running:
		# Delta time for frame-rate-independent animation
		dt = clock.tick(60) / 1000.0

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			if button.handle_event(event):
				print("Button clicked!")

		# Update animation
		button.update(dt)
		title.update(dt)

		# Draw screen
		screen.fill((0, 0, 0))
		button.draw(screen)
		title.draw(screen)

		pygame.display.flip()

	pygame.quit()
