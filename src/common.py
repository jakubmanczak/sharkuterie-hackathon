import pygame

TILE_SIZE = 24
PLAYER_SIZE = 16
TEXTURE_CACHE = {}

def load_texture(path):
    if path not in TEXTURE_CACHE:
        TEXTURE_CACHE[path] = pygame.image.load(path).convert_alpha()
    return TEXTURE_CACHE[path]
