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
        self.hotbar = [None] * constants.HOTBAR_SLOTS
        self.inventory = [[None for _ in range(constants.INVENTORY_COLS)] for _ in range(constants.INVENTORY_ROWS)]
        self.dragged_item = None
        self.font = pygame.font.Font(None, 24)

        #cargar imagenes de los items
        self.item_images = {
            'wood': os.path.join('assets', 'images', 'objects', 'wood.png'),
            'stone': os.path.join('assets', 'images', 'objects', 'small_stone2.png'),
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
        #dibujar hotbar (siempre visivle)
        self._draw_hotbar(screen)

        #dibujar inventario principal si está abierto
        if show_inventory:
            #fondo semitransparente
            background = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
            background.fill((0, 0, 0, 128))
            screen.blit(background, (0, 0))

            self._draw_main_inventory(screen)

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

    def handle_click(self, pos, button, show_inventory=False):
        mouse_x, mouse_y = pos

        #verificar click en hotbar
        if constants.HOTBAR_Y <= mouse_y <= constants.HOTBAR_Y + constants.SLOT_SIZE:
            slot_index = (mouse_x - constants.HOTBAR_X) // constants.SLOT_SIZE
            if 0 <= slot_index < constants.HOTBAR_SLOTS:
                self._handle_slot_click(button, self.hotbar, slot_index,
                                        constants.HOTBAR_X + (slot_index * constants.SLOT_SIZE),
                                        constants.HOTBAR_Y)
                return True

        #verificar click en inventario principal si está abierto
        if show_inventory and constants.INVENTORY_Y <= mouse_y <= constants.INVENTORY_Y + (constants.INVENTORY_ROWS * constants.SLOT_SIZE):
            row = (mouse_y - constants.INVENTORY_Y) // constants.SLOT_SIZE
            col = (mouse_x - constants.INVENTORY_X) // constants.SLOT_SIZE
            if(0 <= row < constants.INVENTORY_ROWS and 0 <= col < constants.INVENTORY_COLS):
                self._handle_grid_slot_click(button, row, col,
                                             constants.INVENTORY_X + (col * constants.SLOT_SIZE),
                                             constants.INVENTORY_Y + (row * constants.SLOT_SIZE))
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











