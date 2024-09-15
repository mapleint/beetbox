import pygame
from pvrecorder import PvRecorder
from detect_peaks import detect_peaks
from rhythm import Rhythm

pygame.mixer.init()

background_colour = (234, 212, 252) 
RESOLUTION = (1920, 1080)
RESOLUTION_X, RESOLUTION_Y = RESOLUTION

display = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption(f'Beetbox @{RESOLUTION_X}x{RESOLUTION_Y}')

kicksound = pygame.mixer.Sound('kick.wav')

recorder = PvRecorder(device_index=-1, frame_length=64)

history = []

MAX_HISTORY = 44100 * 10

def to_ss(*coords : tuple[int, int]) -> tuple[int, int]:
    return coords[0] * RESOLUTION_X, coords[1] * RESOLUTION_Y

#inner third should be 

# 
TRACKS_WIDTH = RESOLUTION_X * 9 / 10
TRACKS_HEIGHT = RESOLUTION_Y / 3
TRACKS = 4

RED = (255, 0, 0)

GREEN = (0, 255, 0)

BLUE = (0, 0, 255)

YELLOW = (255, 255, 0)

track_colors : list[tuple[int, int, int]] = [
    RED,
    GREEN,
    BLUE,
    YELLOW,
]

track_pos : list[int] = []

FALLOFF = 1/10

width, height = RESOLUTION_X, RESOLUTION_Y
XBEGIN = RESOLUTION_X * FALLOFF
XEND = RESOLUTION_X
num_v_lines = 10

line_v_spacing = (XEND - XBEGIN)/(num_v_lines-1)

def board_render():
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
    line_spacing = height // 15

    # Draw four horizontal lines on the surface
    num_h_lines = 5

    for i in range(0, num_h_lines):
        y_value = (i - num_h_lines / 2.0) * line_spacing + RESOLUTION_Y//2
        track_pos.append(y_value + line_spacing / 2)
        pygame.draw.line(display, black, (XBEGIN, y_value), (XEND, y_value), width0)
    
    YBEGIN = (0 - num_h_lines / 2.0) * line_spacing + RESOLUTION_Y//2
    YEND = (num_h_lines-1 - num_h_lines / 2.0) * line_spacing + RESOLUTION_Y//2

    for i in range(0, num_v_lines):
        line_spacing = (XEND - XBEGIN)/(num_v_lines-1)
        x_value = XBEGIN + i*line_spacing
        pygame.draw.line(display, black, (x_value, YBEGIN), (x_value, YEND), width1)

    num_v2_lines = num_v_lines - 1
    
    for i in range(0, num_v2_lines):
        line_spacing = (XEND - XBEGIN) / (num_v_lines-1)
        x_value = XBEGIN + 1/2*line_spacing + i*line_spacing
        pygame.draw.line(display, gray1, (x_value, YBEGIN), (x_value, YEND), width2)
    
    num_v3_lines = 2*num_v2_lines

    for i in range(0, num_v3_lines):
        line_spacing = ((XEND - XBEGIN) / (num_v_lines-1))/2
        x_value = XBEGIN + 1/2*line_spacing + i*line_spacing
        pygame.draw.line(display, gray2, (x_value, YBEGIN), (x_value, YEND), width3)
    
class Line_input:
    size = RESOLUTION_Y / 40
    def __init__(self, track : int):
        self.track = track
        self.y = track_pos[track] / RESOLUTION_Y
        self.x = FALLOFF
        self.size = Line_input.size
        self.color = track_colors[track]

    def render(self):
        pygame.draw.circle(display, self.color, to_ss(self.x, self.y), self.size, int(self.size/3))
        return

    def update(self):
        self.size = self.size - (self.size - Line_input.size) * .05

    def pressed(self):
        self.size = Line_input.size * 1.3
        notes_in_lane = [note for note in notes if note.track == self.track]
        notes_in_lane.sort(key = lambda note: abs(self.x - note.x))
        if not notes_in_lane:
            return
        note = notes_in_lane[0]
        if abs(note.x - self.x) < .03:
            note.alive = False
            print("hit")
        else:
            print('missed')


cooldown = 90
tick_rate=60
min_dt = 1 / tick_rate
fc = 0

