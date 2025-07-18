import pygame
import sys
import constants
import random
import math
from character import Character
from world import World
from main_menu import MainMenu
from controls_screen import ControlsScreen
from game_over_screen import GameOverScreen
from enemy import Skeleton

#inicializar pygame
pygame.init()

screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
pygame.display.set_caption("survilands")

def show_menu():
    menu = MainMenu(screen)
    return menu.run()

def show_controls():
    controles = ControlsScreen(screen)
    controles.run()

def game_loop():
    clock = pygame.time.Clock()
    world = World(constants.WIDTH, constants.HEIGHT)
    character = Character(constants.WIDTH // 2, constants.HEIGHT // 2)
    show_inventory = False
    show_coordinates = False
    status_update_timer = 0
    skeletons = []
    skeletons_spawned = False

    camera_x = camera_y = 0

    while True:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    character.interact(world)
                if event.key == pygame.K_i:
                    show_inventory = not show_inventory
                if event.key == pygame.K_f:
                    character.update_food(20)
                if event.key == pygame.K_t:
                    character.update_thirst(20)
                if event.key == pygame.K_c:
                    show_coordinates = not show_coordinates
                if event.key == pygame.K_ESCAPE:
                    return

            if event.type == pygame.MOUSEBUTTONDOWN:
                character.inventory.handle_click(pygame.mouse.get_pos(), event.button, show_inventory)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                character.inventory.handle_click(pygame.mouse.get_pos(), event.button, show_inventory)

        dx = dy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: dx = -5
        if keys[pygame.K_d]: dx = 5
        if keys[pygame.K_w]: dy = -5
        if keys[pygame.K_s]: dy = 5

        character.is_running = keys[pygame.K_LSHIFT] and character.stamina > 0
        character.move(dx, dy, world)

        camera_x = character.x - constants.WIDTH // 2
        camera_y = character.y - constants.HEIGHT // 2

        world.update_chunks(character.x, character.y)
        world.update(dt)
        world.update_time(dt)

        #generar enemigos solo de noche (18:00)
        is_night = world.current_time >= constants.DUKS_TIME or world.current_time < constants.DAWN_TIME

        if is_night and not skeletons_spawned:
            for _ in range(5):  # cantidad de esqueletos a generar
                distance = random.randint(300, 600)
                angle = random.uniform(0, 2 * 3.14159)
                spawn_x = character.x + int(distance * math.cos(angle))
                spawn_y = character.y + int(distance * math.sin(angle))
                skeletons.append(Skeleton(spawn_x, spawn_y))
            skeletons_spawned = True


        #desaparecer esqueletos al amanecer
        #if not is_night:
        #    skeletons.clear()
        #    skeletons_spawned = False

        #al amanecer, iniciar desaparición en lugar de eliminar al instante
        if not is_night:
            for skeleton in skeletons:
                if not skeleton.disappearing:
                    skeleton.start_disappearing()

        status_update_timer += dt
        if status_update_timer >= constants.STATUS_UPDATE_INTERVAL:
            character.update_status(world)
            status_update_timer = 0

        if character.current_health <= 0:
            game_over = GameOverScreen(screen)
            result = game_over.run()
            if result == "menu":
                return

        screen.fill((0, 0, 0))
        world.draw(screen, camera_x, camera_y)
        character.draw(screen, camera_x, camera_y)
        character.draw_target_tile(screen, camera_x, camera_y)

        #dibujar y actualizar enemigos
        #if is_night:
        #    for skeleton in skeletons:
        #        skeleton.move_towards_player(character, world, skeletons)
        #        skeleton.update_animation()
        #        skeleton.check_collision_with_player(character)
        #        skeleton.draw(screen, camera_x, camera_y)

        # Dibujar y actualizar enemigos (tanto si es de noche o si aún están desapareciendo)
        if is_night or skeletons:
            for skeleton in skeletons[:]:  # iteramos sobre copia para poder remover
                if not skeleton.disappearing:
                    skeleton.move_towards_player(character, world, skeletons)
                    skeleton.update_animation()
                    skeleton.check_collision_with_player(character)
                else:
                    if skeleton.update_disappearance():
                        skeletons.remove(skeleton)
                        continue  # ya se desvaneció completamente

                skeleton.draw(screen, camera_x, camera_y)

        if show_inventory:
            character.draw_inventory(screen)
        character.draw_inventory(screen, show_inventory)

        font = pygame.font.Font(None, 24)
        energy_text = font.render(f"Energy: {int(character.energy)}", True, constants.WHITE)
        food_text = font.render(f"Food: {int(character.food)}", True, constants.WHITE)
        thirst_text = font.render(f"Thirst: {int(character.thirst)}", True, constants.WHITE)
        stamina_text = font.render(f"Stamina: {int(character.stamina)}", True, constants.WHITE)
        health_text = font.render(f"Health: {int(character.current_health)}", True, constants.WHITE)
        time_of_day = (world.current_time / constants.DAY_LENGTH) * 24
        time_text = font.render(f"Time: {int(time_of_day):02d}:00", True, constants.WHITE)

        screen.blit(health_text, (10, constants.HEIGHT - 140))
        screen.blit(energy_text, (10, constants.HEIGHT - 115))
        screen.blit(food_text, (10, constants.HEIGHT - 90))
        screen.blit(thirst_text, (10, constants.HEIGHT - 65))
        screen.blit(stamina_text, (10, constants.HEIGHT - 40))
        screen.blit(time_text, (10, constants.HEIGHT - 15))

        if show_coordinates:
            coord_text = font.render(f"X: {int(character.x)} , Y: {int(character.y)}", True, constants.WHITE)
            screen.blit(coord_text, (10, constants.HEIGHT - 160))

        pygame.display.flip()

def main():
    while True:
        option = show_menu()
        if option == "Jugar":
            game_loop()
        elif option == "Controles":
            show_controls()
        elif option == "Salir":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()
