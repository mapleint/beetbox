import pygame
import random
from display import display

filepath = "/sprites"

class Background:
    def __init__(self, speed):
        self.trees = pygame.sprite.Group()
        self.suns = pygame.sprite.Group()
        self.speed = speed #pixels per tick
        self.add_tree()
        self.add_sun()
        self.add_bird()

    def add_tree(self):
        tree = Tree(self.speed/2)
        self.trees.add(tree)

    def add_sun(self):
        sun = Sun()
        self.suns.add(sun)
    
    def add_bird(self):
        bird = Bird(self.speed/4)
        self.trees.add(bird)
    
    def update(self):
        for obj in self.trees:
            obj.update()
        if random.random() < 0.01*self.speed/2:
            self.add_tree()
        if random.random() < 0.001*self.speed/2:
            self.add_bird()

    def render(self):
        self.trees.draw(display)
        self.suns.draw(display)
    

class Tree(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        # Create an image for the sprite
        image_path = "sprites/tree-removebg-preview.png"
        self.image =  pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (400, 400))
        # Define the rect attribute for positioning
        self.x = 1900
        self.y = 600 + 100 * random.random()
        self.rect = pygame.Rect(self.x, self.y, 100, 100)
        self.speed = speed

    def update(self):
        self.rect = pygame.Rect(self.x, self.y, 100, 100)
        self.x -= self.speed

class Sun(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create an image for the sprite
        image_path = "sprites/sun-removebg-preview.png"
        self.image =  pygame.image.load(image_path).convert_alpha()
        # Define the rect attribute for positioning
        self.x = -100
        self.y = -50
        self.rect = pygame.Rect(self.x, self.y, 100, 100)


class Bird(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        # Create an image for the sprite
        image_path = "sprites/bird1-removebg-preview.png"
        self.image1 =  pygame.transform.rotate(pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (100, 100)), 22)
        image_path = "sprites/bird2-removebg-preview.png"
        self.image2 = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (100, 100)), 22)
        self.image = self.image1
        self.flapping = 0
        self.flapping_counter = 0
        # Define the rect attribute for positioning
        self.x = 2500
        self.y = -50 + 340 * random.random()
        self.rect = pygame.Rect(self.x, self.y, 100, 100)
        self.speed = speed

    def update(self):
        self.rect = pygame.Rect(self.x, self.y, 100, 100)
        self.x -= self.speed
        if not self.flapping:
            if random.random() < 0.005:
                self.flapping = 1
                self.image = self.image2
        else:
            self.flapping_counter += 1
            if self.flapping_counter > 50:
                self.flapping = 0
                self.image = self.image1
                self.flapping_counter = 0
    