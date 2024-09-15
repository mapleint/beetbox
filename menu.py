import pygame
import pygame.examples
from display import display
from render import Text

pygame.init()
pygame.mixer.init()
pygame.font.init()

text_color = (234, 212, 252) 
background_color = (234, 212, 252)

import game
input_method = game.INPUT(None, None)


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


last_rhythm = None
last_score = 0

game_over_text = Text("GAME OVER!", pygame.color.THECOLORS["red"], (.5, .3), True, size=64)

def nothing():
    pass

Option(game_over_text, nothing),

title = Text("XTREME BEETB0XX^{tm}", pygame.color.THECOLORS["black"], (.5, .3), True, 92)

header_color = (0, 0, 0)
song_color = (120, 0, 255)

main_menu : Menu
songs_menu = Menu([
    Option(Text("SONG SELECT", header_color, (.5, .25), True), lambda : nothing),
    Option(Text("rhytm1 (medium)", pygame.color.THECOLORS["blue"], (.5, .35), True), lambda : start_game(game.rhythm1)),
    Option(Text("rhytm2 (hard)", pygame.color.THECOLORS["red"], (.5, .45), True), lambda : start_game(game.rhythm2)),
    Option(Text("rhytm3 (sigma)", song_color, (.5, .55), True), lambda : start_game(game.rhythm3)),
    Option(Text("BACK", pygame.color.THECOLORS["blue"], (.5, .75), True), lambda : change_menu(main_menu)),
])
game_over = Menu([
    Option(game_over_text, nothing),
    Option(Text("RETRY", pygame.color.THECOLORS["green"], (.5, .45), True), lambda : start_game(last_rhythm)),
    Option(Text("MAIN MENU", pygame.color.THECOLORS["blue"], (.5, .55), True), lambda : change_menu(main_menu)),
])

def start_game(rhythm):
    level = game.Game(input_method)
    level.start_game(rhythm)
    global last_score, last_rhythm
    last_score = level.score
    last_rhythm = rhythm
    if last_score >= 0:
        game_over_text.update_text(f"WINNER!! score: {last_score}")
    else:
        game_over_text.update_text("GAME OVER!")
    change_menu(game_over)

selected = game_over
main_menu = Menu([])

import shared
import time
def menu(status = None, inp = None, lock = None):
    if status:
        input_method.input = inp
        input_method.lock = lock
        calibration_text = Text("Calibrate Microphone (beatbox into your microphone)", (255, 255, 255), center=True)
        while status.value == shared.CALIBRATION:
            calibration_text.render()
            pygame.display.update()
            time.sleep(1/30)
        def quit():
            with lock:
                status.value = shared.QUIT
            pygame.quit()
            exit(0)
    else:
        def quit():
            pygame.quit()
            exit(0)
        input_method.get_input = game.KEY_INPUT(None, None).get_input

    global main_menu
    main_menu = Menu([
        Option(Text("SONGS", pygame.color.THECOLORS["green"], (.5, .45), True), lambda : change_menu(songs_menu)),
        Option(Text("QUIT", pygame.color.THECOLORS["blue"], (.5, .55), center=True), quit),
    ])
    global selected
    selected = main_menu

    def run_status():
        if status:
            return status.value
        return 1

    while run_status() != shared.QUIT:
        display.fill(background_color)
        if selected is main_menu:
            title.render()
        selected.render()
        #print("attempting update")
        pygame.display.update()
        #print("attempting event loop")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                selected.click(event.pos[0], event.pos[1])

        clock.tick(30)