speed = 2 #line speed per second

class Beat:
    size = RESOLUTION_Y / 50
    def __init__(self, track : int):
        # in game coords are not resolution based
        self.track = track
        self.y = track_pos[track] / RESOLUTION_Y
        self.x = 1 + self.size / RESOLUTION_X
        pixel_speed = speed * line_v_spacing #pixel speed per second
        window_speed = pixel_speed / RESOLUTION_X #window speed per second
        window_speed_tick = window_speed / tick_rate #window speed per tick
        self.dx = - window_speed_tick
        self.color = track_colors[track]
        self.muted_color = [int(amp * .9) for amp in self.color]
        self.size = Beat.size
        self.alive = True
        return

    def render(self):
        pygame.draw.circle(display, self.color, to_ss(self.x, self.y), self.size, 0)
        pygame.draw.circle(display, self.muted_color, to_ss(self.x, self.y), self.size * .8, 0)
        return

    def update(self):
        if self.x > FALLOFF - Beat.size / RESOLUTION_X:
            self.x += self.dx
        else:
            self.x += self.dx * (self.size / Beat.size) / 1.5
            self.size = self.size * 96 / 100
            if self.size < 0.5:
                print("note died")
                self.alive = False
        return

display.fill(background_colour)
board_render()

pygame.display.flip() 


lanes = [Line_input(i) for i in range(4)]

notes = [Beat(i) for i in range(4)]

import time

cooldown = 90
tick_rate = 60
min_dt = 1 / tick_rate
fc = 0

import math

pygame.font.init()
comic_sans = pygame.font.SysFont('Comic Sans MS', 32)

class floating_text:
    def __init__(self, text, color, fade_speed, size):
        self.text = text
        self.color = color
        self.size = size
        self.start = time.time()
        self.end = self.start + fade_speed
        self.alive = True
        self.x = 200
        self.y = 200
        self.surface = comic_sans.render(self.text, True, self.color)
        self.progress = 0

    def update(self):
        self.progress = (time.time() - self.start) / (self.end - self.start)
        self.y -= 1.5
        if time.time() > self.end:
            self.alive = False

    def render(self):
        alpha_surf = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
        progress = self.progress ** 3
        progress = max(min(1, progress), 0)
        progress = 1 - progress

        alpha_surf.fill((255, 255, 255, int(255 * progress)))
        txt = self.surface.copy()
        txt.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        display.blit(txt, (self.x, self.y))
        pass

previous = time.time()

texts : list[floating_text] = []

def draw_text(jkk):
    texts.append(floating_text("Perfect!", RED, 1, 100))


notes = [Beat(i) for i in range(4)]

import time
import random

previous = time.time()

rhythm1 = Rhythm(60, 4, [(0,0),(0,1),(1,1.5), (0,2),(0,3),(1,3.5)])

try:
    recorder.start()

    while True:
        if random.random() < .02:
            rint = random.randint(0, 3)
            notes.append(Beat(rint))

        # TIME FPS
        fc += 1
        now = time.time()
        if now - previous > 1:
            previous = now
            print(f"fps: {fc}")
            fc = 0


        # RENDER
        display.fill(background_colour)
        board_render()

        for text in texts:
            text.update()
            text.render()
        text = [text for text in texts if text.alive]


        # INPUT AND RENDERING
        for lane in lanes:
            lane.update()
            lane.render()

        # NOTE LOGIC AND RENDERING
        for note in notes:
            note.update()
            note.render()

        notes = [note for note in notes if note.alive]


        pygame.display.update()


        frame = recorder.read()
        history.extend(frame)
        if len(history) > MAX_HISTORY:
            history = history[64:]

        for event in pygame.event.get():
            # INPUT HANDLING
            if event.type == pygame.KEYDOWN:
                keys = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f] 
                for i, key in enumerate(keys):
                    if event.key == key:
                        lanes[i].pressed()
                
            
            if event.type == pygame.QUIT:
                recorder.stop()
                pygame.quit()
                exit()

        delta = time.time() - now
        if min_dt - delta > 0:
            time.sleep(min_dt - delta)

except KeyboardInterrupt:
    recorder.stop()
finally:
    recorder.delete()
