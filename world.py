import pygame
import constants
from elements import Tree, SmallStone, FarmLand, Water
import random
import os
from pygame import Surface


class WorldChunk:
    #Representa una parte del mundo con sus propios elementos
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.farmland_tiles = {}
        self.water_tiles = {}

        #crear una semilla unica basada en las coordenadas del chunk
        chunk_seed = hash(f"{x},{y}")
        #guardar el estado actual del generador random
        old_state = random.getstate()
        #establecer la semilla para este chunk
        random.seed(chunk_seed)

        #generar elementos del chunk
        self.trees = [
            Tree(
                self.x + random.randint(0, width - constants.TREE),
                self.y + random.randint(0, height - constants.TREE)
            ) for _ in range(5)
        ]

        self.small_stones = [
            SmallStone(
                self.x + random.randint(0, width - constants.SMALL_STONE),
                self.y + random.randint(0, height - constants.SMALL_STONE)
            )for _ in range(10)
        ]

        #generar agua (lagos pequeños)
        if random.random() < constants.WATER_GENERATION_PROBABILITY:
            #crear un lago circular
            center_x = self.x + random.randint(0, width)
            center_y = self.y + random.randint(0, height)
            radius = random.randint(3, 8) * constants.GRASS

            #crear tiles de agua en un patron circular
            for y_offset in range(-int(radius), int(radius) + 1, constants.GRASS):
                for x_offset in range(-int(radius), int(radius) + 1, constants.GRASS):
                    #calcular posicion del tile
                    tile_x = center_x + x_offset
                    tile_y = center_y + y_offset

                    #verificar si esta dentro del circulo y dentro del chunk
                    if((x_offset ** 2 + y_offset ** 2) <= radius ** 2 and
                        self.x <= tile_x < self.x + width and
                        self.y <= tile_y < self.y + height):

                        #alinear a la cuadricula
                        grid_x = (tile_x // constants.GRASS) * constants.GRASS
                        grid_y = (tile_y // constants.GRASS) * constants.GRASS

                        tile_key = (grid_x, grid_y)
                        self.water_tiles[tile_key] = Water(grid_x, grid_y)

        #restaurar el estado anterior del generador random
        random.setstate(old_state)

    def draw(self, screen, grass_image, camera_x, camera_y):
        #dibujar el pasto en este chunk con offset de camara
        chunk_screen = self.x - camera_x
        chunk_screen = self.y - camera_y

        #calcular el rango de tiles de grass visibles con un tile extra para evitar lineas
        start_x = max(0, (camera_x - self.x - constants.GRASS) // constants.GRASS)
        end_x = min(self.width // constants.GRASS + 1, (camera_x + constants.WIDTH - self.x + constants.GRASS) // constants.GRASS + 1)
        start_y = max(0, (camera_y - self.y - constants.GRASS) // constants.GRASS)
        end_y = min(self.height // constants.GRASS + 1, (camera_y + constants.HEIGHT - self.y + constants.GRASS) // constants.GRASS + 1)

        for y in range(int(start_y), int(end_y)):
            for x in range(int(start_x), int(end_x)):
                tile_x = self.x + x * constants.GRASS
                tile_y = self.y + y * constants.GRASS
                screen_x = tile_x - camera_x
                screen_y = tile_y - camera_y

                tile_key = (tile_x, tile_y)
                if tile_key not in self.water_tiles:
                    if tile_key in self.farmland_tiles:
                        self.farmland_tiles[tile_key].draw(screen, camera_x, camera_y)
                    else:
                        screen.blit(grass_image, (screen_x, screen_y))

        #remover elementos agotados
        self.trees = [tree for tree in self.trees if not tree.is_depleted()]
        self.small_stones = [stone for stone in self.small_stones if not stone.is_depleted()]

        #dibujar elementos solo si estan en pantalla
        for stone in self.small_stones:
            stone_screen_x = stone.x - camera_x
            stone_screen_y = stone.y - camera_y
            if(stone_screen_x + stone.size >= 0 and stone_screen_x <= constants.WIDTH and 
               stone_screen_y + stone.size >= 0 and stone_screen_y <= constants.HEIGHT):
                stone.draw(screen, camera_x, camera_y)

        for tree in self.trees:
            tree_screen_x = tree.x - camera_x
            tree_screen_y = tree.y - camera_y
            if(tree_screen_x + tree.size >= 0 and tree_screen_x <= constants.WIDTH and 
               tree_screen_y + tree.size >= 0 and tree_screen_y <= constants.HEIGHT):
                tree.draw(screen, camera_x, camera_y)

        #dibujar agua despues de los elementos para que aparezca por encima
        for tile_key, water in self.water_tiles.items():
            water.draw(screen, camera_x, camera_y)

    def update(self, dt):
        """actualizar los elementos del chunk"""
        #actualizar animacion del agua
        for water in self.water_tiles.values():
            water.update(dt)


class World: 
    def __init__(self, width, height):

        self.chunk_size = constants.WIDTH
        self.active_chunks = {}
        self.inactive_chunks = {}

        self.view_width = width
        self.view_height = height

        #cargar imagen del grass
        grass_path = os.path.join('assets', 'images', 'objects', 'grass.png')
        self.grass_image = pygame.image.load(grass_path).convert()
        self.grass_image = pygame.transform.scale(self.grass_image, (constants.GRASS, constants.GRASS))

        #sistema dia/noche
        self.current_time = constants.MORNING_TIME        #comenzar a las 8:00
        self.day_overlay = Surface((width, height))
        self.day_overlay.fill(constants.DAY_COLOR)
        self.day_overlay.set_alpha(0)

        #generar chunk inicial y adyacentes
        self.generate_chunk(0, 0)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                self.generate_chunk(dx, dy)


    def get_chunk_key(self, x, y):
        #obtiene la llave del chunk basandose en coordenadas globales
        chunk_x  = x // self.chunk_size
        chunk_y  = y // self.chunk_size
        return(chunk_x, chunk_y)
    
    def generate_chunk(self, chunk_x, chunk_y):
        #genera un nuevo chunk en las coordenadas especificas o recupera uno existente
        key = (chunk_x, chunk_y)
        if key not in self.active_chunks:
            # verificar si el chunk no existe en inactive_chunks
            if key in self.inactive_chunks:
                #recuperar el chunk inactivo
                self.active_chunks[key] = self.inactive_chunks[key]
                del self.inactive_chunks[key]
            else:
                x = chunk_x * self.chunk_size
                y = chunk_y * self.chunk_size
                self.active_chunks[key] = WorldChunk(x, y, self.chunk_size, self.chunk_size)

    def update_chunks(self, player_x, player_y):
        #actualiza los chunks basado en la posicion del jugador
        current_chunk = self.get_chunk_key(player_x, player_y)

        #generar chunks adyacentes
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                chunk_x = current_chunk[0] + dx
                chunk_y = current_chunk[1] + dy
                self.generate_chunk(chunk_x, chunk_y)

        #mover chunks lejanos a inactive_chunks en lugar de eliminarlos
        chunks_to_move = []
        for chunk_key in self.active_chunks:
            distance_x = abs(chunk_key[0] - current_chunk[0])
            distance_y = abs(chunk_key[1] - current_chunk[1])
            if distance_x > 2 or distance_y > 2:
                chunks_to_move.append(chunk_key)


        for chunk_key in chunks_to_move:
            #mover el chunk a inactive_chunks en lugar de eliminarlos
            self.inactive_chunks[chunk_key] = self.active_chunks[chunk_key]
            del self.active_chunks[chunk_key]

    def update_time(self, dt):
        self.current_time = (self.current_time + dt) % constants.DAY_LENGTH

        #calcular el color y la intensidad basador en la hora del dia
        if constants.MORNING_TIME <= self.current_time < constants.DUKS_TIME:
            #durante el dia(8:00 - 18:00)
            self.day_overlay.fill(constants.DAY_COLOR)
            alpha = 0
        elif constants.DAWN_TIME <= self.current_time <= constants.MORNING_TIME:
            #entre 6:00 y 8:00 - amanecer
            self.day_overlay.fill(constants.NIGHT_COLOR)
            morning_progress = (self.current_time - constants.DAWN_TIME) / (constants.MORNING_TIME - constants.DAWN_TIME)
            alpha = int(constants.MAX_DARKNESS * (1 - morning_progress))
        elif constants.DUKS_TIME <= self.current_time <= constants.MIDNIGHT:
            #entre 18:00 y 00:00 - atardecer
            self.day_overlay.fill(constants.NIGHT_COLOR)
            night_progress = (self.current_time - constants.DUKS_TIME) / (constants.MIDNIGHT - constants.DUKS_TIME)
            alpha = int(constants.MAX_DARKNESS * night_progress)
        else:
            #entre las 00:00 y 06:00 - noche
            self.day_overlay.fill(constants.NIGHT_COLOR)
            alpha = constants.MAX_DARKNESS
        
        self.day_overlay.set_alpha(alpha)

        #actualizar los chunks activos
        for chunk in self.active_chunks.values():
            chunk.update(dt)

    def draw(self, screen, camera_x, camera_y):
        
        #dibujar todos los chunks activos con el offset de la camara
        for chunk in self.active_chunks.values():
            chunk.draw(screen, self.grass_image, camera_x, camera_y)
        
        #aplicar el overlay dia/noche
        screen.blit(self.day_overlay, (0, 0))
    
    def draw_inventory(self, screen, character):
        font = pygame.font.Font(None, 24)
        instruction_text = font.render("Press 'I' to open inventory", True, constants.WHITE)
        screen.blit(instruction_text, (10, 10))

    @property
    def trees(self):
        #retorna todos los arboles de todos los chunks activos
        all_trees = []
        for chunk in self.active_chunks.values():
            all_trees.extend(chunk.trees)
        return all_trees
    
    @property
    def small_stones(self):
        #retorna todos las piedras de todos los chunks activos
        all_stones = []
        for chunk in self.active_chunks.values():
            all_stones.extend(chunk.small_stones)
        return all_stones

    @property
    def water_tiles(self):
        #retorna todos los tiles de agua de todos los chunks activos
        all_water = {}
        for chunk in self.active_chunks.values():
            all_water.update(chunk.water_tiles)
        return all_water

    def add_farmland(self, x, y):
        """añade un tile de tierra cultivada en la posicion especifica"""
        #obtener el chunk correspondiente a la posicion
        chunk_key = self.get_chunk_key(x, y)
        chunk = self.active_chunks.get(chunk_key)

        if chunk:
            #alinear la posicion a la cuadricula
            grid_x = (x // constants.GRASS) * constants.GRASS
            grid_y = (y // constants.GRASS) * constants.GRASS

            #verificar si hay arboles o piedras en esta posicion
            for tree in chunk.trees:
                if(grid_x < tree.x + tree.size and grid_x + constants.GRASS > tree.x and
                    grid_y < tree.y + tree.size and grid_y + constants.GRASS > tree.y):
                    return False

            for stone in chunk.small_stones:
                if(grid_x < stone.x + stone.size and grid_x + constants.GRASS > stone.x and
                    grid_y < stone.y + stone.size and grid_y + constants.GRASS > stone.y):
                    return False

            #verificar si hay agua en esa posicion
            tile_key = (grid_x, grid_y)
            if tile_key in chunk.water_tiles:
                return False

            #si no hay obstaculos, crear el tile de farmland
            from elements import FarmLand
            if tile_key not in chunk.farmland_tiles:
                chunk.farmland_tiles[tile_key] = FarmLand(grid_x, grid_y)
            return True
        return False

    def is_water_at(self, x, y):
        #verifica si hay agua en la posicion especificada
        chunk_key = self.get_chunk_key(x, y)
        chunk = self.active_chunks.get(chunk_key)

        if chunk:
            #alinear la posicion a la cuadricula
            grid_x = (x // constants.GRASS) * constants.GRASS
            grid_y = (y // constants.GRASS) * constants.GRASS

            tile_key = (grid_x, grid_y)
            return tile_key in chunk.water_tiles

        return False

    def get_farmland_at(self, x, y):
        #obtener el objeto de tierra de cultivo en las coordenadas especificadas, si existe
        chunk_key = self.get_chunk_key(x, y)
        chunk = self.active_chunks.get(chunk_key)

        if chunk:
            #convertir coordenadas de cuadricula
            grid_x = (x // constants.GRASS) * constants.GRASS
            grid_y = (y // constants.GRASS) * constants.GRASS

            tile_key = (grid_x, grid_y)
            return chunk.farmland_tiles.get(tile_key)
        return None

    def update(self, dt):
        #actualiza todos los chunks activos y sus elementos
        current_time = pygame.time.get_ticks()

        #actualizar hora del dia
        self.update_time(dt)

        #actualizar tierras de cultivo en todos los chunks activos
        for chunk in self.active_chunks.values():
            chunk.update(dt)

            #actualizar todas las casillas de tierra de cultivo con la hora actual
            for farmland in chunk.farmland_tiles.values():
                farmland.update(current_time)

