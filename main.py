import pygame
import sys
import constants
from character import Character
from world import World
from main_menu import MainMenu

#inicializar pygame
pygame.init()

screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
pygame.display.set_caption("survilands")

# Mostrar menú
menu = MainMenu(screen)
opcion = menu.run()

if opcion == "Jugar":
    # Aquí inicia tu bucle principal del juego
    pass
elif opcion == "Controles":
    # Mostrar pantalla de controles (te ayudo si quieres)
    pass
elif opcion == "Creditos":
    # Mostrar créditos
    pass
elif opcion == "Salir":
    pygame.quit()
    sys.exit()

def main():
    clock = pygame.time.Clock()
    world = World(constants.WIDTH, constants.HEIGHT)
    character = Character(constants.WIDTH // 2, constants.HEIGHT // 2)
    show_inventory = False
    show_coordinates = False

    status_update_timer = 0

    #variables para la camara
    camera_x = 0
    camera_y = 0

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

            #manejar eventos del mouse para el inventario
            if event.type == pygame.MOUSEBUTTONDOWN:
                character.inventory.handle_click(pygame.mouse.get_pos(), event.button, show_inventory)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                character.inventory.handle_click(pygame.mouse.get_pos(), event.button, show_inventory)

        dx = dy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            dx = -5
        if keys[pygame.K_d]:
            dx = 5
        if keys[pygame.K_w]:
            dy = -5
        if keys[pygame.K_s]:
            dy = 5

        #actualizar estado de corriendo
        character.is_running = keys[pygame.K_LSHIFT] and character.stamina > 0
        character.move(dx, dy, world)

        #la camara sigue al personaje 
        camera_x = character.x - constants.WIDTH // 2
        camera_y = character.y - constants.HEIGHT // 2

        #actualizar los chunks en base a la posicion del personaje
        world.update_chunks(character.x, character.y)

        #actulizar elementos del mundo
        world.update(dt)

        #actualizar el tiempo del dia
        world.update_time(dt)

        status_update_timer += dt
        if status_update_timer >= constants.STATUS_UPDATE_INTERVAL:
            character.update_status(world)
            status_update_timer = 0

        if character.current_health <= 0:
            print("game over :c")
            pygame.quit()
            sys.exit()

        #limpiar pantalla
        screen.fill((0, 0, 0))

        #dibujar mundo con offset de camara
        world.draw(screen, camera_x, camera_y)

        #dibujar personaje en el centro de la pantalla
        character.draw(screen, camera_x, camera_y)
        if show_inventory:
            character.draw_inventory(screen)

        #dibujar inventario (hotbar siempr visible + inventario principal si esta abierto)
        character.draw_inventory(screen, show_inventory)


        #dibujar HUD
        font = pygame.font.Font(None, 24)
        energy_text = font.render(f"Energy: {int(character.energy)}", True, constants.WHITE)
        food_text = font.render(f"Food: {int(character.food)}", True, constants.WHITE)
        thirst_text = font.render(f"Thirst: {int(character.thirst)}", True, constants.WHITE)
        stamina_text = font.render(f"Stamina: {int(character.stamina)}", True, constants.WHITE)
        #añadir indicador de tiempo
        time_of_day = (world.current_time / constants.DAY_LENGTH) * 24 #convertir a formato de 24 horas
        time_text = font.render(f"Time: {int(time_of_day):02d}:00", True, constants.WHITE)


        screen.blit(energy_text, (10, constants.HEIGHT - 115))
        screen.blit(food_text, (10, constants.HEIGHT - 90))
        screen.blit(thirst_text, (10, constants.HEIGHT - 65))
        screen.blit(stamina_text, (10, constants.HEIGHT - 40))
        screen.blit(time_text, (10, constants.HEIGHT - 15))

        if show_coordinates:
            coord_text = font.render(f"X: {int(character.x)} , Y: {int(character.y)}", True, constants.WHITE)
            screen.blit(coord_text, (10, constants.HEIGHT - 140))

        pygame.display.flip()


if __name__ == "__main__":
    main()