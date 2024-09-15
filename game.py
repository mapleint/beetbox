from rhythm import Rhythm
from detector_beep import Beat, floating_text, Line_input
import time
import pygame
import time
import random

from display import RESOLUTION, RESOLUTION_X, RESOLUTION_Y, display, LIGHT_BLUE, LIGHT_GREEN
from render import Text
from background import Background

bad_words = [
    "miss",
    "bad",
    "miss",
    "bad",
    "miss",
    "bad",
    "miss",
    "bad",
    "miss",
    "bad",
    "miss",
    "bad",
    "rhythmless",
    "trash",
    "not good",
    "u suck",
    "trash",
    "not good",
    "u suck",
    "trash",
    "not good",
    "u suck",
    "badd",
    "baddd",
    "try again",
    "try again",
    "try again",
    "try again",
    "try again",
    "try again",
    "come on",
    "is this the best u got",
    "TRY HARDER",
    "u missed",
    "rethink ur life",
]
import shared

class INPUT:
    def __init__(self, inp, lock):
        self.input = inp
        self.lock = lock

    def get_input(self):
        ret = None
        with self.lock:
            if self.input.value == shared.NONE:
                return ret
            ret = self.input.value
            self.input.value = shared.NONE
        return ret

class KEY_INPUT(INPUT):
    def __init__(self, inp, lock):
        self.input = inp
        self.lock = lock
    def get_input(self):
        events = pygame.event.get()
        keys = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f] 
        for event in events:
            if event.type == pygame.KEYDOWN:
                for i, key in enumerate(keys):
                    if event.key == key:
                        return i
            if event.type == pygame.QUIT:
                pygame.quit()
        return None
