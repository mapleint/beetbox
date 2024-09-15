import pygame

RESOLUTION = (1920, 1080)
RESOLUTION_X, RESOLUTION_Y = RESOLUTION


LIGHT_GREEN = (0, 204, 0)
LIGHT_BLUE = (102, 153, 255)

display = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption(f'Beetbox@{RESOLUTION_X}x{RESOLUTION_Y}')