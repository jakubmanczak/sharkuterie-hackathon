import pygame
import math
from src.pellet import Pellet
from src.enemy import Enemy
from src.conductor import Conductor
from src.common import TILE_SIZE
from src.tiletype import TileType
from src.tile import Tile
from src.camera import Camera
from src.player import Player, PlayerState
from src.gamestate import gamestate

class Level:
    def __init__(self, width, height, default_tile_type=None):
        self.width = width
        self.height = height
        self.player = None
        self.camera = None
        self.conductor = Conductor()
        self.rhythm_streak = 0
        self.max_streak = 0
        self.last_hit_time = 0
        self.streak_broken_time = 0
        self.last_checked_beat = 0
        self.has_shown_streak_broken = False
        self.last_had_streak = False

        self.enemies = []
        self.pellets = []
        self.grid = []

        # Initialize grid with default tile type
        for y in range(height):
            row = []
            for x in range(width):
                if default_tile_type:
                    row.append(Tile(default_tile_type))
                else:
                    row.append(None)
            self.grid.append(row)

    def set_tile(self, x, y, tile_type):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = Tile(tile_type)
            return True
        return False

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None

    def add_enemy(self, x, y, health=3, texnum=0):
        enemy = Enemy(x, y, health, texnum)
        self.enemies.append(enemy)
        return enemy

    def add_player(self, x, y):
        # Add a player to the level at tile coordinates x, y
        self.player = Player(x, y)
        return self.player

    def add_pellet(self, x, y, direction):
        """Add a new pellet to the level"""
        self.pellets.append(Pellet(x, y, direction))

    def init_camera(self, view_width, view_height):
        self.camera = Camera(view_width, view_height)
        return self.camera

    def check_level_completion(self):
        """Check if level is complete (all enemies defeated and player at door)"""
        # Check if there are any enemies left
        if not self.enemies:
            # No enemies left, check if player is at the door
            door_x = self.width // 2
            door_y = 0

            # If player is standing in front of the door
            if self.player and self.player.tile_x == door_x and self.player.tile_y == 1:
                return True
        return False

    def transition_to_next_level(self):
        """Handle transition to the next level"""
        gamestate.advance_level()

    def handle_player_movement(self, event):
        # Check for restart if player is dead
        if self.player and self.player.state == PlayerState.DEAD and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Restart the level
                self.player.respawn()

                # Optionally reset enemies
                # if hasattr(self, 'enemies'):
                    # self.enemies = []
                    # Re-add enemies as needed or reset their positions

                return

        if not self.player or self.player.state != PlayerState.IDLE:
            return

        if event.type == pygame.KEYDOWN:
            # Check for shooting with SPACE or ENTER
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.player.shoot(self):  # Call the shoot method
                    # Check if shooting is on beat for rhythm mechanics
                    on_beat = self.conductor.is_on_beat()
                    if not on_beat and self.rhythm_streak > 0:
                        self.streak_broken_time = pygame.time.get_ticks()
                        self.has_shown_streak_broken = True
                        self.last_had_streak = True
                        self.rhythm_streak = 0
                        # Reduce pellets on off-beat shot
                        self.player.reduce_pellets_on_rhythm_break()
                return  # Return after handling shooting

            # Handle movement keys
            dx, dy = 0, 0

            if event.key == pygame.K_UP or event.key == pygame.K_w:
                dx, dy = 0, -1
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                dx, dy = 0, 1
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                dx, dy = -1, 0
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                dx, dy = 1, 0

            # Only proceed if movement key was pressed
            if dx != 0 or dy != 0:
                move_succeeded = self.player.move(dx, dy, self)
                if not move_succeeded:
                    return
                # Check if movement is on beat
                on_beat = self.conductor.is_on_beat()
                self.player.update_pellets(on_beat)

                # Update rhythm stats
                if on_beat:
                    # Register this action with the conductor
                    self.conductor.register_action()

                    # Increment streak
                    self.rhythm_streak += 1
                    self.max_streak = max(self.max_streak, self.rhythm_streak)
                    self.last_hit_time = pygame.time.get_ticks()

                    # Reset streak broken flag when player starts a new streak
                    if self.rhythm_streak == 1:
                        self.has_shown_streak_broken = False
                        self.last_had_streak = False
                else:
                    # Off-beat movement breaks the streak
                    if self.rhythm_streak > 0:
                        self.streak_broken_time = pygame.time.get_ticks()
                        self.has_shown_streak_broken = True
                        self.last_had_streak = True

                        # Reduce pellets when rhythm is broken
                        self.player.reduce_pellets_on_rhythm_break()

                    self.rhythm_streak = 0

    def construct_lvl1(self):
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 and y == 0:
                    self.set_tile(x, y, TileType.WALL_CUL)  # Corner upper left
                elif x == self.width - 1 and y == 0:
                    self.set_tile(x, y, TileType.WALL_CUR)  # Corner upper right
                elif y == 0:
                    self.set_tile(x, y, TileType.WALL01)    # Top wall
                elif x == 0 and y == self.height - 1:
                    self.set_tile(x, y, TileType.WALL_CLL)  # Corner lower left
                elif x == 0:
                    self.set_tile(x, y, TileType.WALL_L)    # Left wall
                elif x == self.width - 1 and y == self.height - 1:
                    self.set_tile(x, y, TileType.WALL_CLR)  # Corner lower right
                elif x == self.width - 1:
                    self.set_tile(x, y, TileType.WALL_R)    # Right wall
                elif y == self.height - 1:
                    self.set_tile(x, y, TileType.WALL_DOWN) # Bottom wall
                else:
                    self.set_tile(x, y, TileType.CARPET)    # Floor inside
        self.set_tile(self.width // 2, 0, TileType.WALL_DOOR)
        self.set_tile(1, 5, TileType.PAPERSTACK)
        self.set_tile(1, 6, TileType.PAPERSTACK)
        self.set_tile(9, 1, TileType.PAPERSTACK)
        self.set_tile(1, 3, TileType.TABLE_TL)
        self.set_tile(2, 3, TileType.TABLE_TR)
        self.set_tile(2, 4, TileType.TABLE_BR)
        self.set_tile(1, 4, TileType.TABLE_BL)
        self.set_tile(8, 3, TileType.TABLE_TL)
        self.set_tile(9, 3, TileType.TABLE_TR)
        self.set_tile(9, 4, TileType.TABLE_BR)
        self.set_tile(8, 4, TileType.TABLE_BL)
        self.add_enemy(3, 6, 1)

    def construct_lvl2(self):
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 and y == 0:
                    self.set_tile(x, y, TileType.WALL_CUL)  # Corner upper left
                elif x == self.width - 1 and y == 0:
                    self.set_tile(x, y, TileType.WALL_CUR)  # Corner upper right
                elif y == 0:
                    self.set_tile(x, y, TileType.WALL01)    # Top wall
                elif x == 0 and y == self.height - 1:
                    self.set_tile(x, y, TileType.WALL_CLL)  # Corner lower left
                elif x == 0:
                    self.set_tile(x, y, TileType.WALL_L)    # Left wall
                elif x == self.width - 1 and y == self.height - 1:
                    self.set_tile(x, y, TileType.WALL_CLR)  # Corner lower right
                elif x == self.width - 1:
                    self.set_tile(x, y, TileType.WALL_R)    # Right wall
                elif y == self.height - 1:
                    self.set_tile(x, y, TileType.WALL_DOWN) # Bottom wall
                else:
                    self.set_tile(x, y, TileType.CARPET)    # Floor inside
        self.set_tile(self.width // 2, 0, TileType.WALL_DOOR)
        self.set_tile(2, 2, TileType.TABLE_TL)
        self.set_tile(3, 2, TileType.TABLE_TR)
        self.set_tile(3, 3, TileType.TABLE_BR)
        self.set_tile(2, 3, TileType.TABLE_BL)
        self.add_enemy(5, 4)
        self.add_enemy(3, 7)
        self.set_tile(7, 5, TileType.TABLE_TL)
        self.set_tile(8, 5, TileType.TABLE_TR)
        self.set_tile(8, 6, TileType.TABLE_BR)
        self.set_tile(7, 6, TileType.TABLE_BL)
        self.set_tile(1, 5, TileType.TABLE_TL)
        self.set_tile(2, 5, TileType.TABLE_TR)
        self.set_tile(2, 6, TileType.TABLE_BR)
        self.set_tile(1, 6, TileType.TABLE_BL)

    def construct_lvl3(self):
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 and y == 0:
                    self.set_tile(x, y, TileType.WALL02_CUL)  # Corner upper left
                elif x == self.width - 1 and y == 0:
                    self.set_tile(x, y, TileType.WALL02_CUR)  # Corner upper right
                elif y == 0:
                    self.set_tile(x, y, TileType.WALL02)    # Top wall
                elif x == 0 and y == self.height - 1:
                    self.set_tile(x, y, TileType.WALL02_CLL)  # Corner lower left
                elif x == 0:
                    self.set_tile(x, y, TileType.WALL02_L)    # Left wall
                elif x == self.width - 1 and y == self.height - 1:
                    self.set_tile(x, y, TileType.WALL02_CLR)  # Corner lower right
                elif x == self.width - 1:
                    self.set_tile(x, y, TileType.WALL02_R)    # Right wall
                elif y == self.height - 1:
                    self.set_tile(x, y, TileType.WALL02_DOWN) # Bottom wall
                else:
                    self.set_tile(x, y, TileType.CARPET)    # Floor inside
        self.set_tile(self.width // 2, 0, TileType.WALL02_DOOR)
        self.add_enemy(3, 6, 10, 11)
        self.set_tile(2, 2, TileType.TABLE_TL)
        self.set_tile(3, 2, TileType.TABLE_TR)
        self.set_tile(3, 3, TileType.TABLE_BR)
        self.set_tile(2, 3, TileType.TABLE_BL)
        self.set_tile(1, 5, TileType.PAPERSTACK)

    def draw_rhythm_ui(self, surface, font):
        # Draw beat indicator
        # beat_indicator_size = 10
        # indicator_x = 25
        # indicator_y = 25

        # Colors for beat indicator - based on current timing (not last hit)
        if self.conductor.is_on_beat():
            if self.conductor.get_perfect_timing():
                color = (255, 255, 0)  # Yellow for perfect timing
            elif self.conductor.current_timing == "EARLY":
                color = (0, 255, 255)  # Cyan for early hits
            elif self.conductor.current_timing == "LATE":
                color = (255, 0, 255)  # Magenta for late hits
            else:
                color = (0, 255, 0)    # Green when on beat
        else:
            color = (255, 0, 0)        # Red when off beat

        # Pulse effect based on beat
        # size = beat_indicator_size * (1 + 0.5 * self.conductor.beat_flash)

        # Draw the indicator
        # pygame.draw.circle(surface, color, (indicator_x, indicator_y), size)

        # Draw streak counter
        # streak_text = f"Streak: {self.rhythm_streak}"
        # text_surface = font.render(streak_text, True, (255, 255, 255))
        # surface.blit(text_surface, (40, 20))

        # Draw max streak
        # if self.max_streak > 0:
            # max_text = f"Best: {self.max_streak}"
            # max_surface = font.render(max_text, True, (220, 220, 220))
            # surface.blit(max_surface, (40, 35))

        # Show timing feedback or streak break message
        current_time = pygame.time.get_ticks()

        # Only show "STREAK BROKEN" if:
        # 1. We just broke a streak (within the last 500ms)
        # 2. We haven't shown the message yet for this sequence of missed beats
        # 3. We actually had a streak to break
        if (current_time - self.streak_broken_time < 500 and
            self.has_shown_streak_broken and
            self.last_had_streak):

            # miss_surface = font.render("STREAK BROKEN!", True, (255, 100, 100))
            # surface.blit(miss_surface, (172, 16))

            # Reset the flag so we don't show it again until a new streak is built
            self.has_shown_streak_broken = False
        if current_time - self.last_hit_time < 500:
            # Show timing feedback - use the captured hit timing, not the current timing
            timing_text = self.conductor.last_hit_timing
            if timing_text and timing_text != "MISS" and timing_text != "NONE":
                if timing_text == "PERFECT":
                    color = (255, 255, 0)  # Yellow for perfect
                elif timing_text == "EARLY":
                    color = (0, 255, 255)  # Cyan for early
                elif timing_text == "LATE":
                    color = (255, 0, 255)  # Magenta for late
                else:
                    color = (255, 255, 255)  # White default

                timing_surface = font.render(timing_text, True, color)
                surface.blit(timing_surface, (164, 0))

    def update(self):
        # Update the conductor
        self.conductor.update()

        # Check if we need to evaluate streak
        current_beat = self.conductor.beat_count

        # Only check for missed beats if a new beat has occurred
        if current_beat > self.last_checked_beat:
            # Check if player acted on the previous beat
            if self.conductor.last_action_beat < self.last_checked_beat:
                # Player missed a beat, reset streak
                if self.rhythm_streak > 0:
                    # Only show the streak broken message if we actually had a streak
                    self.streak_broken_time = pygame.time.get_ticks()
                    self.has_shown_streak_broken = True
                    self.last_had_streak = True

                self.rhythm_streak = 0

            # Update the last checked beat
            self.last_checked_beat = current_beat

        # Existing update code...
        if self.player:
            self.player.update()

        if self.player and self.camera:
            self.camera.center_on(self.player.tile_x, self.player.tile_y, self.width, self.height)
            self.camera.update()

        active_pellets = []
        for pellet in self.pellets:
            pellet.update()

            # Check collisions with walls
            tile_x = int(pellet.x / TILE_SIZE)
            tile_y = int(pellet.y / TILE_SIZE)

            # Check if out of bounds or hitting a wall
            if (tile_x < 0 or tile_x >= self.width or
                tile_y < 0 or tile_y >= self.height or
                (self.get_tile(tile_x, tile_y) and self.get_tile(tile_x, tile_y).has_collision())):
                pellet.active = False

            # Check collisions with enemies
            for enemy in list(self.enemies):  # Use a copy of the list since we might modify it
                if pellet.active and pellet.check_collision(enemy):
                    # Enemy hit
                    if enemy.take_damage():
                        # Enemy killed
                        self.enemies.remove(enemy)
                    break

            if pellet.active:
                active_pellets.append(pellet)

        # Update the pellet list
        self.pellets = active_pellets

        for enemy in self.enemies:
            enemy.update(self, self.conductor)

    def draw(self, surface, font=None):
        # Clear surface with background color
        surface.fill((0, 0, 0))

        if self.camera:
            # Round camera position to nearest pixel
            camera_x = round(self.camera.x)
            camera_y = round(self.camera.y)

            # Calculate visible tiles
            start_tile_x = math.floor(camera_x / TILE_SIZE)
            start_tile_y = math.floor(camera_y / TILE_SIZE)

            # Add buffer tiles
            visible_tiles_x = math.ceil(self.camera.width / TILE_SIZE) + 2
            visible_tiles_y = math.ceil(self.camera.height / TILE_SIZE) + 2

            # Clamp to level boundaries
            start_tile_x = max(0, start_tile_x)
            start_tile_y = max(0, start_tile_y)
            end_tile_x = min(self.width, start_tile_x + visible_tiles_x)
            end_tile_y = min(self.height, start_tile_y + visible_tiles_y)

            # Draw tiles with consistent rounding
            for y in range(start_tile_y, end_tile_y):
                for x in range(start_tile_x, end_tile_x):
                    tile = self.grid[y][x]
                    if tile:
                        draw_x = int(x * TILE_SIZE - camera_x)
                        draw_y = int(y * TILE_SIZE - camera_y)
                        tile.draw(surface, draw_x, draw_y, TILE_SIZE)

            for enemy in self.enemies:
                draw_x = int(enemy.pixel_x - camera_x)
                draw_y = int(enemy.pixel_y - camera_y)
                enemy.draw(surface, draw_x, draw_y)

            for pellet in self.pellets:
                pellet.draw(surface, self.camera.x, self.camera.y)

            # Draw player with consistent positioning
            if self.player:
                player_x = int(self.player.pixel_x - camera_x)
                player_y = int(self.player.pixel_y - camera_y)
                self.player.draw(surface, player_x, player_y)

        if self.player:
            self.player.draw_health(surface)
            self.player.draw_pellet_count(surface, font)

        if font:
            self.draw_rhythm_ui(surface, font)

        if self.player and self.player.state == PlayerState.DEAD:
                game_over_text = "GAME OVER"
                text_surf = font.render(game_over_text, True, (255, 0, 0))
                text_rect = text_surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
                surface.blit(text_surf, text_rect)

                # Draw restart instruction
                restart_text = "Press R to restart"
                restart_surf = font.render(restart_text, True, (255, 255, 255))
                restart_rect = restart_surf.get_rect(center=(surface.get_width() // 2,
                                                             surface.get_height() // 2 + 20))
                surface.blit(restart_surf, restart_rect)
