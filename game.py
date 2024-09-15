from rhythm import Rhythm
from detector_beep import Beat, floating_text, Line_input
import time
import pygame
from pvrecorder import PvRecorder
import time
import random

from display import RESOLUTION, RESOLUTION_X, RESOLUTION_Y, display
from render import Text

class Game:
    def __init__(self):
        self.tick_rate = 60
        self.speed = 2.0 #beats per second

        self.score = 0
        self.streak = 0

        pygame.mixer.init()

        self.background_colour = (234, 212, 252) 

        self.recorder = PvRecorder(device_index=-1, frame_length=64)

        self.track_pos : list[int] = []
 
        self.num_v_lines = 10
        self.num_h_lines = 5
        self.line_spacing = RESOLUTION_Y // 15

        for i in range(0, self.num_h_lines):
            y_value = (i - self.num_h_lines / 2.0) * self.line_spacing + RESOLUTION_Y//2
            self.track_pos.append(y_value + self.line_spacing / 2) 

        self.FALLOFF = 1/10
        self.texts : list[floating_text] = []

        self.width, self.height = RESOLUTION_X, RESOLUTION_Y
        self.XBEGIN = RESOLUTION_X * self.FALLOFF
        self.XEND = RESOLUTION_X 
        
        self.TRACKS_WIDTH = RESOLUTION_X * 9 / 10
        self.TRACKS_HEIGHT = RESOLUTION_Y / 3
        self.TRACKS = 4

        self.score_text = Text("Score: 0", (0, 0, 0), (.1, .6), False, 42)

        self.RED = (255, 0, 0)

        self.GREEN = (0, 255, 0)

        self.BLUE = (0, 0, 255)

        self.YELLOW = (255, 255, 0)

        self.track_colors : list[tuple[int, int, int]] = [
            self.RED,
            self.GREEN,
            self.BLUE,
            self.YELLOW,
        ]
 
        self.notes = [] 
        self.lanes = [Line_input(self, i) for i in range(4)]

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
 
    def tick(self):
        self.recorder.start()
        # RENDER
        display.fill(self.background_colour)
        self.board_render()
        self.score_text.update_text(f"Score: {self.score}")
        self.score_text.render()
        for text in self.texts:
            text.update()
            text.render(self)
        text = [text for text in self.texts if text.alive]

        # INPUT AND RENDERING
        for lane in self.lanes:
            lane.update()
            lane.render(self)

        # NOTE LOGIC AND RENDERING
        for note in self.notes:
            note.update(self)
            note.render(self)

        self.notes = [note for note in self.notes if note.alive]
        pygame.display.update()

        for event in pygame.event.get():
            # INPUT HANDLING
            if event.type == pygame.KEYDOWN:
                keys = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f] 
                for i, key in enumerate(keys):
                    if event.key == key:
                        score_delta = self.lanes[i].pressed(self)
                        self.score += score_delta
                        if score_delta > 0:
                            self.streak += 1
                        elif score_delta < 0:
                            if self.streak > 0:
                                self.streak = 1
                            self.streak -= 1
                
            if event.type == pygame.QUIT:
                print("QUITTING")
                pygame.quit()
                exit()

    def draw_text_perfect(self):
        self.texts.append(floating_text("Perfect!", self.RED, 1, 100))
    def draw_text_good(self):
        self.texts.append(floating_text("Good", self.RED, 1, 100))
    def draw_text_ok(self):
        self.texts.append(floating_text("ok", self.RED, 1, 100))

    def to_ss(self, *coords : tuple[int, int]) -> tuple[int, int]:
        return coords[0] * RESOLUTION_X, coords[1] * RESOLUTION_Y

    def start_game(self, rhythm : Rhythm):
        display.fill(self.background_colour)
        self.board_render()

        self.speed = rhythm.bpm/60.0

        total_ticks = 0

        previous = time.time()
        fc = 0
        cooldown = 90
        min_dt = 1 / self.tick_rate
        tick_stopper = 0

        while True:
            # TIME FPS
            fc += 1
            now = time.time()
            if now - previous > 1:
                previous = now
                print(f"fps: {fc}")
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

    def menu(self):
        
        pass


rhythm1 = Rhythm(120, 4, [(0,0),(0,1),(1,1.5), (0,2),(0,3),(1,3.5), (0, 4)])

game = Game()
game.start_game(rhythm1)