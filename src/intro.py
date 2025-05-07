import pygame
from pygame.event import Event
from src.gamestate import gamestate

# Global variables for the intro state
intro_initialized = False

def handle_intro_events(event: Event):
    # Allow skipping the intro with spacebar
    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        if pygame.mixer.get_init() and pygame.mixer.get_busy():
            pygame.mixer.stop()
        gamestate.change_screen("mainmenu")

def initialize_intro():
    global intro_initialized, intro_music, jmanczak_img, nela_img, michal_img, martyna_img, sharks_img, start_time

    # Initialize pygame mixer if not already done
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    # Load the intro music
    intro_music = pygame.mixer.Sound("./assets/intromusic.mp3")

    # Load images
    jmanczak_img = pygame.image.load("./assets/jmanczak.png").convert_alpha()
    nela_img = pygame.image.load("./assets/nela.png").convert_alpha()
    michal_img = pygame.image.load("./assets/michau_sie_skichau.png").convert_alpha()
    martyna_img = pygame.image.load("./assets/martyna.png").convert_alpha()
    sharks_img = pygame.image.load("./assets/sharks.png").convert_alpha()

    # Play the intro music
    intro_music.play()

    # Record the start time
    start_time = pygame.time.get_ticks()

    intro_initialized = True

def handle_intro_drawing(surface):
    global intro_initialized, font

    # Initialize intro sequence if not already done
    if not intro_initialized:
        initialize_intro()
        # Create font for labels
        font = pygame.font.Font("./assets/Micro_Chat.ttf", 5)

    # Clear the surface
    surface.fill((0, 0, 0))

    # Calculate elapsed time
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - start_time

    # Choose which image to display based on elapsed time
    image_number = 0
    fade_duration = 500  # Time in ms for fade-in effect

    if elapsed_time < 1394:
        current_img = nela_img
        image_start_time = 0
        image_number = 1
    elif elapsed_time < 2298:
        current_img = michal_img
        image_start_time = 1394
        image_number = 2
    elif elapsed_time < 3193:
        current_img = martyna_img
        image_start_time = 2298
        image_number = 3
    elif elapsed_time < 4126:
        current_img = jmanczak_img
        image_start_time = 3193
        image_number = 4
    else:
        current_img = sharks_img
        image_start_time = 4126
        image_number = 5

    # Calculate time since current image started
    image_elapsed_time = elapsed_time - image_start_time

    img_rect = current_img.get_rect()
    if image_number < 5:  # Scale the first four images
        scale_factor = min(surface.get_width() / img_rect.width,
                          surface.get_height() / img_rect.height) * .5
        new_width = int(img_rect.width * scale_factor)
        new_height = int(img_rect.height * scale_factor)
        scaled_img = pygame.transform.scale(current_img, (new_width, new_height))
    else:  # For sharks image, use original size
        new_width = img_rect.width*2
        new_height = img_rect.height*2
        scaled_img = pygame.transform.scale(current_img, (new_width, new_height))  # No scaling applied

    # Create a faded version of the image for the first four images
    if image_number < 5:
        # Calculate alpha (0-255) based on time elapsed for this image
        alpha = min(255, int(255 * image_elapsed_time / fade_duration))

        # Create a copy that supports alpha
        faded_img = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
        faded_img.blit(scaled_img, (0, 0))
        faded_img.set_alpha(alpha)
        scaled_img = faded_img

    # Center the image on screen
    img_x = (surface.get_width() - new_width) // 2
    img_y = (surface.get_height() - new_height) // 2

    # Draw the image
    surface.blit(scaled_img, (img_x, img_y))

    # Draw the text label for each image
    if image_number < 5:  # Only for the first four images
        # Use specific text for each image
        if image_number == 1:
            display_text = "popelnila nela brankiewicz"
        elif image_number == 2:
            display_text = "popelnil michal kamieniak"
        elif image_number == 3:
            display_text = "popelnila martyna kubiak"
        elif image_number == 4:
            display_text = "popelnil jakub manczak"

        text = font.render(display_text, True, (255, 255, 255))
        text_rect = text.get_rect(centerx=surface.get_width() // 2,
                                  top=img_y + new_height + 10)  # 10 pixels below the image

        # Fade in the text along with the image
        text_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        text_surface.blit(text, (0, 0))
        text_surface.set_alpha(alpha)
        surface.blit(text_surface, text_rect)
    elif image_number == 5:  # For the sharks image
        # Text above the image
        top_text = "blahajtron presents"
        text_top = font.render(top_text, True, (255, 255, 255))
        text_top_rect = text_top.get_rect(centerx=surface.get_width() // 2,
                                         bottom=img_y - 10)  # 10 pixels above the image
        surface.blit(text_top, text_top_rect)

        # Text below the image
        bottom_text = "sharkuterie board"
        text_bottom = font.render(bottom_text, True, (255, 255, 255))
        text_bottom_rect = text_bottom.get_rect(centerx=surface.get_width() // 2,
                                              top=img_y + new_height + 10)  # 10 pixels below the image
        surface.blit(text_bottom, text_bottom_rect)

    # Check if music has finished playing
    if not pygame.mixer.get_init() or not pygame.mixer.get_busy():
        # Intro finished, move to main menu
        if elapsed_time >= 500:  # Make sure it's not just initializing
            gamestate.change_screen("mainmenu")
