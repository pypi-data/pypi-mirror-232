import pygame


class Base:
    def __init__(self, title, wh, icon=None, defaultScreen="start"):
        self.MainRoot = pygame.display.set_mode(wh)
        pygame.display.set_caption(title)

        self.MakeScreen(defaultScreen)

        self.Screen = defaultScreen

        if icon:
            pygame.display.set_icon(pygame.image.load(icon))

