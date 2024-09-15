import pygame
from rhythm import Rhythm
from display import RESOLUTION, RESOLUTION_Y, RESOLUTION_X, display

#inner third should be 
    
class Line_input:
    def __init__(self, game, track : int):
        self.track = track
        self.y = game.track_pos[track] / RESOLUTION_Y
        self.x = game.FALLOFF
        self.constant_size = RESOLUTION_Y / 40
        self.size = RESOLUTION_Y / 40
        self.color = game.track_colors[track]

    def render(self, game):
        pygame.draw.circle(display, self.color, game.to_ss(self.x, self.y), self.size, int(self.size/3))
        return

    def update(self):
        self.size = self.size - (self.size - self.constant_size) * .05

    def pressed(self, game):
        self.size = self.constant_size * 1.3
        notes_in_lane = [note for note in game.notes if note.track == self.track]
        notes_in_lane.sort(key = lambda note: abs(self.x - note.x))
        if not notes_in_lane:
            return -200
        note = notes_in_lane[0]
        if not note.alive:
            print("ERROR")
            return 1
        dist = abs(note.x - self.x)*RESOLUTION_X
        if dist < game.line_v_spacing/2:
            note.alive = False
            if dist < game.line_v_spacing/8:
                game.draw_text_perfect()
                return 500
            elif dist < game.line_v_spacing/4:
                game.draw_text_good()
                return 250
            elif dist < game.line_v_spacing/2:
                game.draw_text_ok()
                return 125
        else:
            game.draw_text_bad()
            return -200

class Beat:
    def __init__(self, game, track : int, speed, tick_rate):
        # in game coords are not resolution based
        self.track = track
        self.y = game.track_pos[track] / RESOLUTION_Y
        self.constant_size = RESOLUTION_Y / 50
        self.size = RESOLUTION_Y / 50
        self.x = 1 + self.size / RESOLUTION_X
        line_v_spacing = (game.XEND - game.XBEGIN)/(game.num_v_lines-1)
        pixel_speed = speed * line_v_spacing #pixel speed per second
        window_speed = pixel_speed / RESOLUTION_X #window speed per second
        window_speed_tick = window_speed / tick_rate #window speed per tick
        self.dx = - window_speed_tick
        self.color = game.track_colors[track]
        self.muted_color = [int(amp * .9) for amp in self.color]
        self.alive = True
        return

    def render(self, game):
        pygame.draw.circle(display, self.color, game.to_ss(self.x, self.y), self.size, 0)
        pygame.draw.circle(display, self.muted_color, game.to_ss(self.x, self.y), self.size * .8, 0)
        return

    def update(self, game):
        if self.x > game.FALLOFF - self.size / RESOLUTION_X:
            self.x += self.dx
        else:
            self.x += self.dx * (self.size / self.constant_size) / 1.5
            self.size = self.size * 90 / 100
            if self.size < 5:
                print("note died")
                self.alive = False
                game.draw_text_bad()
                return -200
        return 0

import time

pygame.font.init()

class floating_text:
    def __init__(self, text, color, fade_speed, size):
        comic_sans = pygame.font.SysFont('Comic Sans MS', size)
        self.text = text
        self.start = time.time()
        self.end = self.start + fade_speed
        self.alive = True
        self.x = 200
        self.y = 200
        self.surface = comic_sans.render(self.text, True, color)
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