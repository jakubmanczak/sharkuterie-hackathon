import pygame

class Tile:
    def __init__(self, tile_type):
        self.tile_type = tile_type

    def has_collision(self):
        return self.tile_type.wall_collision

    def can_spawn_enemies(self):
        return self.tile_type.spawn_enemies

    def draw(self, surface, x, y, tile_size):
        texture = self.tile_type.texture
        # Scale with 1 extra pixel to prevent gaps
        scaled_texture = pygame.transform.scale(texture, (tile_size, tile_size))
        # Ensure integer coordinates
        surface.blit(scaled_texture, (int(x), int(y)))
