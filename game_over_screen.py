import pygame
import sys
import constants

class GameOverScreen:
    def __init__(self, screen):
        self.screen = screen
        self.options = ["Volver al menu", "Salir"]
        self.selected = 0
        self.font = pygame.font.Font("assets/fonts/Minecraft.ttf", 32)

    def draw(self):
        self.screen.fill((0, 0, 0))
        title_font = pygame.font.Font("assets/fonts/Minecraft.ttf", 64)
        title = title_font.render("GAME OVER", True, constants.RED)
        self.screen.blit(title, (constants.WIDTH // 2 - title.get_width() // 2, 100))

        for i, option in enumerate(self.options):
            color = constants.YELLOW if i == self.selected else constants.WHITE
            text = self.font.render(option, True, color)
            self.screen.blit(text, (constants.WIDTH // 2 - text.get_width() // 2, 250 + i * 60))

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.options[self.selected] == "Volver al menu":
                            return "menu"
                        elif self.options[self.selected] == "Salir":
                            pygame.quit()
                            sys.exit()
            clock.tick(60)
