import pygame
from src.gamestate import gamestate

# Define the dialogue for each cutscene
opening_cutscene_dialogue = [
    "...",
    "Nazywam sie Input i jestem studentem pierwszego roku Kognitywistyki.",
    "Nienawidze rodzicow za to jak mnie nazwali.",
    "Wracajac. ",
    "Wracajac. Nie zaliczylem logiki.",
    "Nie zamierzam wyleciec ze studiow, wiec ide na dyzur do dr. Radzia.",
    "Nie zamierzam wyleciec ze studiow, wiec ide na dyzur do dr. Radzia. Bede go blagac na kolanach o ostatnia szanse.",
    "Ale podchodzac do gabinetu, na drzwiach spostrzegam kartke.",
    "\"Doktor Radz zostal porwany!\"",
    "\"Doktor Radz zostal porwany! Przetrzymuja go w ostatnim pokoju.\"",
    "To moja jedyna szansa na zdanie przedmiotu. Musze go uratowac."
]

final_cutscene_dialogue = [
    "Dr. Mateusz Radz: dziekuje Input! Uratowales mnie.",
    "Dr. Mateusz Radz: dziekuje Input! Uratowales mnie. Zasluzyles na ocene dostateczna z logiki.",
    "...Nie zebys mial przejsc do drugiego semestru, bo z tego co wiem nie zdajesz z Matematyki."
]

class CutsceneHandler:
    def __init__(self, dialogue_list):
        self.dialogue = dialogue_list
        self.current_line = 0
        self.font = pygame.font.Font("./assets/Micro_Chat.ttf", 5)
        self.background = pygame.image.load("./assets/textures/dywan.png")
        self.last_advance_time = 0
        self.cooldown_ms = 350

    def handle_events(self, event):
        current_time = pygame.time.get_ticks()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # Check if enough time has passed since the last advance
            if current_time - self.last_advance_time >= self.cooldown_ms:
                self.advance_dialogue()
                self.last_advance_time = current_time

    def advance_dialogue(self):
        self.current_line += 1
        if self.current_line >= len(self.dialogue):
            # Cutscene finished
            self.current_line = 0
            if gamestate.screen == "openingcutscene":
                gamestate.current_level = 1
                gamestate.change_screen("ingame")
            elif gamestate.screen == "finalcutscene":
                gamestate.change_screen("mainmenu")

    def draw(self, surface):
        # Draw tiled background
        bg_width = self.background.get_width()
        bg_height = self.background.get_height()
        for y in range(0, surface.get_height(), bg_height):
            for x in range(0, surface.get_width(), bg_width):
                surface.blit(self.background, (x, y))

        # Draw current dialogue
        if self.current_line < len(self.dialogue):
            text = self.dialogue[self.current_line]
            # Create a rectangle that covers most of the screen for text rendering
            text_area = pygame.Rect(40, 40, surface.get_width() - 80, surface.get_height() - 80)
            self.draw_wrapped_text(surface, text, text_area)

            # Draw prompt
            prompt_font = pygame.font.Font("./assets/Micro_Chat.ttf", 5)
            prompt = prompt_font.render("Press SPACE to continue", True, (255, 255, 255))
            surface.blit(prompt, (surface.get_width() - prompt.get_width() - 20,
                                 surface.get_height() - prompt.get_height() - 20))

    def draw_wrapped_text(self, surface, text, rect, color=(255, 255, 255)):
        # Split speaker from dialogue
        parts = text.split(": ", 1)

        current_x = rect.x
        current_y = rect.y
        line_height = self.font.get_height() + 5

        if len(parts) == 2:
            speaker, message = parts
            # Draw speaker name in yellow
            speaker_text = speaker + ": "
            speaker_surface = self.font.render(speaker_text, True, (255, 255, 0))
            surface.blit(speaker_surface, (current_x, current_y))

            # Update position after speaker name
            current_x += speaker_surface.get_width()

            # Draw the message with word wrapping
            words = message.split(' ')

            for word in words:
                # Render the word to get its width
                word_surface = self.font.render(word, True, color)
                word_width = word_surface.get_width()

                # Check if adding this word would exceed the rect width
                if current_x + word_width > rect.right:
                    # Move to the next line
                    current_x = rect.x
                    current_y += line_height

                # Draw the word at the current position
                surface.blit(word_surface, (current_x, current_y))

                # Move position for next word (add space)
                current_x += word_width + self.font.size(' ')[0]

        else:
            # Just a single line with no speaker
            words = text.split(' ')

            for word in words:
                word_surface = self.font.render(word, True, color)
                word_width = word_surface.get_width()

                if current_x + word_width > rect.right:
                    current_x = rect.x
                    current_y += line_height

                surface.blit(word_surface, (current_x, current_y))
                current_x += word_width + self.font.size(' ')[0]
