import pygame
import math
from pygame.event import Event
from src.gamestate import gamestate
from src.common import load_texture

# Global variables for the main menu
menu_initialized = False

def handle_menu_events(event: Event):
    current_time = pygame.time.get_ticks()
    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        if current_time - menu_load_time >= 1000:
            gamestate.change_screen("openingcutscene")

def initialize_menu():
    global menu_initialized, menu_frames, font, start_time, current_frame, last_frame_time, logo_image, menu_load_time

    menu_load_time = pygame.time.get_ticks()

    # Load all 14 menu frames
    menu_frames = []
    for i in range(1, 15):  # Load m1.png through m14.png
        menu_frames.append(load_texture(f"./assets/menu/m{i}.png"))

    # Load the logo
    logo_image = load_texture("./assets/menu/logo.png")

    # Get the font for the text
    font = pygame.font.Font("./assets/Micro_Chat.ttf", 5)

    # Record start time for animations
    start_time = pygame.time.get_ticks()

    # Initialize animation variables
    current_frame = 0
    last_frame_time = pygame.time.get_ticks()

    menu_initialized = True

def handle_menu_drawing(surface):
    global menu_initialized, start_time, current_frame, last_frame_time, menu_frames, logo_image

    # Initialize menu if not already done
    if not menu_initialized:
        initialize_menu()

    # Clear the surface
    surface.fill((0, 0, 0))

    # Update the current frame every 150ms
    current_time = pygame.time.get_ticks()
    if current_time - last_frame_time > 150:
        current_frame = (current_frame + 1) % len(menu_frames)
        last_frame_time = current_time

    # Scale the current frame to fit the surface
    scaled_frame = pygame.transform.scale(menu_frames[current_frame],
                                        (surface.get_width(), surface.get_height()))

    # Draw the current frame
    surface.blit(scaled_frame, (0, 0))

    # Draw the logo at 1:1 scale over the background
    surface.blit(logo_image, (0, 0))

    # Calculate the text opacity (oscillating between 50% and 100%)
    time_passed = (current_time - start_time) / 1000  # Convert to seconds

    # Use sine wave to oscillate alpha from 128 to 255 (50% to 100% opacity)
    alpha = int(128 + 127 * math.sin(time_passed * 2) ** 2)

    # Create text surface
    text_surface = font.render("Press Spacebar to start", True, (255, 255, 255))

    # Create a surface with per-pixel alpha
    text_surface_alpha = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)

    # Blit the text onto the alpha surface with the calculated alpha
    text_surface_alpha.fill((255, 255, 255, alpha))
    text_surface_alpha.blit(text_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Position the text at the lower portion of the screen
    text_rect = text_surface.get_rect(centerx=surface.get_width() // 2,
                                    bottom=surface.get_height() - 20)  # 20 pixels from the bottom

    title_text = font.render("team blahajtron 2025", True, (255, 255, 255))
    title_rect = title_text.get_rect(topright=(surface.get_width() - 5, 5))
    surface.blit(title_text, title_rect)
    title_text = font.render("kogni hackathon", True, (255, 255, 255))
    title_rect = title_text.get_rect(topright=(surface.get_width() - 5, 15))
    surface.blit(title_text, title_rect)

    # Draw the text with fading effect
    surface.blit(text_surface_alpha, text_rect)
