import pygame
from pvrecorder import PvRecorder
from detect_peaks import detect_peaks

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

GREEN = (0, 0, 255)

BLUE = (0, 255, 0)

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

    # Calculate the spacing between lines
    line_spacing = height // 20

    # Draw four horizontal lines on the surface
    num_h_lines = 5

    for i in range(0, num_h_lines):
        y_value = (i - num_h_lines / 2.0) * line_spacing + RESOLUTION_Y//2
        track_pos.append(y_value + line_spacing / 2)
        pygame.draw.line(display, black, (XBEGIN, y_value), (XEND, y_value))
    
    YBEGIN = (0 - num_h_lines / 2.0) * line_spacing + RESOLUTION_Y//2
    YEND = (num_h_lines-1 - num_h_lines / 2.0) * line_spacing + RESOLUTION_Y//2

    for i in range(0, num_v_lines):
        line_spacing = (XEND - XBEGIN)/(num_v_lines-1)
        x_value = XBEGIN + i*line_spacing
        pygame.draw.line(display, black, (x_value, YBEGIN), (x_value, YEND))
    
class Line_input:
    size = RESOLUTION_Y / 50
    def __init__(self, track : int):
        self.y = track_pos[track] / RESOLUTION_Y
        self.x = FALLOFF + 2/50
        self.size = Line_input.size
        self.color = (255, 255, 255)

    def render(self):
        pygame.draw.circle(display, self.color, to_ss(self.x, self.y), self.size, 0)
        return

    def update(self):
        self.size = self.size - (self.size - Line_input.size) * .05

    def pressed(self):
        print("pressed")
        self.size = Line_input.size * 1.3


cooldown = 90
tick_rate=60
min_dt = 1 / tick_rate
fc = 0

speed = 2 #line speed per second

class Beat:
    size = RESOLUTION_Y / 50
    def __init__(self, track : int, time : int = 2):
        # in game coords are not resolution based
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

notes = [Beat(i, 1) for i in range(4)]

import time

previous = time.time()

try:
    recorder.start()

    while True:

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

        # NOTE LOGIC AND RENDERING
        for note in notes:
            note.update()
            note.render()
        notes = [note for note in notes if note.alive]

        # INPUT AND RENDERING
        for lane in lanes:
            lane.update()
            lane.render()

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
