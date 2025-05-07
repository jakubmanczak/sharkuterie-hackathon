class GameState:
    def __init__(self):
        self.screen = "introvideo"
        self.current_level = 0  # 0=no level, 1-3 for actual levels
        self.cutscene_index = 0  # For tracking which cutscene is playing

    def change_screen(self, new_screen):
        self.screen = new_screen

    def advance_level(self):
        self.current_level += 1
        if self.current_level > 3:  # After level 3
            self.change_screen("finalcutscene")
        else:
            self.change_screen("ingame")

gamestate = GameState()