class Game:
    def __init__(self, input_method : INPUT):
        self.input_method : INPUT = input_method
        self.tick_rate = 60
        self.speed = 2.0 #beats per second

        self.score = 0
        self.streak = 0
        self.multiplier = 1

        pygame.mixer.init()

        # self.background_colour = (234, 212, 252)
        self.background_colour = LIGHT_BLUE

        self.track_pos : list[int] = []
 
        self.num_v_lines = 10
        self.num_h_lines = 5
        self.line_h_spacing = RESOLUTION_Y // 15

        for i in range(0, self.num_h_lines):
            y_value = (i - self.num_h_lines / 2.0) * self.line_h_spacing + RESOLUTION_Y//2
            self.track_pos.append(y_value + self.line_h_spacing / 2)

        self.FALLOFF = 1/10
        self.texts : list[floating_text] = []

        self.width, self.height = RESOLUTION_X, RESOLUTION_Y
        self.XBEGIN = RESOLUTION_X * self.FALLOFF
        self.XEND = RESOLUTION_X 

        self.line_v_spacing = ((self.XEND - self.XBEGIN) / (self.num_v_lines-1)) 

        self.pixel_speed = self.speed * self.line_v_spacing #pixel speed per second
        
        self.TRACKS_WIDTH = RESOLUTION_X * 9 / 10
        self.TRACKS_HEIGHT = RESOLUTION_Y / 3
        self.TRACKS = 4

        self.score_text = Text("Score: 0", (0, 0, 0), (.1, .6), False, 42)
        self.streak_text = Text("Streak: 0", (0, 0, 0), (.1, .65), False, 42)

        self.RED = (255, 0, 0)

        self.GREEN = (0, 255, 0)

        self.BLUE = (0, 0, 255)

        self.YELLOW = (255, 255, 0)

        self.PINK = (255, 51, 153)

        self.PURPLE = (204, 0, 255)

        self.track_colors : list[tuple[int, int, int]] = [
            self.RED,
            self.GREEN,
            self.BLUE,
            self.YELLOW,
            self.PINK,
            self.PURPLE,
        ]
 
        self.notes = [] 
        self.lanes = [Line_input(self, i) for i in range(4)]

        self.background = Background(0)

    def board_render(self):
 
        # Set the dimensions of the image 

        # Define the color (black in this case)
        black = (0, 0, 0,)  # RGBA format
        gray1 = (90, 90, 90,)
        gray2 = (150, 150, 150,)

        width0 = 5
        width1 = 7
        width2 = 3
        width3 = 1

        GRASS_TOP_Y = RESOLUTION_Y//8
        grass = pygame.Rect(0, RESOLUTION_Y - GRASS_TOP_Y, RESOLUTION_X, GRASS_TOP_Y)
        pygame.draw.rect(display, LIGHT_GREEN, grass)

        # Calculate the spacing between lines
        line_spacing = self.height // 15

        for i in range(0, self.num_h_lines):
            y_value = (i - self.num_h_lines / 2.0) * line_spacing + RESOLUTION_Y//2
            pygame.draw.line(display, black, (self.XBEGIN, y_value), (self.XEND, y_value), width0)
        
        YBEGIN = (0 - self.num_h_lines / 2.0) * line_spacing + RESOLUTION_Y//2
        YEND = (self.num_h_lines-1 - self.num_h_lines / 2.0) * line_spacing + RESOLUTION_Y//2

        for i in range(0, self.num_v_lines):
            line_spacing = (self.XEND - self.XBEGIN)/(self.num_v_lines-1)
            x_value = self.XBEGIN + i*line_spacing
            pygame.draw.line(display, black, (x_value, YBEGIN), (x_value, YEND), width1)

        num_v2_lines = self.num_v_lines - 1
        
        for i in range(0, num_v2_lines):
            line_spacing = (self.XEND - self.XBEGIN) / (self.num_v_lines-1)
            x_value = self.XBEGIN + 1/2*line_spacing + i*line_spacing
            pygame.draw.line(display, gray1, (x_value, YBEGIN), (x_value, YEND), width2)
        
        num_v3_lines = 2*num_v2_lines

        for i in range(0, num_v3_lines):
            line_spacing = ((self.XEND - self.XBEGIN) / (self.num_v_lines-1))/2
            x_value = self.XBEGIN + 1/2*line_spacing + i*line_spacing
            pygame.draw.line(display, gray2, (x_value, YBEGIN), (x_value, YEND), width3)

        self.background.update()
        self.background.render()

    def add_score(self, score):
        self.score += score * self.multiplier

    def update_streak(self, score):
        if score > 0:
            if self.streak < 0:
                self.streak = 0
            self.streak += 1
            if self.streak == 10:
                self.draw_text_multiplier2()
            if self.streak >= 20 and self.streak %10 == 0:
                self.draw_text_multiplier3()
        elif score < 0:
            if self.streak > 0:
                self.streak = 1
            self.streak -= 1
 
    def tick(self):
        # RENDER
        display.fill(self.background_colour)
        self.board_render()
        self.score_text.update_text(f"Score: {self.score}")
        self.streak_text.update_text(f"Streak: {self.streak}")
        self.score_text.render()
        self.streak_text.render()
        for text in self.texts:
            text.update()
            text.render()
        text = [text for text in self.texts if text.alive]

        # INPUT AND RENDERING
        for lane in self.lanes:
            lane.update()
            lane.render(self)

        # NOTE LOGIC AND RENDERING
        for note in self.notes:
            score_delta = note.update(self)  
            self.add_score(score_delta)
            self.update_streak(score_delta)         
            note.render(self)

        self.notes = [note for note in self.notes if note.alive]
        pygame.display.update()
        i = self.input_method.get_input()
        if i is not None:
            score_delta = self.lanes[i].pressed(self)
            self.add_score(score_delta)
            self.update_streak(score_delta)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
    def draw_text_perfect(self):
        self.texts.append(floating_text("Perfect!", self.GREEN, 2, 128))
    def draw_text_good(self):
        self.texts.append(floating_text("Good", self.BLUE, 1, 64))
    def draw_text_ok(self):
        self.texts.append(floating_text("ok", (150, 150, 150), 1, 32))
    def draw_text_bad(self):
        self.texts.append(floating_text(random.choice(bad_words), self.RED, 1, 32))
    def draw_text_multiplier2(self):
        self.texts.append(floating_text("X2!!", self.PINK, 3, 170))
    def draw_text_multiplier3(self):
        self.texts.append(floating_text("X3!!!", self.PURPLE, 4, 250))

    def to_ss(self, *coords : tuple[int, int]) -> tuple[int, int]:
        return coords[0] * RESOLUTION_X, coords[1] * RESOLUTION_Y

    def start_game(self, rhythm : Rhythm):
        rhythm.reset()
        display.fill(self.background_colour)
        self.board_render()

        self.speed = rhythm.bpm/60.0
        self.pixel_speed = self.speed * self.line_v_spacing #pixel speed per second
        self.background.speed = self.pixel_speed/self.tick_rate

        total_ticks = 0

        previous = time.time()
        fc = 0
        min_dt = 1 / self.tick_rate
        tick_stopper = 0

        while True:
            # TIME FPS
            fc += 1
            now = time.time()
            if now - previous > 1:
                previous = now
                #print(f"fps: {fc}")
                fc = 0

            self.tick()

            if len(rhythm.track) > 0:
                if ((1.0*total_ticks)/self.tick_rate)*self.speed > rhythm.track[0][1]:
                    self.notes.append(Beat(self, rhythm.track[0][0], self.speed, self.tick_rate))
                    rhythm.track = rhythm.track[1:]
            else:
                tick_stopper += 1
            
            if tick_stopper/self.tick_rate*self.speed > 11:
                break

            delta = time.time() - now
            if min_dt - delta > 0:
                time.sleep(min_dt - delta)

            total_ticks += 1


# rhythm1 = Rhythm(60, 4, [(0,0),(0,1),(1,1.5), (0,2),(0,3),(1,3.5), (0, 4)])
# rhythm1 = Rhythm(120, 16, [(0,0),(1,1.5),(0,2),(1,3),(1,3.5),(0,0+4),(1,1.5+4),(0,2+4),(1,3+4),(1,3.5+4),(0,8),(1,9),(0,9.5),(1,10),(1,10.5),(0,11),(1,12),(1,13),(0,13.5),(0,14),(1,15),(0,16)])
rhythm1 = Rhythm(60, 12, [(0,0),(2,0.5),(0,1),(2,1.5),(0,0+2),(2,0.5+2),(0,1+2),(2,1.5+2),(0,0+4),(2,0.25+4),(1,0.5+4),(2,0.75+4),(0,1+4),(2,1.25+4),(1,1.5+4),(2,1.75+4),(0,0+6),(1,0.25+6),(2,0.5+6),(1,0.75+6),(0,1+6),(1,1.25+6),(2,1.5+6),(1,1.75+6),(0,0+8),(1,0.5+8),(0,1+8),(1,1.5+8),(2,0+2+8),(1,0.5+2+8),(1,1+2+8),(0,1.5+2+8),(1,11.75),(0,12)])