import pygame
from src.common import TILE_SIZE, load_texture

class Pellet:
    def __init__(self, start_x, start_y, direction, speed=5):
        self.x = start_x
        self.y = start_y
        self.direction = direction  # (dx, dy) normalized direction vector
        self.speed = speed
        self.active = True
        self.damage = 1
        self.lifetime = 2000  # 2 seconds lifetime
        self.spawn_time = pygame.time.get_ticks()

        # Choose a random pellet texture (1-4)
        pellet_num = (pygame.time.get_ticks() % 4) + 1
        self.texture = load_texture(f"./assets/textures/pellet{pellet_num}.png")

    def update(self):
        # Move the pellet
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed

        # Check if pellet has exceeded its lifetime
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.active = False

    def check_collision(self, enemy):
        # Get pellet position in tile coordinates
        pellet_tile_x = int(self.x / TILE_SIZE)
        pellet_tile_y = int(self.y / TILE_SIZE)

        # Check if pellet is in same tile as enemy
        if pellet_tile_x == enemy.tile_x and pellet_tile_y == enemy.tile_y:
            self.active = False
            return True
        return False

    def draw(self, surface, camera_x, camera_y):
        # Draw the pellet at its current position
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y - camera_y)

        # Scale texture to appropriate size (half tile size)
        size = TILE_SIZE // 2
        scaled_texture = pygame.transform.scale(self.texture, (size, size))

        # Center the pellet in its position
        centered_x = draw_x - size // 2
        centered_y = draw_y - size // 2

        surface.blit(scaled_texture, (centered_x, centered_y))
