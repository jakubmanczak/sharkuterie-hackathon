import pygame
import random
import math
import heapq
from enum import Enum
from src.common import TILE_SIZE, load_texture

class EnemyState(Enum):
    IDLE = 0
    MOVING = 1

class Enemy:
    def __init__(self, x, y, health=3, texnum=0):
        self.tile_x = x
        self.tile_y = y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE

        # Randomly select one of the shark sprites
        if texnum == 0:
            shark_num = random.randint(1, 10)
        else:
            shark_num = texnum
        self.texture = load_texture(f"./assets/textures/shark{shark_num}.png")

        # Movement properties
        self.state = EnemyState.IDLE
        self.move_duration = 200
        self.move_start_time = 0
        self.move_progress = 0.0
        self.source_x = 0
        self.source_y = 0
        self.target_x = 0
        self.target_y = 0

        self.max_health = health
        self.current_health = health
        self.hit_flash_time = 0
        self.hit_sound = pygame.mixer.Sound("./assets/Hit10.wav")  # Reuse or add new sound
        self.hit_sound.set_volume(0.5)

        # Beat-based movement
        self.beat_counter = 0
        self.move_frequency = random.choice([2, 3])  # Move every 2nd or 3rd beat
        self.detection_range = 8  # Detection range in tiles

        # Path finding
        self.current_path = []

    def take_damage(self, amount=1):
        """Apply damage to the enemy"""
        self.current_health -= amount
        self.hit_flash_time = pygame.time.get_ticks()
        self.hit_sound.play()

        # Return True if the enemy is dead
        return self.current_health <= 0

    def update(self, level, conductor):
        # Check if it's time to move based on the beat
        if conductor.active and conductor.beat_count > self.beat_counter:
            # A new beat has occurred
            self.beat_counter = conductor.beat_count

            # Only move on certain beats based on move_frequency
            if self.beat_counter % self.move_frequency == 0 and self.state == EnemyState.IDLE:
                # Try to move
                self.move_on_beat(level)

        # Handle movement animation
        if self.state == EnemyState.MOVING:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.move_start_time

            # Calculate progress (0.0 to 1.0)
            self.move_progress = min(1.0, elapsed / self.move_duration)

            if self.move_progress >= 1.0:
                # Movement complete
                self.state = EnemyState.IDLE
                self.pixel_x = self.tile_x * TILE_SIZE
                self.pixel_y = self.tile_y * TILE_SIZE

                # Check if we've landed on the player
                try:
                    if level.player and level.player.tile_x == self.tile_x and level.player.tile_y == self.tile_y:
                        self.collide_with_player(level)
                except Exception as e:
                    print(f"Error in player collision: {e}")
            else:
                # Calculate current position
                src_x = self.source_x * TILE_SIZE
                src_y = self.source_y * TILE_SIZE
                dst_x = self.target_x * TILE_SIZE
                dst_y = self.target_y * TILE_SIZE

                # Linear interpolation
                self.pixel_x = src_x + (dst_x - src_x) * self.move_progress
                self.pixel_y = src_y + (dst_y - src_y) * self.move_progress

    def collide_with_player(self, level):
        """Handle collision with player, dealing damage and pushing them"""
        # Damage the player and pass level for push effect
        if level.player.take_damage(amount=1, level=level):
            # If damage was successful (not invulnerable)
            print(f"Player health: {level.player.current_health}/{level.player.max_health}")

            # Check if player died from this hit
            if level.player.current_health <= 0:
                print("Player died from enemy attack!")

    def move_on_beat(self, level):
        # Check if player is within range
        player_in_range = False
        distance = float('inf')

        if level.player:
            dx = level.player.tile_x - self.tile_x
            dy = level.player.tile_y - self.tile_y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance <= self.detection_range:
                player_in_range = True
                # Recalculate path each time we move when player is in range
                # This ensures we adapt to player movement
                self.current_path = self.find_path_to_player(level)

        # Choose direction
        if player_in_range and self.current_path:
            # Use A* path to move toward player
            return self.follow_path(level)
        else:
            # Move randomly
            return self.move_randomly(level)

    def follow_path(self, level):
        """Move one step along calculated path"""
        # Safety check
        if not self.current_path:
            return self.move_randomly(level)

        # Get the next step in the path (just one step)
        next_x, next_y = self.current_path[0]

        # Calculate direction to move (should only be one step in cardinal direction)
        dx = next_x - self.tile_x
        dy = next_y - self.tile_y

        # Verify we're only moving one tile in a cardinal direction
        if abs(dx) + abs(dy) != 1:
            # Something's wrong with the path - fallback to random movement
            self.current_path = []
            return self.move_randomly(level)

        # Try to move in the calculated direction
        if self.try_move(dx, dy, level):
            # Remove the step we just took
            self.current_path.pop(0)
            return True

        # If movement failed, recalculate path next time
        self.current_path = []
        return False

    def find_path_to_player(self, level):
        """A* pathfinding algorithm to find the best path to the player"""
        if not level.player:
            return []

        start = (self.tile_x, self.tile_y)
        goal = (level.player.tile_x, level.player.tile_y)

        # If already at goal
        if start == goal:
            return []

        # Open and closed sets
        open_set = []
        closed_set = set()

        # Dictionary to store g scores
        g_score = {start: 0}

        # Dictionary to reconstruct path
        came_from = {}

        # F score = g score + heuristic
        f_score = {start: self.heuristic(start, goal)}

        # Push start node to open set
        heapq.heappush(open_set, (f_score[start], start))

        while open_set:
            # Get node with lowest f_score
            _, current = heapq.heappop(open_set)

            # Check if we reached the goal
            if current == goal:
                # Get path but limit to reasonable length
                path = self.reconstruct_path(came_from, current)
                return path

            # Add current to closed set
            closed_set.add(current)

            # Check neighbors (only cardinal directions)
            for neighbor in self.get_neighbors(current, level):
                if neighbor in closed_set:
                    continue

                # Calculate tentative g score
                tentative_g_score = g_score[current] + 1  # Cost is 1 for each step

                # If neighbor not in g_score or we found a better path
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # This path is better, record it
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)

                    # Add to open set if not already there
                    if neighbor not in [node[1] for node in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # No path found
        return []

    def heuristic(self, a, b):
        """Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, pos, level):
        """Get valid neighboring positions (only cardinal directions)"""
        x, y = pos
        neighbors = []

        # Check all 4 cardinal directions (NO DIAGONALS)
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy

            # Check if position is valid
            if (0 <= nx < level.width and
                0 <= ny < level.height):

                # Check if tile allows movement
                tile = level.get_tile(nx, ny)
                if tile and not tile.has_collision():

                    # Check for other enemies (can't pass through them)
                    position_occupied = False
                    if hasattr(level, 'enemies'):
                        for enemy in level.enemies:
                            if enemy != self and enemy.tile_x == nx and enemy.tile_y == ny:
                                position_occupied = True
                                break

                    # Allow movement onto player's tile
                    if not position_occupied:
                        neighbors.append((nx, ny))

        return neighbors

    def reconstruct_path(self, came_from, current):
        """Reconstruct the path from came_from dictionary"""
        total_path = [current]

        while current in came_from:
            current = came_from[current]
            if len(total_path) > 20:  # Safety limit on path length
                break
            total_path.append(current)

        # Reverse to get path from start to goal and remove starting position
        path = total_path[:-1][::-1]
        return path

    def move_randomly(self, level):
        # Choose a random direction
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)

        # Try each direction until one works
        for dx, dy in directions:
            if self.try_move(dx, dy, level):
                return True

        return False

    def try_move(self, dx, dy, level):
        # Ensure we're only moving one step in a cardinal direction
        if abs(dx) + abs(dy) != 1:
            return False

        # Calculate new position
        new_x = self.tile_x + dx
        new_y = self.tile_y + dy

        # Check if movement is valid
        if (0 <= new_x < level.width and
            0 <= new_y < level.height):

            # Check if tile allows movement
            tile = level.get_tile(new_x, new_y)
            if tile and not tile.has_collision():

                # Check if there's already an enemy at this position
                position_occupied = False
                if hasattr(level, 'enemies'):
                    for enemy in level.enemies:
                        if enemy != self and enemy.tile_x == new_x and enemy.tile_y == new_y:
                            position_occupied = True
                            break

                if not position_occupied:
                    self.state = EnemyState.MOVING
                    self.move_start_time = pygame.time.get_ticks()
                    self.move_progress = 0.0

                    self.source_x = self.tile_x
                    self.source_y = self.tile_y
                    self.target_x = new_x
                    self.target_y = new_y

                    self.tile_x = new_x
                    self.tile_y = new_y

                    return True

        return False

    def draw(self, surface, x, y):
        # Apply the centering offset
        centered_x = int(x)
        centered_y = int(y)

        # Apply hit flash effect
        if pygame.time.get_ticks() - self.hit_flash_time < 200:
            # Create a white flash effect
            flash_surface = self.texture.copy()
            flash_surface.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_ADD)
            scaled_texture = pygame.transform.scale(flash_surface, (TILE_SIZE, TILE_SIZE))
        else:
            # Normal rendering
            scaled_texture = pygame.transform.scale(self.texture, (TILE_SIZE, TILE_SIZE))

        surface.blit(scaled_texture, (centered_x, centered_y))
