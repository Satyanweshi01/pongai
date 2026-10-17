
class Config:
    def __init__(self,width,height):
        self.WINDOW_WIDTH = width
        self.WINDOW_HEIGHT = height

        # Reference resolution
        self.BASE_WIDTH = 1200
        self.BASE_HEIGHT = 700

        # Scaling factors
        self.SCALE_X = self.WINDOW_WIDTH / self.BASE_WIDTH
        self.SCALE_Y = self.WINDOW_HEIGHT / self.BASE_HEIGHT
        self.SCALE = min(self.SCALE_X, self.SCALE_Y)

        # Bat dimensions
        self.BAT_WIDTH = round(20 * self.SCALE)
        self.BAT_HEIGHT = round(100 * self.SCALE)
        self.BAT_SENSITIVITY = round(15 * self.SCALE)

        # Ball settings
        self.BALL_RADIUS = round(10 * self.SCALE)
        self.BALL_SPEED_SCALE = max(0.4, self.SCALE)
        self.BALL_SPEED = 5 * self.BALL_SPEED_SCALE

        # Screen center
        self.CENTER_X = self.WINDOW_WIDTH // 2
        self.CENTER_Y = self.WINDOW_HEIGHT // 2

        # Boundaries
        self.WALL_LEFT_BOUNDARY = -self.BALL_RADIUS * 2
        self.WALL_RIGHT_BOUNDARY = self.WINDOW_WIDTH
        self.WALL_TOP_BOUNDARY = 0
        self.WALL_BOTTOM_BOUNDARY = self.WINDOW_HEIGHT

        self.BAT_TOP_BOUNDARY = 0
        self.BAT_BOTTOM_BOUNDARY = self.WINDOW_HEIGHT - self.BAT_HEIGHT

