import pygame

class SoundPlayer:
    def __init__(self, sound_mapping):
        pygame.mixer.init()
        self.sound_mapping = sound_mapping  # Map labels to sound files

    def play_sound(self, label):
        sound_file = self.sound_mapping[label]
        sound = pygame.mixer.Sound(sound_file)
        sound.play()
