from display import RESOLUTION_X, RESOLUTION_Y, display
import pygame

class Text:
    def __init__(self, text, color, pos = (.5, .5), center = False, size = 32):
        self.renderer = pygame.font.SysFont("Comic Sans MS", size)
        self.color = color
        self.center = center
        self.offset = pos
        self.pos = pos

        self.update_text(text)

    def update_text(self, new):
        self.surface = self.renderer.render(new, False, self.color)
        dims = self.surface.get_size()

        self.offset = (self.pos[0] * RESOLUTION_X,  self.pos[1] * RESOLUTION_Y - dims[1])
        if self.center:
            dims = self.surface.get_size()
            self.pos = (self.offset[0] - dims[0] / 2, self.pos[1])

    def render(self):
        display.blit(self.surface, self.pos)

    def bounding_box(self) -> tuple[int, int, int, int]:
        size = self.surface.get_size()
        return self.pos[0], self.pos[0] + size[0], self.pos[1], self.pos[1] + size[1]
