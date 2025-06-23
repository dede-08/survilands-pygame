import math

import pygame
import constants
import os 

class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.wood = 5

        tree_path = os.path.join('assets', 'images', 'objects', 'tree.png')
        self.image = pygame.image.load(tree_path). convert_alpha()
        self.image = pygame.transform.scale(self.image, (constants.TREE, constants.TREE))
        self.size = self.image.get_width()


    def draw(self, screen, camera_x, camera_y):
        #calcular posicion en pantalla relatica de la camara
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        #solo dibujar si esta en pantalla
        if(screen_x + self.size >= 0 and screen_x <= constants.WIDTH and
           screen_y + self.size >= 0 and screen_y <= constants.HEIGHT):
            screen.blit(self.image, (screen_x, screen_y))

    def chop(self, with_axe = False):
        if self.wood > 0:
            if with_axe:
                self.wood -= 2
                if self.wood < 0:
                    self.wood = 0
            else:
                self.wood -= 1
            return True
        return False

    def is_depleted(self):
        return self.wood <= 0

class SmallStone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.stone = 1

        small_stone_path = os.path.join('assets', 'images', 'objects', 'small_stone2.png')
        self.image = pygame.image.load(small_stone_path). convert_alpha()
        self.image = pygame.transform.scale(self.image, (constants.SMALL_STONE, constants.SMALL_STONE))
        self.size = self.image.get_width()
    
    def draw(self, screen, camera_x, camera_y):
        #calcular posición en pantalla relativa a la camara
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        #solo dibujar si esta en pantalla
        if(screen_x + self.size >= 0 and screen_x <= constants.WIDTH and
           screen_y + self.size >= 0 and screen_y <= constants.HEIGHT):
            screen.blit(self.image, (screen_x, screen_y))

    def collect(self):
        if self.stone > 0:
            self.stone -= 1
            return True
        return False

    def is_depleted(self):
        return self.stone <= 0

class FarmLand:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        farmland_path = os.path.join('assets', 'images', 'objects', 'FarmLand.png')
        self.image = pygame.image.load(farmland_path). convert_alpha()
        self.image = pygame.transform.scale(self.image, (constants.GRASS, constants.GRASS))
        self.size = self.image.get_width()

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        if(screen_x + self.size >= 0 and screen_x <= constants.WIDTH and
                screen_y + self.size >= 0 and screen_y <= constants.HEIGHT):
            screen.blit(self.image, (screen_x, screen_y))

class Water:
    def __init__(self, x, y, is_flowing=False):
        self.x = x
        self.y = y
        self.is_flowing = is_flowing #para diferenciar rios de lagos
        self.is_drinkable = True
        self.size = constants.GRASS
        #para animacion simple
        self.animation_frame = 0
        self.animation_timer = 0

    def update(self, dt):
        #animacion simple del agua
        self.animation_timer += dt
        if self.animation_timer > 500: #cambiar frame cada 500ms
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        if(screen_x + self.size >= 0 and screen_x <= constants.WIDTH and
            screen_y + self.size >= 0 and screen_y <= constants.HEIGHT):
            #crear un rectangulo para el agua
            water_rect = pygame.Rect(screen_x, screen_y, self.size, self.size)

            #aplicar un pequeño offset basado en animation_frame para crear el efecto de ondulacion
            offset_y = math.sin(self.animation_frame * math.pi / 2) * 2

            #dibujar el agua como un rectangulo con el color definido en constants
            pygame.draw.rect(screen, constants.WATER_COLOR, pygame.Rect(screen_x, screen_y + offset_y, self.size, self.size))










