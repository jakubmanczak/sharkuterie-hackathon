import pygame

class Conductor:
    def __init__(self):
        self.beat_interval = 600
        self.tick_sound = pygame.mixer.Sound("./assets/tick.mp3")
        self.last_beat_time = 0
        self.next_beat_time = 0
        self.audio_delay = 25
        # Window of time considered "on-beat" (ms before and after beat)
        self.beat_window = 125  # ms on either side of beat point
        self.active = False

        # Visual feedback variables
        self.beat_flash = 0  # 0-1 value for visual feedback
        self.flash_duration = 100  # ms

        # For feedback - internal state
        self.current_timing = "NONE"  # Real-time timing state (not for display)

        # For feedback - displayed to player
        self.last_hit_timing = "NONE"  # Captured at moment of action

        # Beat tracking - simplified approach
        self.beat_count = 0
        self.last_action_beat = -1  # Track which beat number the player last acted on

        self.tick_sound.set_volume(.35)

    def start(self):
        if (self.active):
            return
        current_time = pygame.time.get_ticks()
        self.last_beat_time = current_time
        self.next_beat_time = current_time + self.beat_interval
        self.active = True
        self.beat_count = 0
        self.last_action_beat = -1

    def stop(self):
        self.active = False

    def update(self):
        if not self.active:
            return

        current_time = pygame.time.get_ticks()

        # Update beat flash effect
        time_since_last_beat = current_time - self.last_beat_time
        self.beat_flash = max(0, 1 - (time_since_last_beat / self.flash_duration))

        # Check if a new beat occurred
        if current_time >= self.next_beat_time:
            self.tick_sound.play()
            self.last_beat_time = self.next_beat_time
            self.next_beat_time += self.beat_interval
            self.beat_flash = 1.0
            self.beat_count += 1

        # Update current timing status (for internal use only)
        self._update_current_timing()

    def _update_current_timing(self):
        """Updates the current timing status with audio delay compensation"""
        if not self.active:
            self.current_timing = "NONE"
            return

        # Apply audio delay compensation to center the beat window
        current_time = pygame.time.get_ticks() + self.audio_delay

        # Calculate timing relative to the beats
        time_since_last_beat = current_time - self.last_beat_time
        time_until_next_beat = self.next_beat_time - current_time

        # Check if we're within the window of either the previous or next beat
        if time_since_last_beat <= self.beat_window:
            self.current_timing = "LATE"
        elif time_until_next_beat <= self.beat_window:
            self.current_timing = "EARLY"
        else:
            self.current_timing = "MISS"

    def register_action(self):
        """Returns True if the action is on-beat and registers it"""
        if self.is_on_beat():
            # Important: Capture the current timing at the moment of action
            # This is what we'll display to the player
            self.last_hit_timing = self.current_timing

            # Check if we're very close to perfect timing
            if self.get_perfect_timing():
                self.last_hit_timing = "PERFECT"

            self.last_action_beat = self.beat_count
            return True
        else:
            self.last_hit_timing = "MISS"
            return False

    def is_on_beat(self):
        """Returns True if current time is within acceptable window of a beat"""
        return self.current_timing in ("EARLY", "LATE")

    def get_perfect_timing(self):
        """Returns True if timing is very close to perfect beat with audio delay compensation"""
        # Apply audio delay compensation
        current_time = pygame.time.get_ticks() + self.audio_delay

        time_since_last_beat = current_time - self.last_beat_time
        time_until_next_beat = self.next_beat_time - current_time

        # Perfect window is much smaller than general "on-beat" window
        perfect_window = 30  # ms

        return (time_since_last_beat <= perfect_window or
                time_until_next_beat <= perfect_window)
