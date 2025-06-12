import pygame

import constants
import os

class InventoryItem:
    def __init__(self, name, image_path, quantity = 1):
        self.name = name
        self.quantity = quantity
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (constants.SLOT_SIZE - 10, constants.SLOT_SIZE - 10))
        self.dragging = False
        self.drag_offset = (0, 0)


class Inventory:
    def __init__(self):
        self.left_hand = None
        self.right_hand = None
        self.hotbar = [None] * constants.HOTBAR_SLOTS
        self.inventory = [[None for _ in range(constants.INVENTORY_COLS)] for _ in range(constants.INVENTORY_ROWS)]
        self.crafting_grid = [[None for _ in range(constants.CRAFTING_GRID_SIZE)] for _ in range(constants.CRAFTING_GRID_SIZE)]
        self.crafting_result = None
        self.dragged_item = None
        self.font = pygame.font.Font(None, 24)

        #cargar imagenes de los items
        self.item_images = {
            'wood': os.path.join('assets', 'images', 'objects', 'wood.png'),
            'stone': os.path.join('assets', 'images', 'objects', 'small_stone2.png'),
            'axe': os.path.join('assets', 'images', 'objects', 'axe.png')
        }

        #definir recetas de crafteo
        self.recipes = {
            'axe' : {
                'pattern': [('wood', 'stone'), (None, None)],
                'result': 'axe'
            }
        }

    def add_item(self, item_name, quantity=1):
        #primero intentar apilar en el hotbar
        for i, slot in enumerate(self.hotbar):
            if slot and slot.name == item_name:
                slot.quantity += quantity
                return True

        #luego intentar apilar en el inventario principal
        for row in range(constants.INVENTORY_ROWS):
            for col in range(constants.INVENTORY_COLS):
                if self.inventory[row][col] and self.inventory[row][col].name == item_name:
                    self.inventory[row][col].quantity += quantity
                    return True

        #buscar slot vacio en el hotbar
        for i, slot in enumerate(self.hotbar):
            if slot is None:
                self.hotbar[i] = InventoryItem(item_name, self.item_images[item_name], quantity)
                return True

        #buscar slot vacio en el inventario principal
        for row in range(constants.INVENTORY_ROWS):
            for col in range(constants.INVENTORY_COLS):
                if self.inventory[row][col] is None:
                    self.inventory[row][col] = InventoryItem(item_name, self.item_images[item_name], quantity)
                    return True


    def draw(self, screen, show_inventory=False):
        #dibujar los slots de manos (siempre visibles)
        self._draw_hand_slots(screen)
        #dibujar hotbar (siempre visivle)
        self._draw_hotbar(screen)

        #dibujar inventario principal si está abierto
        if show_inventory:
            #fondo semitransparente
            background = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
            background.fill((0, 0, 0, 128))
            screen.blit(background, (0, 0))

            self._draw_main_inventory(screen)
            self._draw_crafting_grid(screen)

        #dibujar item siendo arrastrado al final para que aparezca encima de todo
        if self.dragged_item:
            mouse_pos = pygame.mouse.get_pos()
            screen.blit(self.dragged_item.image,
                        (mouse_pos[0] - self.dragged_item.drag_offset[0],
                         mouse_pos[1] - self.dragged_item.drag_offset[1]))
            if self.dragged_item.quantity > 1:
                text = self.font.render(str(self.dragged_item.quantity), True, constants.WHITE)
                text_rect = text.get_rect()
                text_rect.bottomright = (mouse_pos[0] + self.dragged_item.image.get_width() // 2 - 5,
                                         mouse_pos[1] + self.dragged_item.image.get_height() // 2 - 5)
                screen.blit(text, text_rect)

    def _draw_hotbar(self, screen):
        for i in range(constants.HOTBAR_SLOTS):
            x = constants.HOTBAR_X + (i * constants.SLOT_SIZE)
            y = constants.HOTBAR_Y

            #dibujar fondo del slot
            pygame.draw.rect(screen, constants.SLOT_BORDER,
                             (x, y, constants.SLOT_SIZE, constants.SLOT_SIZE))
            pygame.draw.rect(screen, constants.SLOT_COLOR,
                             (x + 2, y + 2, constants.SLOT_SIZE - 4, constants.SLOT_SIZE - 4))

            #dibujar item si existe
            if self.hotbar[i]:
                self._draw_item(screen, self.hotbar[i], x, y)

    def _draw_main_inventory(self, screen):
        for row in range(constants.INVENTORY_ROWS):
            for col in range(constants.INVENTORY_COLS):
                x = constants.INVENTORY_X + (col * constants.SLOT_SIZE)
                y = constants.INVENTORY_Y + (row * constants.SLOT_SIZE)

                #dibujar fondo del slot
                pygame.draw.rect(screen, constants.SLOT_BORDER,
                                 (x, y, constants.SLOT_SIZE, constants.SLOT_SIZE))
                pygame.draw.rect(screen, constants.SLOT_COLOR,
                                 (x + 2, y + 2, constants.SLOT_SIZE - 4, constants.SLOT_SIZE - 4))

                #dibujar item si existe
                if self.inventory[row][col]:
                    self._draw_item(screen, self.inventory[row][col], x, y)

    def _draw_item(self, screen, item, x, y):
        #centrar item en el slot
        item_x = x + (constants.SLOT_SIZE - item.image.get_width()) // 2
        item_y = y + (constants.SLOT_SIZE - item.image.get_height()) // 2
        screen.blit(item.image, (item_x, item_y))

        #dibujar cantidad
        if item.quantity > 1:
            text = self.font.render(str(item.quantity), True, constants.WHITE)
            text_rect = text.get_rect()
            text_rect.bottomright = (x + constants.SLOT_SIZE - 5, y + constants.SLOT_SIZE - 5)
            screen.blit(text, text_rect)

    def _draw_hand_slots(self, screen):
        #dibujar slot de la mano izquierda
        pygame.draw.rect(screen, constants.SLOT_BORDER,
                         (constants.LEFT_HAND_SLOT_X, constants.LEFT_HAND_SLOT_Y, constants.SLOT_SIZE,
                          constants.SLOT_SIZE))
        pygame.draw.rect(screen, constants.SLOT_COLOR,
                         (constants.LEFT_HAND_SLOT_X + 2, constants.LEFT_HAND_SLOT_Y + 2, constants.SLOT_SIZE - 4,
                          constants.SLOT_SIZE - 4))
        if self.left_hand:
            self._draw_item(screen, self.left_hand,
                            constants.LEFT_HAND_SLOT_X,
                            constants.LEFT_HAND_SLOT_Y)

        #dibujar slot de la mano derecha
        pygame.draw.rect(screen, constants.SLOT_BORDER,
                         (constants.RIGHT_HAND_SLOT_X, constants.RIGHT_HAND_SLOT_Y, constants.SLOT_SIZE,
                          constants.SLOT_SIZE))
        pygame.draw.rect(screen, constants.SLOT_COLOR,
                         (constants.RIGHT_HAND_SLOT_X + 2, constants.RIGHT_HAND_SLOT_Y + 2, constants.SLOT_SIZE - 4,
                          constants.SLOT_SIZE - 4))
        if self.right_hand:
            self._draw_item(screen, self.right_hand,
                            constants.RIGHT_HAND_SLOT_X,
                            constants.RIGHT_HAND_SLOT_Y)

    def handle_click(self, pos, button, show_inventory=False):
        mouse_x, mouse_y = pos

        #verificar slots de manos primero
        if constants.HOTBAR_Y <= mouse_y <= constants.HOTBAR_Y + constants.SLOT_SIZE:
            #slot de mano izquierda
            if (constants.LEFT_HAND_SLOT_X <= mouse_x <= constants.LEFT_HAND_SLOT_X + constants.SLOT_SIZE):
                self._handle_hand_slot_click(button, 'left')
                return True
            #slot de mano derecha
            elif (constants.RIGHT_HAND_SLOT_X <= mouse_x <= constants.RIGHT_HAND_SLOT_X + constants.SLOT_SIZE):
                self._handle_hand_slot_click(button, 'right')
                return True

        #verificar click en hotbar
        if constants.HOTBAR_Y <= mouse_y <= constants.HOTBAR_Y + constants.SLOT_SIZE:
            slot_index = (mouse_x - constants.HOTBAR_X) // constants.SLOT_SIZE
            if 0 <= slot_index < constants.HOTBAR_SLOTS:
                self._handle_slot_click(button, self.hotbar, slot_index,
                                        constants.HOTBAR_X + (slot_index * constants.SLOT_SIZE),
                                        constants.HOTBAR_Y)
                return True


        if show_inventory:
            #verificar click en inventario principal
            if constants.INVENTORY_Y <= mouse_y <= constants.INVENTORY_Y + (constants.INVENTORY_ROWS * constants.SLOT_SIZE):
                row = (mouse_y - constants.INVENTORY_Y) // constants.SLOT_SIZE
                col = (mouse_x - constants.INVENTORY_X) // constants.SLOT_SIZE
                if(0 <= row < constants.INVENTORY_ROWS and 0 <= col < constants.INVENTORY_COLS):
                    self._handle_grid_slot_click(button, row, col,
                                                 constants.INVENTORY_X + (col * constants.SLOT_SIZE),
                                                 constants.INVENTORY_Y + (row * constants.SLOT_SIZE))
                    return True

        #verificar click en la cuadricula de crafteo
        if constants.CRAFTING_GRID_Y <= mouse_y <= constants.CRAFTING_GRID_Y + (constants.CRAFTING_GRID_SIZE * constants.SLOT_SIZE):
            row = (mouse_y - constants.CRAFTING_GRID_Y) // constants.SLOT_SIZE
            col = (mouse_x - constants.CRAFTING_GRID_X) // constants.SLOT_SIZE
            if(0 <= row < constants.CRAFTING_GRID_SIZE and 0 <= col < constants.CRAFTING_GRID_SIZE):
                self._handle_crafting_grid_click(button, row, col)
                return True

        #verificar click en el slot de resultado
        if (constants.CRAFTING_RESULT_SLOT_X <= mouse_x <= constants.CRAFTING_RESULT_SLOT_X + constants.SLOT_SIZE and
                constants.CRAFTING_RESULT_SLOT_Y <= mouse_y <= constants.CRAFTING_RESULT_SLOT_Y + constants.SLOT_SIZE):
            self._handle_crafting_result_click(button)
            return True

        #click afuera de los slots
        if self.dragged_item and button == 1:
            self._return_dragged_item()
        return False

    def _handle_slot_click(self, button, slot_list, index, slot_x, slot_y):
        mouse_pos = pygame.mouse.get_pos()
        mouse_x, mouse_y = mouse_pos
        if button == 1: #click izquierdo
            if self.dragged_item:
                #soltar item
                if slot_list[index] is None:
                    slot_list[index] = self.dragged_item
                else:
                    #intercambiar items
                    slot_list[index], self.dragged_item = self.dragged_item, slot_list[index]
                    return
                self.dragged_item = None
            elif slot_list[index]:
                #comenzar a arrastrar
                self.dragged_item = slot_list[index]
                slot_list[index] = None
                #calcular offset para el arrastre centrado
                item_rect = self.dragged_item.image.get_rect()
                item_rect.x = slot_x
                item_rect.y = slot_y
                self.dragged_item.drag_offset = (mouse_x - item_rect.centerx,
                                                 mouse_y - item_rect.centery)

    def _handle_grid_slot_click(self, button, row, col, slot_x, slot_y):
        mouse_pos = pygame.mouse.get_pos()
        mouse_x, mouse_y = mouse_pos
        if button == 1:     #click izquierdo
            if self.dragged_item:
                #soltar item
                if self.inventory[row][col] is None:
                    self.inventory[row][col] = self.dragged_item
                else:
                    #intercambiar items
                    self.inventory[row][col], self.dragged_item = self.dragged_item, self.inventory[row][col]
                    return
                self.dragged_item = None
            elif self.inventory[row][col]:
                #comenzar a arrastrar
                self.dragged_item = self.inventory[row][col]
                self.inventory[row][col] = None
                #calcular offset para el arrastre centrado
                item_rect = self.dragged_item.image.get_rect()
                item_rect.x = slot_x
                item_rect.y = slot_y
                self.dragged_item.drag_offset = (mouse_x - item_rect.centerx,
                                                 mouse_y - item_rect.centery)


    def _handle_hand_slot_click(self, button, hand):
        if button == 1: #left click
            if hand == 'left':
                if self.dragged_item:
                    if self.dragged_item.name == 'axe': #only allow axe in hands
                        self.left_hand, self.dragged_item = self.dragged_item, self.left_hand
                elif self.left_hand:
                    self.dragged_item = self.left_hand
                    self.left_hand = None
            else:
                if self.dragged_item:
                    if self.dragged_item.name == 'axe':
                        self.right_hand, self.dragged_item = self.dragged_item, self.right_hand
                elif self.right_hand:
                    self.dragged_item = self.right_hand
                    self.right_hand = None

    def has_axe_equipped(self):
        return(
            (self.left_hand and self.left_hand.name == 'axe') or
            (self.right_hand and self.right_hand.name == 'axe')
        )

    def _return_dragged_item(self):
        #intentar devolver al hotbar primero
        for i, slot in enumerate(self.hotbar):
            if slot is None:
                self.hotbar[i] = self.dragged_item
                self.dragged_item = None
                return

        #si no hay espacio en el hotbar, intentar el inventario principal
        for row in range(constants.INVENTORY_ROWS):
            for col in range(constants.INVENTORY_COLS):
                if self.inventory[row][col] is None:
                    self.inventory[row][col] = self.dragged_item
                    self.dragged_item = None
                    return

    def _draw_crafting_grid(self, screen):
        #dibujar cuadricula de crafteo
        for row in range(constants.CRAFTING_GRID_SIZE):
            for col in range(constants.CRAFTING_GRID_SIZE):
                x = constants.CRAFTING_GRID_X + (col * constants.SLOT_SIZE)
                y = constants.CRAFTING_GRID_Y + (row * constants.SLOT_SIZE)

                #dibujar fondo del slot
                pygame.draw.rect(screen, constants.SLOT_BORDER, (x, y, constants.SLOT_SIZE, constants.SLOT_SIZE))
                pygame.draw.rect(screen, constants.SLOT_COLOR, (x + 2, y + 2, constants.SLOT_SIZE - 4, constants.SLOT_SIZE - 4))

                #bibujar item si existe
                if self.crafting_grid[row][col]:
                    self._draw_item(screen, self.crafting_grid[row][col], x, y)

        #dibujar slot de resultados
        pygame.draw.rect(screen, constants.SLOT_BORDER,
                         (constants.CRAFTING_RESULT_SLOT_X, constants.CRAFTING_RESULT_SLOT_Y, constants.SLOT_SIZE, constants.SLOT_SIZE))
        pygame.draw.rect(screen, constants.SLOT_COLOR,
                         (constants.CRAFTING_RESULT_SLOT_X + 2, constants.CRAFTING_RESULT_SLOT_Y + 2, constants.SLOT_SIZE - 4,
                          constants.SLOT_SIZE - 4))

        #dibujar resultado si existe
        if self.crafting_result:
            self._draw_item(screen, self.crafting_result,
                            constants.CRAFTING_RESULT_SLOT_X, constants.CRAFTING_RESULT_SLOT_Y)

    def _handle_crafting_grid_click(self, button, row, col):
        if button == 1: #click izquierdo
            if self.dragged_item:
                #soltar item en la cuadricula
                if self.crafting_grid[row][col] is None:
                    self.crafting_grid[row][col] = self.dragged_item
                    self.dragged_item = None
                else:
                    #intercambiar items
                    self.crafting_grid[row][col], self.dragged_item = self.dragged_item, self.crafting_grid[row][col]
            elif self.crafting_grid[row][col]:
                #comenzar a arrastrar
                self.dragged_item = self.crafting_grid[row][col]
                self.crafting_grid[row][col] = None

            #verificar receta despues de cada cambio
            self._check_recipe()

    def _handle_crafting_result_click(self, button):
        if button == 1 and self.crafting_result: #click izquierdo y hay resultado
            if not self.dragged_item:
                #tomar resultado
                self.dragged_item = self.crafting_result
                self.crafting_result = None
                #consumir materiales
                for row in range(constants.CRAFTING_GRID_SIZE):
                    for col in range(constants.CRAFTING_GRID_SIZE):
                        if self.crafting_grid[row][col]:
                            if self.crafting_grid[row][col].quantity > 1:
                                self.crafting_grid[row][col].quantity -= 1
                            else:
                                self.crafting_grid[row][col] = None

    def _check_recipe(self):
        #obtener el patron actual
        current_pattern = []
        for row in range(constants.CRAFTING_GRID_SIZE):
            pattern_row = []
            for col in range(constants.CRAFTING_GRID_SIZE):
                item = self.crafting_grid[row][col]
                pattern_row.append(item.name if item else None)
            current_pattern.append(tuple(pattern_row))

        #verificar si coincide con alguna receta
        for recipe_name, recipe in self.recipes.items():
            matches = True
            for row in range(constants.CRAFTING_GRID_SIZE):
                for col in range(constants.CRAFTING_GRID_SIZE):
                    expected = recipe['pattern'][row][col]
                    actual = current_pattern[row][col]
                    if expected != actual:
                        matches = False
                        break
                if not matches:
                    break

            if matches:
                #crear el resultado
                self.crafting_result = InventoryItem(recipe['result'],
                                                     self.item_images[recipe['result']])
                return

        #si no hay coincidencias, limpiar el resultado
        self.crafting_result = None