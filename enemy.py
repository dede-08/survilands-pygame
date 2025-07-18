import math
import world
import pygame
import os
import constants

IDLE_DOWN = 0
IDLE_UP = 1
IDLE_RIGHT = 2
WALK_DOWN = 3
WALK_UP = 4
WALK_RIGHT = 5
BASIC_FRAMES = 6  # igual que el jugador
ANIMATION_DELAY = 100

class Skeleton:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame_size = constants.FRAME_SIZE
        self.sprite_sheet = pygame.image.load(
            os.path.join("assets", "images", "enemies", "Skeleton.png")).convert_alpha()
        self.animations = self.load_animations()
        self.current_state = WALK_DOWN
        self.animation_frame = 0
        self.animation_timer = 0
        self.health = 3
        self.speed = 1
        self.disappearing = False
        self.disappear_alpha = 255

    def load_animations(self):
        animations = {}
        for state in range(6):  # 6 filas: idle/walk (down, up, right)
            frames = []
            for frame in range(BASIC_FRAMES):
                temp = pygame.Surface((self.frame_size, self.frame_size), pygame.SRCALPHA)
                temp.blit(self.sprite_sheet, (0, 0), (frame * self.frame_size, state * self.frame_size, self.frame_size, self.frame_size))
                surface = pygame.transform.scale(temp, (constants.PLAYER, constants.PLAYER))
                frames.append(surface)
            animations[state] = frames
        return animations

    def update_animation(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer > ANIMATION_DELAY:
            self.animation_timer = current_time
            self.animation_frame = (self.animation_frame + 1) % BASIC_FRAMES

    def move_towards_player(self, player, world, others):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            dx /= distance
            dy /= distance

            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed

            #solo moverse si no colisiona con otro esqueleto
            if not self.check_collision(new_x, new_y, others):
                self.x = new_x
                self.y = new_y

            if not self.collides_with_objects(new_x, new_y, world, others):
                self.x = new_x
                self.y = new_y

        #dirección de movimiento para animaciones
        if abs(dx) > abs(dy):
            self.current_state = WALK_RIGHT
            if dx < 0:
                self.facing_left = True
            else:
                self.facing_left = False
        else:
            self.current_state = WALK_UP if dy < 0 else WALK_DOWN

    def check_collision_with_player(self, player):
        if abs(self.x - player.x) < constants.PLAYER and abs(self.y - player.y) < constants.PLAYER:
            current_time = pygame.time.get_ticks()
            if not hasattr(self, 'last_attack') or current_time - self.last_attack > 2000:
                player.current_health -= 1
                self.last_attack = current_time

    def check_collision(self, x, y, others):
        for other in others:
            if other is not self:
                if (x < other.x + self.frame_size and x + self.frame_size > other.x and
                        y < other.y + self.frame_size and y + self.frame_size > other.y):
                    return True
        return False

    def collides_with_objects(self, x, y, world, other_skeletons):
        #verificar colisión con otros esqueletos
        for other in other_skeletons:
            if other is not self:
                if (x < other.x + self.frame_size and x + self.frame_size > other.x and
                        y < other.y + self.frame_size and y + self.frame_size > other.y):
                    return True

        #verificar colisión con árboles
        for tree in world.trees:
            if (x < tree.x + tree.size and x + self.frame_size > tree.x and
                    y < tree.y + tree.size and y + self.frame_size > tree.y):
                return True

        #verificar colisión con piedras pequeñas
        for stone in world.small_stones:
            if (x < stone.x + stone.size and x + self.frame_size > stone.x and
                    y < stone.y + stone.size and y + self.frame_size > stone.y):
                return True

        return False

    def start_disappearing(self):
        self.disappearing = True
        self.disappear_alpha = 255

    def update_disappearance(self):
        if self.disappearing:
            self.disappear_alpha -= 10
            if self.disappear_alpha <= 0:
                return True  # señal para eliminar al esqueleto
        return False

    def draw(self, screen, camera_x, camera_y):
        frame = self.animations[self.current_state][self.animation_frame]
        if getattr(self, "facing_left", False):
            frame = pygame.transform.flip(frame, True, False)

        if self.disappearing:
            frame = frame.copy()
            frame.set_alpha(self.disappear_alpha)

        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        screen.blit(frame, (screen_x, screen_y))
