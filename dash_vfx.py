import random
import pygame

LINE_SPREAD = 6
RING_GROW = 2
STRETCH_AMOUNT = 1.6
DUST_BURST = 10
CHUNK_BURST = 6
DUST_PER_FRAME = 1
DUST_END = 5
WALK_PUFF_BURST = 2
WALK_CHUNK_BURST = 2
WALK_PUFF_SPEED = 0.45
JUMP_RING_LIFT = 10
DASH_FRAMES = 9
JUMP_TRAIL_FRAMES = 6
DOUBLE_JUMP_LINE_COUNT = 2
DOUBLE_JUMP_SPARK_COUNT = 17
PLAYER_SIZE = 16
PLAYER_COLOR = (80, 200, 255)

YELLOW = (0, 255, 255)
ORANGE = (0, 0, 255)
WHITE = (255, 255, 255)

AIR_BLUE = (WHITE, YELLOW, ORANGE)
AIR_RED = (WHITE, (255, 120, 120), (255, 0, 0))
AIR_GREEN = (WHITE, (120, 255, 120), (0, 255, 0))
DOUBLE_JUMP_SPARK_COLORS = (WHITE, (255, 240, 120), (255, 210, 0))

GROUND_GRASS = ((150, 215, 105), (110, 180, 75), (60, 125, 50))
GROUND_METAL = ((195, 205, 220), (150, 160, 178), (100, 108, 126))
GROUND_CEMENT = ((210, 140, 125), (175, 100, 88), (120, 62, 58))

effects = []


class Ghost:
    def __init__(self, position, color=ORANGE):
        self.pos = pygame.Vector2(position)
        self.color = color
        self.frames_left = 15
        self.alpha = 160

    def update(self):
        self.frames_left -= 1
        self.alpha -= 10

    def draw(self, surface, size):
        img = pygame.Surface((size, size))
        img.fill(self.color)
        img.set_alpha(self.alpha)
        surface.blit(img, img.get_rect(center=self.pos))


class Spark:
    def __init__(self, position, vel, colors=(WHITE, YELLOW, ORANGE), life=(15, 30)):
        self.pos = pygame.Vector2(position)
        self.vel = pygame.Vector2(vel)
        self.colors = colors
        self.frames_left = random.randint(life[0], life[1])

    def update(self):
        self.frames_left -= 1
        self.pos += self.vel
        self.vel *= 0.93

    def draw(self, surface, size):
        if self.frames_left > 10:
            color = self.colors[0]
        elif self.frames_left > 5:
            color = self.colors[1]
        else:
            color = self.colors[2]
        radius = 1 + self.frames_left / 5
        pygame.draw.circle(surface, color, self.pos, radius)


class Ring:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.frames_left = 18
        self.radius = 0
        self.shade = 255

    def update(self):
        self.frames_left -= 1
        self.radius += RING_GROW
        self.shade -= 14

    def draw(self, surface, size):
        thickness = 1 + self.frames_left // 4
        color = (self.shade, self.shade, self.shade)
        pygame.draw.circle(surface, color, self.pos, self.radius, thickness)


class Line:
    def __init__(self, pos, direction):
        self.pos = pygame.Vector2(pos)
        self.direction = pygame.Vector2(direction)
        self.frames_left = 12
        self.length = 36

    def update(self):
        self.frames_left -= 1
        self.length -= 3

    def draw(self, surface, size):
        tail = self.pos - self.direction * self.length
        pygame.draw.line(surface, WHITE, self.pos, tail, 2)


class Puff:
    def __init__(self, pos, vel, life, max_radius, colors):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.life = life
        self.frames_left = life
        self.max_radius = max_radius
        self.colors = colors

    def update(self):
        self.frames_left -= 1
        self.pos += self.vel
        self.vel *= 0.9

    def draw(self, surface, size):
        t = 1 - self.frames_left / self.life
        radius = self.max_radius * min(1, t * 4) * (1 - t)
        if t < 0.3:
            color = self.colors[0]
        elif t < 0.65:
            color = self.colors[1]
        else:
            color = self.colors[2]
        if radius >= 1:
            pygame.draw.circle(surface, color, self.pos, radius)


class Chunk:
    def __init__(self, pos, vel, colors):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.color = colors[random.choice((1, 2))]
        self.floor = self.pos.y
        self.frames_left = 24

    def update(self):
        self.frames_left -= 1
        self.vel.y += 0.3
        self.pos += self.vel
        if self.pos.y >= self.floor:
            self.frames_left = 0

    def draw(self, surface, size):
        pygame.draw.rect(surface, self.color, (round(self.pos.x), round(self.pos.y), 2, 2))


class Trail:
    def __init__(self, pos, direction, colors):
        self.player = pos
        self.direction = pygame.Vector2(direction)
        self.colors = colors
        self.frames_left = DASH_FRAMES

    def update(self):
        self.frames_left -= 1
        effects.append(Ghost(self.player, self.colors[2]))
        vel = (-self.direction).rotate(random.uniform(-25, 25)) * random.uniform(2, 7)
        effects.append(Spark(self.player, vel, self.colors))
        _spawn_lines(self.player, self.direction)

    def draw(self, surface, size):
        pass


