import pygame
import sys
import constants

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        #self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font("assets/fonts/Minecraft.ttf", 100)
        self.clock = pygame.time.Clock()

        self.options = ["Jugar", "Controles", "Salir"]
        self.selected = 0

        #cargar imagen de fondo
        self.background_image = pygame.image.load("assets/images/interface/options_background.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, (constants.WIDTH, constants.HEIGHT))

        #cargar fuentes de las opciones
        self.font = pygame.font.Font("assets/fonts/Minecraft.ttf", 48)

    def draw(self):
        #self.screen.fill((30, 30, 30))  # fondo oscuro

        #dibujar el fondo del menu
        self.screen.blit(self.background_image, (0, 0))

        #título del juego
        title_text = self.title_font.render("SURVILANDS", True, constants.WHITE)
        title_rect = title_text.get_rect(center=(constants.WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)

        #opciones del menu
        for index, option in enumerate(self.options):
            color = constants.WHITE if index != self.selected else (255, 255, 0)  # Amarillo si está seleccionado
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(constants.WIDTH // 2, 300 + index * 60))
            self.screen.blit(text, rect)

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(60)
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.options[self.selected]
