from display import RESOLUTION_X, RESOLUTION_Y, display
import pygame

class Text:
    def __init__(self, text, color, pos = (.5, .5), center = False, size = 32):
        self.renderer = pygame.font.SysFont("Comic Sans MS", size)
        self.color = color
        self.center = center
        self.pos = pos
        self.update_text(text)

    def update_text(self, new):
        self.surface = self.renderer.render(new, False, self.color)
        dims = self.surface.get_size()

        self.offset = (self.pos[0] * RESOLUTION_X,  self.pos[1] * RESOLUTION_Y)
        if self.center:
            dims = self.surface.get_size()
            self.offset = (self.offset[0] - dims[0] / 2, self.offset[1])
    

    def render(self):
        display.blit(self.surface, self.offset)

    def bounding_box(self) -> tuple[int, int, int, int]:
        size = self.surface.get_size()
        return self.offset[0], self.offset[0] + size[0], self.offset[1], self.offset[1] + size[1]
