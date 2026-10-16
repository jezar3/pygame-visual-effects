import os
import random
import pygame

WALL_COLOR = (235, 245, 255)
WATER_COLOR = (80, 205, 255)
WALL_COUNT = 4
WATER_COUNT = 5
GRAVITY = .16

EFFECTS = []
FRAMES = []
SHEET_PATH = os.path.join(os.path.dirname(__file__), "assets", "splash.png")


def _load_frames():
    if FRAMES:
        return
    sheet = pygame.image.load(SHEET_PATH).convert_alpha()
    frame_width = sheet.get_width() // 6
    for i in range(6):
        FRAMES.append(sheet.subsurface(i * frame_width, 0, frame_width, sheet.get_height()).copy())


class Splash:
    def __init__(self, pos, vel, life, size, color, flip=False):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.life = self.max_life = life
        self.size = size
        self.color = color
        self.flip = flip

    def update(self):
        self.life -= 1
        self.pos += self.vel
        self.vel.y += GRAVITY

    def draw(self, surface):
        frame = min(5, int((1 - self.life / self.max_life) * 6))
        image = FRAMES[frame].copy()
        image.fill(self.color, special_flags=pygame.BLEND_RGB_MULT)
        if self.flip:
            image = pygame.transform.flip(image, True, False)
        image = pygame.transform.scale_by(image, self.size)
        image.set_alpha(round(255 * self.life / self.max_life))
        surface.blit(image, image.get_rect(center=self.pos))


class Drop:
    def __init__(self, pos, vel, life, color):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.life = self.max_life = life
        self.color = color

    def update(self):
        self.life -= 1
        self.pos += self.vel
        self.vel.y += GRAVITY

    def draw(self, surface):
        radius = max(1, round(2 * self.life / self.max_life))
        pygame.draw.circle(surface, self.color, self.pos, radius)


def wall_jump(pos, side=1):
    side = 1 if side >= 0 else -1
    for _ in range(WALL_COUNT):
        vel = side * random.uniform(1, 3), random.uniform(-3, -1)
        EFFECTS.append(Splash(pos, vel, random.randint(9, 13), random.uniform(.6, 1), WALL_COLOR, side < 0))
    for _ in range(3):
        vel = side * random.uniform(.5, 2), random.uniform(-2.5, -.5)
        EFFECTS.append(Drop(pos, vel, random.randint(8, 12), WALL_COLOR))


def water_splash(pos, strength=1):
    for _ in range(WATER_COUNT):
        vel = random.uniform(-3, 3) * strength, random.uniform(-4, -1) * strength
        EFFECTS.append(Splash(pos, vel, random.randint(10, 15), random.uniform(.8, 1.2) * strength,
                              WATER_COLOR, vel[0] < 0))
    for _ in range(4):
        vel = random.uniform(-2.5, 2.5) * strength, random.uniform(-4, -1) * strength
        EFFECTS.append(Drop(pos, vel, random.randint(9, 14), WATER_COLOR))


def update():
    for effect in EFFECTS[:]:
        effect.update()
        if effect.life <= 0:
            EFFECTS.remove(effect)


def draw(surface):
    if EFFECTS:
        _load_frames()
    for effect in EFFECTS:
        effect.draw(surface)
