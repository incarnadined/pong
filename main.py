from __future__ import annotations
import math as maths
from re import X
import pygame
import copy
import random

WIDTH = 1200
HEIGHT = 800
FPS = 60
SPEED = 500 # ball speed

HIGHLIGHT = (255, 255, 255) # highlighted colour

def invert_colour(colour: tuple) -> tuple:
    return ((colour[0]-128)*-1+127, (colour[1]-128)*-1+127, (colour[2]-128)*-1+127)

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def polar(cls, r, theta):
        return cls(r*maths.cos(maths.pi*theta/180), r*maths.sin(maths.pi*theta/180))

    def __mul__(self, other: float):
        if type(other) == float:
            return Vec2(self.x * other, self.y * other)
        return NotImplemented

    def __iadd__(self, other: Vec2):
        if type(other) == Vec2:
            self.x += other.x
            self.y += other.y
            return self
        return NotImplemented

    def __iter__(self):
        return iter([self.x, self.y])

    def __getitem__(self, key):
        if key == 0:
            return self.x
        return self.y

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

class Ball:
    def __init__(self, initial_location, direction=0, radius=12, colour=HIGHLIGHT):
        self.initial_location = copy.deepcopy(initial_location)
        self.location = initial_location
        self.velocity = Vec2.polar(SPEED, direction) # direction is an angle measured anticlockwise from the i unit vector (in degrees)
        self.radius = radius
        self.colour = colour

    def move(self, dt):
        self.location += self.velocity * dt

    def draw(self, screen):
        pygame.draw.circle(screen, self.colour, tuple(self.location), self.radius)

    def bounce(self):
        print("BOUNCED")
        if self.location.y < (0 + self.radius) or self.location.y > (HEIGHT - self.radius):
            self.velocity = Vec2(self.velocity.x, -self.velocity.y)

    def score(self, scores):
        if self.location.x < 0:
            scores = [scores[0], scores[1]+1]
        elif self.location.x > WIDTH:
            scores = [scores[0]+1, scores[1]]
        else:
            return scores
        
        self.location = copy.deepcopy(self.initial_location)
        self.location.y = random.randint(0, HEIGHT)
        self.velocity = Vec2.polar(SPEED, random.choice([0, 180]))
        return scores


class Paddle:
    def __init__(self, width, height, location, colour=HIGHLIGHT):
        self.width = width
        self.height = height
        self.initial_location = copy.deepcopy(location)
        self.location = location
        self.rect = pygame.Rect(*self.location, self.width, self.height)
        self.colour = colour

    def reset(self):
        self.location = copy.deepcopy(self.initial_location)

    def draw(self, screen):
        self.rect = pygame.Rect(*self.location, self.width, self.height)
        pygame.draw.rect(screen, self.colour, self.rect)

    def mouse_move(self):
        self.location = Vec2(self.location[0],  pygame.mouse.get_pos()[1]-self.height/2)

    def keyboard_move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.location += Vec2(0, -10)
            return
        if keys[pygame.K_s]:
            self.location += Vec2(0, 10)
            return


class Button:
    def __init__(self, text, location, font, text_colour):
        self.text = text
        self.location = location
        self.rect = pygame.Rect(*self.location, font.size(text)[0]+10, font.size(text)[1]+10)
        self.font = font
        self.text_colour = text_colour
        self.active_colour = text_colour

    def hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.active_colour = invert_colour(self.text_colour)
        else:
            self.active_colour = self.text_colour

    def draw(self, screen):
        pygame.draw.rect(screen, invert_colour(self.active_colour), self.rect) # body
        pygame.draw.rect(screen, self.active_colour, self.rect, width = 1) # border
        
        rendered_text = self.font.render(self.text, True, self.active_colour)
        screen.blit(rendered_text, self.location)

    def clicked(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

if __name__ == "__main__":

    pygame.init()
    # pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    title_font = pygame.font.Font("Blippo Bold.ttf", 200)
    player_font = pygame.font.Font("Blippo Bold.ttf", 100)
    score_font = pygame.font.Font("Blippo Bold.ttf", 150)
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock() 

    title_screen = True
    title = title_font.render("PONG", True, HIGHLIGHT)
    players_one = Button("1 Player", (150, 600), player_font, HIGHLIGHT)
    players_two = Button("2 Players", (650, 600), player_font, HIGHLIGHT)

    divider = [pygame.Rect(590, 30*i-30, 5, 15) for i in range(0, int(HEIGHT/15))]
    paddles = [Paddle(15, 80, Vec2(1150, 380)), Paddle(15, 80, Vec2(50, 380))]
    ball = Ball(Vec2(WIDTH/2, HEIGHT/2), random.choice([0, 180]))

    players = 0
    scores = [0, 0]
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    title_screen = True
                    scores = [0, 0]
                    for paddle in paddles:
                        paddle.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if title_screen:
                    if players_one.clicked():
                        players = 1
                        title_screen = False
                    elif players_two.clicked():
                        players = 2
                        title_screen = False

        screen.fill(invert_colour(HIGHLIGHT))

        if title_screen:
            screen.blit(title, (350, 40))
            players_one.hover()
            players_one.draw(screen)
            players_two.hover()
            players_two.draw(screen)
        else:
            for rect in divider:
                pygame.draw.rect(screen, HIGHLIGHT, rect)
            paddles[0].mouse_move()
            if players == 2:
                paddles[1].keyboard_move()
            for paddle in paddles:
                paddle.draw(screen)

            ball.move(dt / 1000)
            ball.draw(screen)

            scores_text = score_font.render(f"{scores[0]}   {scores[1]}", True, HIGHLIGHT)
            screen.blit(scores_text, (WIDTH/2 - score_font.size(f"{scores[0]}   {scores[1]}")[0]/2, 30))

            scores = ball.score(scores)

        pygame.display.flip()       

    pygame.quit()