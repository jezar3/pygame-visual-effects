import colorsys
import math
import random

import pygame

LIGHT_RED_HUE_SHIFT = 167
LIGHT_BLUE_HUE_SHIFT = 68
LIGHT_GREEN_HUE_SHIFT = -92
HEAVY_RED_HUE_SHIFT = 22
HEAVY_BLUE_HUE_SHIFT = -122
HEAVY_GREEN_HUE_SHIFT = 170

CYAN = (40, 200, 255)
WHITE = (255, 255, 255)
PALE_BLUE = (110, 225, 255)
YELLOW = (255, 220, 40)
RED = (252, 3, 94)
MAGENTA = (252, 3, 119)

LIGHT_PALETTE = (CYAN, WHITE, PALE_BLUE)
LIGHT_DOT_COLOR = YELLOW
HEAVY_PALETTE = (RED, WHITE, MAGENTA)

LIGHT_SPLASH_COUNT = 8
LIGHT_DOT_COUNT = 14
HEAVY_SCATTER_COUNT = 28
SLOW_DECAY = 0.82
EFFECTS = []


def _shift_color(color, hue_shift):
    hue, saturation, value = colorsys.rgb_to_hsv(*(channel / 255 for channel in color))
    red, green, blue = colorsys.hsv_to_rgb((hue + hue_shift / 360) % 1, saturation, value)
    return round(red * 255), round(green * 255), round(blue * 255)


class Oval:
    def __init__(self, center, angle, life, speed, half_len, half_thick, palette, dot_color=None):
        self.center = pygame.Vector2(center)
        self.angle = angle
        self.life = life
        self.distance = 0
        self.speed = speed
        self.half_len = half_len
        self.half_thick = half_thick
        self.palette = palette
        self.dot_color = dot_color

    def update(self):
        self.life -= 1
        self.distance += self.speed
        self.speed *= SLOW_DECAY
        if self.life < 10:
            self.half_len *= 0.8
            self.half_thick *= 0.8

    def draw(self, surface):
        travel = pygame.Vector2(self.distance, 0).rotate(self.angle)
        center = self.center + travel
        if self.dot_color is not None:
            pygame.draw.circle(surface, self.dot_color, center, self.half_len)
            return

        if self.life > 10:
            color = self.palette[0]
        elif self.life > 5:
            color = self.palette[1]
        else:
            color = self.palette[2]

        points = []
        for i in range(10):
            corner = math.radians(i * 36)
            local = pygame.Vector2(math.cos(corner) * self.half_len,
                                   math.sin(corner) * self.half_thick)
            points.append(center + local.rotate(self.angle))
        pygame.draw.polygon(surface, color, points)


def _start_light(center, side, hue_shift):
    base = 0 if side > 0 else 180
    palette = tuple(_shift_color(color, hue_shift) for color in LIGHT_PALETTE)
    dot_color = _shift_color(LIGHT_DOT_COLOR, hue_shift)

    for _ in range(LIGHT_SPLASH_COUNT):
        angle = base + random.uniform(-55, 55)
        speed = random.uniform(6, 12)
        life = random.randint(14, 22)
        half_len = random.uniform(5, 9)
        EFFECTS.append(Oval(center, angle, life, speed, half_len, half_len * 0.3,
                            palette, dot_color))

    for _ in range(LIGHT_DOT_COUNT):
        angle = base + random.uniform(-80, 80)
        speed = random.uniform(3, 10)
        life = random.randint(12, 22)
        radius = random.uniform(1.5, 3)
        EFFECTS.append(Oval(center, angle, life, speed, radius, radius, palette, dot_color))


def _start_heavy(center, target_angle, cone_width, hue_shift):
    palette = tuple(_shift_color(color, hue_shift) for color in HEAVY_PALETTE)
    half_cone = cone_width / 2

    for _ in range(HEAVY_SCATTER_COUNT):
        angle = random.uniform(target_angle - half_cone, target_angle + half_cone)
        speed = random.uniform(5, 17)
        life = random.randint(14, 24)
        half_len = random.uniform(4, 9)
        EFFECTS.append(Oval(center, angle, life, speed, half_len, half_len * 0.45, palette))


def start(center, target_angle=180, cone_width=90, side=0, hue_shift=0):
    _start_heavy(center, target_angle, cone_width, hue_shift)


def light_red(center, side=1):
    _start_light(center, side, LIGHT_RED_HUE_SHIFT)


def light_blue(center, side=1):
    _start_light(center, side, LIGHT_BLUE_HUE_SHIFT)


def light_green(center, side=1):
    _start_light(center, side, LIGHT_GREEN_HUE_SHIFT)


def heavy_red(center, target_angle=180, side=0):
    _start_heavy(center, target_angle, 90, HEAVY_RED_HUE_SHIFT)


def heavy_blue(center, target_angle=180, side=0):
    _start_heavy(center, target_angle, 90, HEAVY_BLUE_HUE_SHIFT)


def heavy_green(center, target_angle=180, side=0):
    _start_heavy(center, target_angle, 90, HEAVY_GREEN_HUE_SHIFT)


def update():
    for effect in EFFECTS[:]:
        effect.update()
        if effect.life <= 0:
            EFFECTS.remove(effect)


def draw(surface):
    for effect in EFFECTS:
        effect.draw(surface)
