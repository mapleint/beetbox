import pygame
from display import  display
from render import Text

pygame.init()
pygame.mixer.init()
pygame.font.init()

text_color = (234, 212, 252) 
background_color = (234, 212, 252)


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

def change_menu(menu):
    global selected
    selected = menu

COLORS = pygame.color.THECOLORS
BLUE = COLORS["blue"]
RED = COLORS["red"]
GREEN = COLORS["green"]

main_menu : Menu

last_rhythm = None
last_score = 0

game_over_text = Text("GAME OVER!", pygame.color.THECOLORS["red"], (.5, .3), True, size=64)

def nothing():
    pass

Option(game_over_text, nothing),

import game
def start_game(rhythm):
    level = game.Game()
    level.start_game(rhythm)
    global last_score, last_rhythm
    last_score = level.score
    last_rhythm = rhythm
    if last_score >= 0:
        game_over_text.update_text(f"WINNER!! score: {last_score}")
    else:
        game_over_text.update_text("GAME OVER!")
    change_menu(game_over)

songs_menu = Menu([
    Option(Text("rhytm1", pygame.color.THECOLORS["green"], (.5, .45), True), lambda : start_game(game.rhythm1)),
    Option(Text("BACK", pygame.color.THECOLORS["blue"], (.5, .55), True), lambda : change_menu(main_menu)),
])

main_menu = Menu([
    Option(Text("SONGS", pygame.color.THECOLORS["green"], (.5, .45), True), lambda : change_menu(songs_menu)),
    Option(Text("QUIT", pygame.color.THECOLORS["blue"], (.5, .55), center=True), quit),
])

 

game_over = Menu([
    Option(game_over_text, nothing),
    Option(Text("RETRY", pygame.color.THECOLORS["green"], (.5, .45), True), lambda : start_game(last_rhythm)),
    Option(Text("MAIN MENU", pygame.color.THECOLORS["blue"], (.5, .55), True), lambda : change_menu(main_menu)),
])

selected = main_menu

title = Text("BEETBOX^{tm}", pygame.color.THECOLORS["black"], (.5, .3), True, 92)


def quit():
    pygame.quit()
    exit(0)

while True:
    display.fill(background_color)
    if selected is main_menu:
        title.render()
    selected.render()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            selected.click(event.pos[0], event.pos[1])

    clock.tick(60)