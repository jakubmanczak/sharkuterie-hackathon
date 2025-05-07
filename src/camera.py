from src.common import TILE_SIZE

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0

        # Simple smoothness factor for 60 FPS
        self.smoothness = 0.1  # Lower = smoother but slower (try 0.05-0.15)

    def center_on(self, target_x, target_y, level_width, level_height):
        # Convert tile coordinates to pixel coordinates for center
        target_pixel_x = target_x * TILE_SIZE + (TILE_SIZE // 2)
        target_pixel_y = target_y * TILE_SIZE + (TILE_SIZE // 2)

        # Calculate desired camera position (center on target)
        desired_x = target_pixel_x - (self.width // 2)
        desired_y = target_pixel_y - (self.height // 2)

        # Clamp to level bounds
        self.target_x = max(0, min(desired_x, level_width * TILE_SIZE - self.width))
        self.target_y = max(0, min(desired_y, level_height * TILE_SIZE - self.height))

    def update(self):
        # Simple linear interpolation at fixed rate
        self.x += (self.target_x - self.x) * self.smoothness
        self.y += (self.target_y - self.y) * self.smoothness
