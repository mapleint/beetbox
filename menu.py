import pygame

pygame.init()
pygame.mixer.init()
pygame.font.init()

text_color = (234, 212, 252) 
background_color = (234, 212, 252)

RESOLUTION = (1920, 1080)
RESOLUTION_X, RESOLUTION_Y = RESOLUTION

display = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption(f'Beetbox@{RESOLUTION_X}x{RESOLUTION_Y}')


class Text:
    def __init__(self, text, color, pos = (.5, .5), center = False, size = 32):
        sans = pygame.font.SysFont("Comic Sans MS", size)

        self.surface = sans.render(text, False, color)
        self.pos = (pos[0] * RESOLUTION_X,  pos[1] * RESOLUTION_Y)
        if center:
            dims = self.surface.get_size()
            self.pos = (self.pos[0] - dims[0] / 2, self.pos[1] - dims[1] / 2)
        
    def render(self):
        display.blit(self.surface, self.pos)

    def bounding_box(self) -> tuple[int, int, int, int]:
        size = self.surface.get_size()
        return self.pos[0], self.pos[0] + size[0], self.pos[1], self.pos[1] + size[1]
        

class Option:
    def __init__(self, text : Text, func):
        self.text = text
        self.func = func

    def render(self):
        self.text.render()

    def click(self, x : int, y : int):
        box = self.text.bounding_box()
        if box[0] < x < box[1] and box[2] < y < box[3]:
            self.func()

class Menu:
    def __init__(self, options : list[Option]):
        self.options = options
        pass
    def click(self, x : int, y : int):
        for option in self.options:
            option.click(x, y)
        pass
    def render(self):
        for option in self.options:
            option.render()
    
clock = pygame.time.Clock()
pygame.display.flip()

main_menu = Menu([Option(Text("quit", pygame.color.THECOLORS["blue"]), quit)])
selected = main_menu

title = Text("BEETBOX^{tm}", pygame.color.THECOLORS["black"], (.5, .2), True, 92)

def quit():
    pygame.quit()
    exit(0)

while True:
    display.fill(background_color)
    title.render()
    selected.render()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            main_menu.click(event.pos[0], event.pos[1])

    clock.tick(60)