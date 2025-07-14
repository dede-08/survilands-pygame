import pygame
import constants
import os

class ControlsScreen:
    def __init__(self, screen):
        self.screen = screen
        font_path = os.path.join("assets", "fonts", "Minecraft.ttf")
        self.title_font = pygame.font.Font(font_path, 48)
        self.text_font = pygame.font.Font(font_path, 32)

        #cargar imagen de fondo
        self.background_image = pygame.image.load("assets/images/interface/options_background.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, (constants.WIDTH, constants.HEIGHT))

        self.controls = [
            ("W / A / S / D", "Mover al personaje"),
            ("Shift", "Correr"),
            ("E", "Interactuar (usar herramientas, beber agua, etc.)"),
            ("I", "Abrir/Cerrar Inventario"),
            ("C", "Mostrar coordenadas"),
            ("Click Izq/Der", "Interacción con inventario")
        ]

    def run(self):
        running = True
        while running:

            #dibujar el fondo de la pantalla
            self.screen.blit(self.background_image, (0, 0))

            title = self.title_font.render("Controles del Juego", True, constants.WHITE)
            self.screen.blit(title, (constants.WIDTH // 2 - title.get_width() // 2, 50))

            start_y = 180
            spacing = 50

            for key, action in self.controls:
                key_text = self.text_font.render(f"{key}", True, constants.YELLOW)
                action_text = self.text_font.render(f"- {action}", True, constants.WHITE)

                self.screen.blit(key_text, (100, start_y))
                self.screen.blit(action_text, (400, start_y))
                start_y += spacing

            back_text = self.text_font.render("Presiona ESC para volver", True, constants.RED)
            self.screen.blit(back_text, (constants.WIDTH // 2 - back_text.get_width() // 2, constants.HEIGHT - 100))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