class _JumpTrail:
    

    def __init__(self, pos, direction, line_count=2, line_spread=LINE_SPREAD):
        
        self.player = pos
        self.direction = pygame.Vector2(direction)
        self.line_count = line_count
        self.line_spread = line_spread
        self.frames_left = JUMP_TRAIL_FRAMES

    def update(self):
        self.frames_left -= 1
        _spawn_lines(self.player, self.direction, self.line_count, self.line_spread)

    def draw(self, surface, size):
        pass


class DustTrail:
    def __init__(self, pos, direction, colors):
        self.player = pos
        self.direction = pygame.Vector2(direction)
        self.colors = colors
        self.frames_left = DASH_FRAMES

    def puff(self, count, speed=1):
        for i in range(count):
            feet = self.player + pygame.Vector2(random.uniform(-3, 3), PLAYER_SIZE / 2 - 4)
            tilt = random.uniform(0, 30) * self.direction.x
            vel = (-self.direction).rotate(tilt) * random.uniform(0.8, 2.4) * speed
            effects.append(Puff(feet, vel, random.randint(12, 20), random.uniform(2.5, 4.5), self.colors))

    def chunk(self, count):
        for i in range(count):
            feet = self.player + pygame.Vector2(random.uniform(-4, 4), PLAYER_SIZE / 2 - 2)
            vel = pygame.Vector2(-self.direction.x * random.uniform(0.5, 2), -random.uniform(1.2, 2.6))
            effects.append(Chunk(feet, vel, self.colors))

    def update(self):
        self.frames_left -= 1
        self.puff(DUST_PER_FRAME)
        if random.random() < 0.5:
            self.chunk(1)
        if self.frames_left == 0:
            self.puff(DUST_END, 0.5)

    def draw(self, surface, size):
        pass


class Stretch:
    def __init__(self, pos):
        self.player = pos
        self.frames_left = DASH_FRAMES

    def update(self):
        self.frames_left -= 1

    def draw(self, surface, size):
        life = self.frames_left / DASH_FRAMES
        extra = round(size * STRETCH_AMOUNT * life / 2)
        p = self.player
        pygame.draw.rect(surface, PLAYER_COLOR, (p.x - size / 2 - extra, p.y - size / 2, size + 2 * extra, size))


def spawn_air(pos, direction, colors):
    effects.append(Ring(pos))
    for i in range(14):
        vel = (-direction).rotate(random.uniform(-60, 60)) * random.uniform(2, 7)
        effects.append(Spark(pos, vel, colors))
    effects.append(Trail(pos, direction, colors))


def spawn_ground(pos, direction, colors):
    dust = DustTrail(pos, direction, colors)
    dust.puff(DUST_BURST)
    dust.chunk(CHUNK_BURST)
    effects.append(dust)
    effects.append(Stretch(pos))


def _spawn_lines(pos, direction, count=2, spread=LINE_SPREAD):
    direction = pygame.Vector2(direction)
    for i in range(count):
        offset = direction.rotate(90) * random.uniform(-spread, spread)
        effects.append(Line(pos + offset, direction))


def air_dash_red(pos, direction):
    spawn_air(pos, direction, AIR_RED)


def air_dash_green(pos, direction):
    spawn_air(pos, direction, AIR_GREEN)


def air_dash_blue(pos, direction):
    spawn_air(pos, direction, AIR_BLUE)


def ground_dash_grass(pos, direction):
    spawn_ground(pos, direction, GROUND_GRASS)


def ground_dash_metal(pos, direction):
    spawn_ground(pos, direction, GROUND_METAL)


def ground_dash_cement(pos, direction):
    spawn_ground(pos, direction, GROUND_CEMENT)


def _spawn_walk_particles(pos, direction, colors):
    
    direction = pygame.Vector2(direction)
    if direction.length_squared() == 0:
        return

    dust = DustTrail(pos, direction.normalize(), colors)
    dust.puff(WALK_PUFF_BURST, WALK_PUFF_SPEED)
    dust.chunk(WALK_CHUNK_BURST)


def walk_grass(pos, direction):
    
    _spawn_walk_particles(pos, direction, GROUND_GRASS)


def walk_cement(pos, direction):
    
    _spawn_walk_particles(pos, direction, GROUND_CEMENT)


def walk_metal(pos, direction):
    
    _spawn_walk_particles(pos, direction, GROUND_METAL)


def jump_shockwave(pos):
    effects.append(Ring(pos + pygame.Vector2(0, PLAYER_SIZE / 2 - JUMP_RING_LIFT)))


def _spawn_jump_trail(pos, line_count=2, line_spread=LINE_SPREAD):
    effects.append(_JumpTrail(pos, pygame.Vector2(0, -1), line_count, line_spread))


def single_jump(pos):
   
    _spawn_jump_trail(pos)


def double_jump(pos):
   
    jump_shockwave(pos)
    _spawn_jump_trail(pos, DOUBLE_JUMP_LINE_COUNT, LINE_SPREAD * 1.5)
    for i in range(DOUBLE_JUMP_SPARK_COUNT):
        vel = pygame.Vector2(0, 1).rotate(random.uniform(-80, 80)) * random.uniform(2, 5)
        effects.append(Spark(pos, vel, DOUBLE_JUMP_SPARK_COLORS, life=(10, 20)))


def update():
    for fx in effects.copy():
        fx.update()
        if fx.frames_left <= 0:
            effects.remove(fx)


def draw_effects(surface, size):
    for fx in effects:
        if not isinstance(fx, Stretch):
            fx.draw(surface, size)
    for fx in effects:
        if isinstance(fx, Stretch):
            fx.draw(surface, size)
