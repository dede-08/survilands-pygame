import pygame
import constants
import os
from constants import *
from inventory import Inventory

class Character: 
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.inventory = Inventory()
        self.max_health = 10
        self.current_health = 10
        self.last_damage_time = pygame.time.get_ticks()

        #cargar hoja de sprite
        image_path = os.path.join('assets', 'images', 'character', 'Player.png')
        self.sprite_sheet = pygame.image.load(image_path).convert_alpha()
        #cargar hoja de sprites de animacion de hacha
        self.action_sprite_sheet = pygame.image.load(
            os.path.join('assets', 'images', 'character', 'Player_Actions.png')
        ).convert_alpha()

        #cargar imagen del corazón
        self.heart_full = pygame.image.load(os.path.join("assets", "images", "interface", "heart.png")).convert_alpha()
        self.heart_empty = pygame.image.load(os.path.join("assets", "images", "interface", "heart_empty.png")).convert_alpha()

        #escalarlas si es necesario (por ejemplo, 32x32 px)
        self.heart_full = pygame.transform.scale(self.heart_full, (24, 24))
        self.heart_empty = pygame.transform.scale(self.heart_empty, (24, 24))

        #animacion properties
        self.frame_size = FRAME_SIZE
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_delay = ANIMATION_DELAY
        self.current_state = IDLE_DOWN
        self.moving = False
        self.facing_left = False
        self.is_running = False
        #agregar propiedades de animacion del hacha y azada
        self.is_chopping = False
        self.chop_timer = 0
        self.chop_frame = 0
        self.is_hoeing = False
        self.hoe_timer = 0
        self.hoe_frame = 0


        #load all animations frames
        self.animations = self.load_animations()
        # cargar animaciones del hacha
        self.axe_animations = self.load_axe_animations()
        self.hoe_animations = self.load_hoe_animations()

        self.item_images = {
            "wood": self.load_item_image("wood.png"),
            "stone": self.load_item_image("small_stone.png")
        }

        self.energy = constants.MAX_ENERGY
        self.food = constants.MAX_FOOD
        self.thirst = constants.MAX_THIRST
        self.stamina = constants.MAX_STAMINA


    def load_animations(self):
        animations = {}
        for state in range(6): #6 animations states
            frames = []
            for frame in range(BASIC_FRAMES): #6 frames per animation
                temp_surface = pygame.Surface((self.frame_size ,self.frame_size), pygame.SRCALPHA)
                temp_surface.blit(self.sprite_sheet, (0, 0), (frame * self.frame_size, state * self.frame_size, self.frame_size, self.frame_size))

                #create final surface at player size
                surface = pygame.Surface((constants.PLAYER, constants.PLAYER), pygame.SRCALPHA)
                #scale and blit the temp surface onto the final surface
                scaled_temp = pygame.transform.scale(temp_surface, (constants.PLAYER, constants.PLAYER))
                surface.blit(scaled_temp, (0, 0))
                #if constants.PLAYER != self.frame_size:
                    #surface = pygame.transform.scale(surface, (constants.PLAYER, constants.PLAYER))
                frames.append(surface)
            animations[state] = frames
        return animations

    def load_axe_animations(self):
        animations = {}
        # map the sprite sheet rows to animation states
        # row 4 (index 3) for right-facing
        # row 5 (index 4) for down-facing
        # row 6 (index 5) for up-facing
        row_mapping = {
            3: 3, #right-facing animations in row 4
            4: 4, #down-facing animations in row 5
            5: 5  #up-facing animations in row 6
        }

        for state, row in row_mapping.items():
            frames = []
            for frame in range(AXE_FRAMES):
                #create a temporary surface to hold the frame
                temp_surface = pygame.Surface((constants.ACTION_FRAME_SIZE, constants.ACTION_FRAME_SIZE), pygame.SRCALPHA)
                #calculate x position based on frame number and colums
                x = (frame % AXE_COLS) * constants.ACTION_FRAME_SIZE
                #get the frame from the correct position in the sprite sheet
                frame_rect = pygame.Rect(x, row * constants.ACTION_FRAME_SIZE,
                                         constants.ACTION_FRAME_SIZE,
                                         constants.ACTION_FRAME_SIZE)

                #draw the frame onto the temporary surface
                temp_surface.blit(self.action_sprite_sheet, (0, 0), frame_rect)

                #calculate the proper size for action frames
                action_scale = constants.ACTION_FRAME_SIZE / constants.FRAME_SIZE
                action_size = int(constants.PLAYER * action_scale)

                #create the final surface at the scaled action size
                surface = pygame.Surface((action_size, action_size), pygame.SRCALPHA)

                #scale and blit the temp surface onto the final surface
                scaled_temp = pygame.transform.scale(temp_surface, (action_size, action_size))
                surface.blit(scaled_temp, (0, 0))

                frames.append(surface)
            animations[state] = frames
        return animations

    def load_hoe_animations(self):
        animations = {}
        # map the sprite sheet rows to animation states
        # row 4 (index 3) for right-facing
        # row 5 (index 4) for down-facing
        # row 6 (index 5) for up-facing
        row_mapping = {
            6: 6, #right-facing animations in row 4
            7: 7, #down-facing animations in row 5
            8: 8  #up-facing animations in row 6
        }

        for state, row in row_mapping.items():
            frames = []
            for frame in range(HOE_FRAMES):
                #create a temporary surface to hold the frame
                temp_surface = pygame.Surface((constants.ACTION_FRAME_SIZE, constants.ACTION_FRAME_SIZE), pygame.SRCALPHA)
                #calculate x position based on frame number and colums
                x = (frame % HOE_COLS) * constants.ACTION_FRAME_SIZE
                #get the frame from the correct position in the sprite sheet
                frame_rect = pygame.Rect(x, row * constants.ACTION_FRAME_SIZE,
                                         constants.ACTION_FRAME_SIZE,
                                         constants.ACTION_FRAME_SIZE)

                #draw the frame onto the temporary surface
                temp_surface.blit(self.action_sprite_sheet, (0, 0), frame_rect)

                #calculate the proper size for action frames
                action_scale = constants.ACTION_FRAME_SIZE / constants.FRAME_SIZE
                action_size = int(constants.PLAYER * action_scale)

                #create the final surface at the scaled action size
                surface = pygame.Surface((action_size, action_size), pygame.SRCALPHA)

                #scale and blit the temp surface onto the final surface
                scaled_temp = pygame.transform.scale(temp_surface, (action_size, action_size))
                surface.blit(scaled_temp, (0, 0))

                frames.append(surface)
            animations[state] = frames
        return animations
    
    def update_animations(self):
        current_time = pygame.time.get_ticks()

        if self.is_chopping:
            if current_time - self.chop_timer > AXE_ANIMATION_DELAY:
                self.chop_timer = current_time
                self.chop_frame = (self.chop_frame + 1) % AXE_FRAMES
                if self.chop_frame == 0: #animation completed
                    self.is_chopping = False
        elif self.is_hoeing:
            if current_time - self.hoe_timer > HOE_ANIMATION_DELAY:
                self.hoe_timer = current_time
                self.hoe_frame = (self.hoe_frame + 1) % HOE_FRAMES
                if self.hoe_frame == 0:
                    self.is_hoeing = False
        else:
            #ajustar la velocidad de animacion segun si está corriendo o caminando
            animation_speed = RUNNING_ANIMATION_DELAY if self.is_running else ANIMATION_DELAY
            if current_time - self.animation_timer > animation_speed:
                self.animation_timer = current_time
                self.animation_frame = (self.animation_frame + 1) % 6

    def load_item_image(self, filename):
        path = os.path.join('assets', 'images', 'objects', filename)
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (40, 40))

    def draw(self, screen, camera_x, camera_y):
        #calcular posicion en pantalla relativa a la camara 
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y



        if self.is_chopping:
            if self.current_state in [IDLE_RIGHT, WALK_RIGHT]:
                current_frame = self.axe_animations[3][self.chop_frame]
                if self.facing_left:
                    current_frame = pygame.transform.flip(current_frame, True, False)
            elif self.current_state in [IDLE_DOWN, WALK_DOWN]:
                current_frame = self.axe_animations[4][self.chop_frame]
            elif self.current_state in [IDLE_UP, WALK_UP]:
                current_frame = self.axe_animations[5][self.chop_frame]
        elif self.is_hoeing:
            if self.current_state in [IDLE_RIGHT, WALK_RIGHT]:
                current_frame = self.hoe_animations[6][self.hoe_frame]
                if self.facing_left:
                    current_frame = pygame.transform.flip(current_frame, True, False)
            elif self.current_state in [IDLE_DOWN, WALK_DOWN]:
                current_frame = self.hoe_animations[7][self.hoe_frame]
            elif self.current_state in [IDLE_UP, WALK_UP]:
                current_frame = self.hoe_animations[8][self.hoe_frame]
        else:
            current_frame = self.animations[self.current_state][self.animation_frame]
            if self.facing_left:
                current_frame = pygame.transform.flip(current_frame, True, False)

        if self.is_chopping:
            action_scale = constants.ACTION_FRAME_SIZE / constants.FRAME_SIZE
            size_diff = int(constants.PLAYER * (action_scale - 1))
            screen.blit(current_frame, (screen_x - size_diff // 2, screen_y - size_diff // 2))
        else:
            screen.blit(current_frame, (screen_x, screen_y))
        self.draw_status_bars(screen)

    def is_in_water(self, world):
        #verificar si el personaje esta en el agua
        return world.is_water_at(self.x + constants.PLAYER // 2, self.y + constants.PLAYER // 2)

    def move(self, dx, dy, world):
        self.moving = dx != 0 or dy != 0

        if self.moving:
            #ajustar la animacion segun si está corriendo o caminando
            speed_multiplier = RUN_SPEED if self.is_running and self.stamina > 0 else WALK_SPEED

            #redicir velocidad si esta en el agua
            if self.is_in_water(world):
                speed_multiplier *= constants.WATER_MOVEMENT_MULTIPLIER

            dx *= speed_multiplier / WALK_SPEED
            dy *= speed_multiplier / WALK_SPEED
            if dy > 0:
                self.current_state = WALK_DOWN
                self.facing_left = False
            elif dy < 0:
                self.current_state = WALK_UP
                self.facing_left = False
            elif dx > 0:
                self.current_state = WALK_RIGHT
                self.facing_left = False
            elif dx < 0:
                self.current_state = WALK_RIGHT
                self.facing_left = True
        else:
            if self.current_state == WALK_DOWN:
                self.current_state = IDLE_DOWN
            elif self.current_state == WALK_UP:
                self.current_state = IDLE_UP
            elif self.current_state == WALK_RIGHT:
                self.current_state = IDLE_RIGHT

        new_x = self.x + dx
        new_y = self.y + dy

        for tree in world.trees:
            if self.check_collition(new_x, new_y, tree):
                self.moving = False
                return
            
        self.x = new_x
        self.y = new_y

        self.update_animations()

        #cuando se mueve pierde energia
        if self.moving:
            if self.is_running and self.stamina > 0:
                self.update_stamina(-STAMINA_DECREASE_RATE)
                self.update_energy(-MOVEMENT_ENERGY_COST * 2)
            else:
                self.update_energy(-MOVEMENT_ENERGY_COST)
                if not self.moving:
                    self.update_stamina(STAMINA_INCREASE_RATE)

    def check_collition(self, x, y, obj):
        return (x < obj.x + obj.size*.75 and x + constants.PLAYER*.75 > obj.x and 
                y < obj.y + obj.size*.75 and y + constants.PLAYER*.75 > obj.y)
    
    def is_near(self, obj):
        return(abs(self.x - obj.x) <= max(constants.PLAYER, obj.size) + 5 and 
               abs(self.y - obj.y) <= max(constants.PLAYER, obj.size) + 5)
    
    def interact(self, world):
        #check if 'e' key is pressing and hoe is equipped
        keys = pygame.key.get_pressed()

        #verificar si tiene cubeta llena equipada
        water_bucket_equipped, hand = self.inventory.has_water_bucket_equipped()
        if water_bucket_equipped and keys[pygame.K_e]:
            #obtener posicion de casilla donde está parado el jugador
            grid_x = (self.x // constants.GRASS) * constants.GRASS
            grid_y = (self.y // constants.GRASS) * constants.GRASS

            #verificar si hay tierra de cultivo en esta posicion
            farmland = world.get_farmland_at(grid_x, grid_y)
            if farmland:
                if farmland.water():
                    #vaciar el cubo despues de regar
                    self.inventory.empty_bucket(hand)
                    return
            #si no encuentra tierra de cultivo o ya está regada, simplemente vaciar el cubo
            self.inventory.empty_bucket(hand)
            return



        #si está en el agua, verificar si tiene la cubeta equipada
        if keys[pygame.K_e] and self.is_in_water(world):
            #verificar si tiene la cubeta equipada
            bucket_equipped, hand = self.inventory.has_bucket_equipped()
            if bucket_equipped:
                #llenar la cubeta
                self.inventory.fill_bucket(hand)
                return
            #si no tiene cubeta, solo beber agua
            self.update_thirst(constants.WATER_THIRST_RECOVERY)
            return
        #restaurar salud si comida y sed están al máximo
        if self.food >= constants.MAX_FOOD and self.thirst >= constants.MAX_THIRST:
            if self.current_health < self.max_health:
                self.current_health += 1


        #si tiene la azada equipada, usar la azada
        if keys[pygame.K_e] and self.inventory.has_hoe_equipped():
            self.is_hoeing = True
            self.hoe_timer = pygame.time.get_ticks()
            self.hoe_frame = 0
            #intentar crear tierra de cultivo en la posicion actual
            world.add_farmland(self.x, self.y)
            return

        #verificar si podemos cosechar los cultivos presionando E
        if keys[pygame.K_e]:
            grid_x = (self.x // constants.GRASS) * constants.GRASS
            grid_y = (self.y // constants.GRASS) * constants.GRASS
            farmland = world.get_farmland_at(grid_x, grid_y)
            if farmland and farmland.harvest():
                self.inventory.add_item('carrot')
                return

        for tree in world.trees:
            if self.is_near(tree):
                has_axe = self.inventory.has_axe_equipped()
                if has_axe:
                    self.is_chopping = True
                    self.chop_timer = pygame.time.get_ticks()
                    self.chop_frame = 0
                if tree.chop(with_axe = has_axe):
                    self.inventory.add_item('wood')
                return

        #comer zanahoria si está equipada y presiona E
        if keys[pygame.K_e]:
            if self.inventory.left_hand and self.inventory.left_hand.name == 'carrot':
                self.update_food(5)
                self.inventory.left_hand.quantity -= 1
                if self.inventory.left_hand.quantity <= 0:
                    self.inventory.left_hand = None
                #restaurar salud si comida y sed están al máximo
                if self.food >= constants.MAX_FOOD and self.thirst >= constants.MAX_THIRST:
                    if self.current_health < self.max_health:
                        self.current_health += 1
                return
            elif self.inventory.right_hand and self.inventory.right_hand.name == 'carrot':
                self.update_food(5)
                self.inventory.right_hand.quantity -= 1
                if self.inventory.right_hand.quantity <= 0:
                    self.inventory.right_hand = None
                # restaurar salud si comida y sed están al máximo
                if self.food >= constants.MAX_FOOD and self.thirst >= constants.MAX_THIRST:
                    if self.current_health < self.max_health:
                        self.current_health += 1
                return

        for stone in world.small_stones:
            if self.is_near(stone):
                if stone.collect():
                    self.inventory.add_item('stone')
                return
            
    def draw_inventory(self, screen ,show_inventory = False):
        #dibujar el inventario
        self.inventory.draw(screen, show_inventory)

        #texto de cierre si el inventario está abierto
        if show_inventory:
            font = pygame.font.Font(None, 24)
            close_text = font.render("Press 'I' to close inventory", True, constants.WHITE)
            screen.blit(close_text, (constants.WIDTH // 2 - close_text.get_width() // 2, constants.HEIGHT - 40))
    
    def update_energy(self, amount):
        self.energy = max(0, min(self.energy + amount, constants.MAX_ENERGY))

    def update_food(self, amount):
        self.food = max(0, min(self.food + amount, constants.MAX_FOOD))

    def update_thirst(self, amount):
        self.thirst = max(0, min(self.thirst + amount, constants.MAX_THIRST))

    def update_stamina(self, amount):
        self.stamina = max(0, min(self.stamina + amount, constants.MAX_STAMINA))

    def draw_status_bars(self, screen):
        bar_width = 100
        bar_height = 10
        x_offset = 10
        y_offset = 10

        #energy bar
        pygame.draw.rect(screen, constants.BAR_BACKGROUND, (x_offset, y_offset, bar_width, bar_height))
        pygame.draw.rect(screen, constants.ENERY_COLOR, (x_offset, y_offset, bar_width * (self.energy / constants.MAX_ENERGY), bar_height))

        #food bar
        y_offset += 15
        pygame.draw.rect(screen, constants.BAR_BACKGROUND, (x_offset, y_offset, bar_width, bar_height))
        pygame.draw.rect(screen, constants.FOOD_COLOR, (x_offset, y_offset, bar_width * (self.food / constants.MAX_FOOD), bar_height))

        #thirst bar
        y_offset += 15
        pygame.draw.rect(screen, constants.BAR_BACKGROUND, (x_offset, y_offset, bar_width, bar_height))
        pygame.draw.rect(screen, constants.THIRST_COLOR, (x_offset, y_offset, bar_width * (self.thirst / constants.MAX_THIRST), bar_height))

        #stamina bar
        y_offset += 15
        pygame.draw.rect(screen, constants.BAR_BACKGROUND, (x_offset, y_offset, bar_width, bar_height))
        pygame.draw.rect(screen, constants.STAMINA_COLOR, (x_offset, y_offset, bar_width * (self.stamina / constants.MAX_STAMINA), bar_height))

        #mostrar mensaje si esta en el agua
        font = pygame.font.Font(None, 20)
        if hasattr(self, 'in_water') and self.in_water:
            #verificar si tiene cubeta
            bucket_equipped, _ = self.inventory.has_bucket_equipped()
            water_bucket_equipped, _ = self.inventory.has_water_bucket_equipped()
            if bucket_equipped:
                water_text = font.render("press 'E' to fill bucket", True, constants.WHITE)
                screen.blit(water_text, (x_offset, y_offset + 25))
            elif water_bucket_equipped:
                water_text = font.render("press 'E' to empty bucket", True, constants.WHITE)
                screen.blit(water_text, (x_offset, y_offset + 25))
            else:
                water_text = font.render("press 'E' to drink water", True, constants.WHITE)
                screen.blit(water_text, (x_offset, y_offset + 25))

        #dibujar corazones de vida
        heart_spacing = 25
        heart_x = constants.WIDTH - (self.max_health * heart_spacing) - 10
        heart_y = 10

        for i in range(self.max_health):
            if i < self.current_health:
                screen.blit(self.heart_full, (heart_x + i * heart_spacing, heart_y))
            else:
                screen.blit(self.heart_empty, (heart_x + i * heart_spacing, heart_y))

    def update_status(self, world=None):
        #aplicar multiplicadores si está corriendo
        food_rate = FOOD_DECREASE_RATE * (RUN_FOOD_DECREASE_MULTIPLIER if self.is_running else 1)
        thirst_rate = THIRST_DECREASE_RATE * (RUN_THIRST_DECREASE_MULTIPLIER if self.is_running else 1)

        self.update_food(-food_rate)
        self.update_thirst(-thirst_rate)

        if self.food < constants.MAX_FOOD * 0.2 or self.thirst < constants.MAX_THIRST * 0.2:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_damage_time > 30000:  # cada 30 segundos
                if self.current_health > 0:
                    self.current_health -= 1
                    self.last_damage_time = current_time
            self.update_energy(-constants.ENERY_DECREASE_RATE)
        else:
            self.update_energy(constants.ENERY_INCREASE_RATE)

        #recuperar stamina cuando no está corriendo
        if not self.is_running:
            self.update_stamina(STAMINA_DECREASE_RATE)

        #actualizar estado de agua
        if world:
            self.in_water = self.is_in_water(world)

    def draw_target_tile(self, screen, camera_x, camera_y):
        #verifica si tiene equipada una herramienta de acción (azada o cubeta)
        hoe_equipped = self.inventory.has_hoe_equipped()
        bucket_equipped, _ = self.inventory.has_bucket_equipped()
        water_bucket_equipped, _ = self.inventory.has_water_bucket_equipped()

        if hoe_equipped or bucket_equipped or water_bucket_equipped:
            #calcular la posición del tile donde está parado el personaje
            grid_x = (self.x // constants.GRASS) * constants.GRASS
            grid_y = (self.y // constants.GRASS) * constants.GRASS

            screen_x = grid_x - camera_x
            screen_y = grid_y - camera_y

            #dibujar un borde negro semitransparente como resaltado
            highlight_rect = pygame.Rect(screen_x, screen_y, constants.GRASS, constants.GRASS)
            pygame.draw.rect(screen, (0, 0, 0), highlight_rect, 1)
