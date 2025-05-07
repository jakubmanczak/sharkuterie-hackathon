import pygame
import math
from enum import Enum
from src.common import TILE_SIZE, PLAYER_SIZE, load_texture

class PlayerState(Enum):
    IDLE = 0
    MOVING = 1
    HURT = 2  # New state for hurt animation
    DEAD = 3  # New state for death

class PlayerDirection(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class Player:
    def __init__(self, x, y):
        self.tile_x = x
        self.tile_y = y
        self.starting_x = x  # Store starting position for respawn
        self.starting_y = y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE

        # Load textures
        self.texture_down = load_texture("./assets/textures/student01.png")
        self.texture_left = load_texture("./assets/textures/student_l.png")
        self.texture_right = pygame.transform.flip(self.texture_left, True, False)
        self.texture_up = load_texture("./assets/textures/student_u.png")

        # Health system
        self.max_health = 6
        self.current_health = self.max_health
        self.invulnerable = False
        self.invulnerable_time = 0
        self.invulnerable_duration = 1500  # 1.5 seconds of invulnerability after hit
        self.brain_texture = load_texture("./assets/textures/mozg.png")  # Load brain texture for UI
        self.flash_timer = 0  # For hurt animation flashing

        self.hit_sound = pygame.mixer.Sound("./assets/Hit10.wav")
        self.hit_sound.set_volume(0.7)  # Adjust volume as needed

        self.pellets = 0
        self.max_pellets = 12  # Maximum pellets player can hold
        self.pellet_textures = [load_texture(f"./assets/textures/pellet{i}.png") for i in range(1, 5)]
        self.shoot_sound = pygame.mixer.Sound("./assets/Blip3.wav")  # Reuse existing sound or add new one
        self.shoot_sound.set_volume(0.7)

        # Initial direction
        self.direction = PlayerDirection.DOWN

        # Rest of the initialization stays the same
        self.state = PlayerState.IDLE
        self.move_duration = 150
        self.move_start_time = 0
        self.move_progress = 0.0
        self.source_x = 0
        self.source_y = 0
        self.target_x = 0
        self.target_y = 0
        self.move_direction = (0, 0)

    def shoot(self, level):
        """Shoot a pellet in the direction the player is facing"""
        if self.pellets <= 0 or self.state != PlayerState.IDLE:
            return False

        # Determine direction vector based on player facing
        if self.direction == PlayerDirection.UP:
            direction = (0, -1)
        elif self.direction == PlayerDirection.RIGHT:
            direction = (1, 0)
        elif self.direction == PlayerDirection.DOWN:
            direction = (0, 1)
        else:  # LEFT
            direction = (-1, 0)

        # Calculate starting position (center of tile)
        start_x = (self.tile_x + 0.5) * TILE_SIZE
        start_y = (self.tile_y + 0.5) * TILE_SIZE

        # Create pellet and add it to level
        level.add_pellet(start_x, start_y, direction)

        # Decrease pellet count and play sound
        self.pellets -= 1
        self.shoot_sound.play()

        return True

    def update_pellets(self, on_beat_move):
        """Update pellet count based on rhythm"""
        if on_beat_move:
            # Gain exactly 1 pellet for on-beat movement
            self.pellets = min(self.max_pellets, self.pellets + 1)
        else:
            # Lose exactly 2 pellets for off-beat movement
            self.pellets = max(0, self.pellets - 2)

    def reduce_pellets_on_rhythm_break(self):
        """Reduce pellet count when rhythm is broken"""
        pass
        # this was the source of so many woes
        # but the broken must rejoice
        # for the healing shall start when i go to sleep

        # if self.pellets > 4:
        #     self.pellets = self.pellets // 2  # Half if more than 4
        # elif self.pellets > 0:
        #     self.pellets -= 1  # Decrease by 1 if 4 or less

    def draw_pellet_count(self, surface, font):
        icon = pygame.transform.scale(self.pellet_textures[0], (8, 8))
        surface.blit(icon, (6, 24))
        count_text = font.render(f"x{self.pellets}", True, (255, 255, 255))
        surface.blit(count_text, (18, 16))

    def move(self, dx, dy, level, on_beat=False):
        # Don't allow movement if dead
        if self.state == PlayerState.DEAD:
            return False

        # Only accept new movement if currently idle
        if self.state != PlayerState.IDLE:
            return False

        # Update player direction
        if dx > 0:
            self.direction = PlayerDirection.RIGHT
        elif dx < 0:
            self.direction = PlayerDirection.LEFT
        elif dy > 0:
            self.direction = PlayerDirection.DOWN
        elif dy < 0:
            self.direction = PlayerDirection.UP

        # Calculate new position
        new_x = self.tile_x + dx
        new_y = self.tile_y + dy

        # Check if movement is valid
        if (0 <= new_x < level.width and
            0 <= new_y < level.height and
            not level.get_tile(new_x, new_y).has_collision()):

            # Check for enemy collision BEFORE starting movement
            if hasattr(level, 'enemies'):
                for enemy in level.enemies:
                    if enemy.tile_x == new_x and enemy.tile_y == new_y:
                        # Just take damage but DON'T move into the enemy
                        if self.take_damage(amount=1, level=level):
                            # Check if player died from this collision
                            if self.current_health <= 0:
                                self.state = PlayerState.DEAD
                        return False  # Cancel the movement entirely

            # No enemy collision, proceed with movement
            self.move_duration = 200  # Fixed duration for all moves

            self.state = PlayerState.MOVING
            self.move_start_time = pygame.time.get_ticks()
            self.move_progress = 0.0

            self.source_x = self.tile_x
            self.source_y = self.tile_y
            self.target_x = new_x
            self.target_y = new_y
            self.move_direction = (dx, dy)

            self.tile_x = new_x
            self.tile_y = new_y

            return True
        return False

    def take_damage(self, amount=1, level=None):
        """Handle player taking damage with invulnerability period"""
        # If player is invulnerable, don't take damage
        if self.invulnerable or self.state == PlayerState.DEAD:
            return False

        # Play hit sound effect
        self.hit_sound.play()

        # Reduce health
        self.current_health -= amount

        # Play hurt sound or animation
        self.state = PlayerState.HURT
        self.flash_timer = pygame.time.get_ticks()

        # Start invulnerability period
        self.invulnerable = True
        self.invulnerable_time = pygame.time.get_ticks()

        # Push player in random direction if level is provided
        if level is not None:
            self.push_in_random_direction(level)

        # Check if player died
        if self.current_health <= 0:
            self.current_health = 0
            self.state = PlayerState.DEAD
            print("Player died!")

        return True

    def respawn(self):
        """Respawn the player at starting position with full health"""
        self.tile_x = self.starting_x
        self.tile_y = self.starting_y
        self.pixel_x = self.tile_x * TILE_SIZE
        self.pixel_y = self.tile_y * TILE_SIZE
        self.current_health = self.max_health
        self.state = PlayerState.IDLE
        self.invulnerable = True
        self.invulnerable_time = pygame.time.get_ticks()

    def get_current_texture(self):
        # Return the appropriate texture based on direction
        if self.direction == PlayerDirection.LEFT:
            return self.texture_left
        elif self.direction == PlayerDirection.RIGHT:
            return self.texture_right
        elif self.direction == PlayerDirection.UP:
            return self.texture_up
        else:
            return self.texture_down

    def push_in_random_direction(self, level):
        """Push the player in a random direction after being hit"""
        import random

        # Generate random directions (up, right, down, left)
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        random.shuffle(directions)

        # Try each direction until one works
        for dx, dy in directions:
            new_x = self.tile_x + dx
            new_y = self.tile_y + dy

            # Verify the move is valid
            if (0 <= new_x < level.width and
                0 <= new_y < level.height and
                not level.get_tile(new_x, new_y).has_collision()):

                # Set up the movement
                self.state = PlayerState.MOVING
                self.move_start_time = pygame.time.get_ticks()
                self.move_progress = 0.0

                self.source_x = self.tile_x
                self.source_y = self.tile_y
                self.target_x = new_x
                self.target_y = new_y
                self.move_direction = (dx, dy)

                # Update player position
                self.tile_x = new_x
                self.tile_y = new_y

                # We found a valid direction, so stop trying
                return True

        # If no valid direction found, don't move
        return False

    def update(self):
        current_time = pygame.time.get_ticks()

        # Update invulnerability status
        if self.invulnerable and current_time - self.invulnerable_time > self.invulnerable_duration:
            self.invulnerable = False

        # Update hurt state
        if self.state == PlayerState.HURT and current_time - self.flash_timer > 300:
            # Transition back to IDLE after hurt animation
            if self.current_health > 0:
                self.state = PlayerState.IDLE

        # Handle movement animation
        if self.state == PlayerState.MOVING:
            elapsed = current_time - self.move_start_time

            # Calculate progress (0.0 to 1.0)
            self.move_progress = min(1.0, elapsed / self.move_duration)

            if self.move_progress >= 1.0:
                # Movement complete
                self.state = PlayerState.IDLE
                self.pixel_x = self.tile_x * TILE_SIZE
                self.pixel_y = self.tile_y * TILE_SIZE
            else:
                # Calculate current position with arc
                src_x = self.source_x * TILE_SIZE
                src_y = self.source_y * TILE_SIZE
                dst_x = self.target_x * TILE_SIZE
                dst_y = self.target_y * TILE_SIZE

                # Linear interpolation for the base movement
                self.pixel_x = src_x + (dst_x - src_x) * self.move_progress
                self.pixel_y = src_y + (dst_y - src_y) * self.move_progress

                # Add arc effect - highest at the middle of movement
                arc_height = 5.0  # maximum height of arc in pixels
                arc_offset = arc_height * math.sin(self.move_progress * math.pi)
                self.pixel_y -= arc_offset

    def draw(self, surface, x, y):
        # Don't draw if dead (or implement death animation)
        if self.state == PlayerState.DEAD:
            return

        # Get the current texture based on direction
        texture = self.get_current_texture()

        # Calculate centering offsets to position the player in the middle of the tile
        offset_x = (TILE_SIZE - PLAYER_SIZE) // 2
        offset_y = (TILE_SIZE - PLAYER_SIZE) // 2

        # Apply the centering offset
        centered_x = int(x) + offset_x
        centered_y = int(y) + offset_y

        # Apply hurt/invulnerable flashing effect
        should_draw = True
        if self.invulnerable:
            # Flash every 100ms while invulnerable
            should_draw = (pygame.time.get_ticks() // 100) % 2 == 0

        if should_draw:
            # Scale to proper player size (16x16), not full tile size
            scaled_texture = pygame.transform.scale(texture, (PLAYER_SIZE, PLAYER_SIZE))
            surface.blit(scaled_texture, (centered_x, centered_y))

    def draw_health(self, surface):
        """Draw the health UI with brain icons"""
        brain_size = 16
        padding = 4
        start_x = 4
        start_y = 4

        # Draw brain icons
        for i in range(self.max_health):
            brain_x = start_x + i * (brain_size + padding)

            # Scale the brain texture
            scaled_brain = pygame.transform.scale(self.brain_texture, (brain_size, brain_size))

            if i < self.current_health:
                # Draw full brain for current health
                surface.blit(scaled_brain, (brain_x, start_y))
            else:
                # Draw empty outline for lost health
                # Create a slightly transparent version for empty slots
                empty_brain = scaled_brain.copy()
                empty_brain.set_alpha(80)  # Make semi-transparent
                surface.blit(empty_brain, (brain_x, start_y))
