import pygame, random, math, os

C_START, C_MIDDLE, C_END = (72, 224, 255), (255, 255, 255), (255, 28, 190)
C_RED, C_HOT_PINK = (255, 42, 72), (255, 48, 220)
COLORS = (C_START, (140, 104, 255), C_END, C_END, C_HOT_PINK, C_HOT_PINK,
          C_RED, C_RED, C_RED, (255, 226, 68))

SLOW, TRAVEL_SCALE = .95, 3.2
TARGET_FPS, EFFECT_SECONDS = 60, 1.5
EFFECT_FRAMES = round(TARGET_FPS * EFFECT_SECONDS)
DEFAULT_ANGLE, DEFAULT_CONE_WIDTH, DEFAULT_SIDE = 180, 24, 0

EFFECT_SCALE = 3.0
ACTIVITY_PULSE, ACTIVITY_PULSE_SPEED = .06, .70
ACTIVITY_WOBBLE, ACTIVITY_ANGLE_WOBBLE = .75, .75

SCATTER_COUNT = 46
STREAK_LIFE, STREAK_SPEED = (EFFECT_FRAMES - 30, EFFECT_FRAMES - 24), (5, 17)
STREAK_SCALE, STREAK_SIZE = (.16, .60), 4.0
STREAK_LANE_OFFSET = (-9, 9)
STREAK_THICKNESS = .35
STREAK_BRIGHTNESS = .90

CORE_DELAY = 9
STAR_LIFE = 13
BEAM_LIFE = EFFECT_FRAMES - CORE_DELAY - STAR_LIFE
BEAM_SPEED = (5, 8)
BEAM_SIZE = 3
BEAM_LAYERS = ((C_HOT_PINK, 1.00), (C_RED, .78), (None, .60))
BEAM_INNER_SCALE = .42
BEAM_SHRINK_AT, BEAM_SHRINK = 10, .84
BEAM_THICKNESS = (1.5, .14)

STAR_FRAMES = 24
BEAM_STAR_CHANCE, BEAM_STAR_COUNT = .20, 1
STAR_PATH = (.36, .62)
STAR_SPEED = (.2, 1.6)
STAR_SCALE, GLINT_SCALE, STAR_SIZE = (.42, .92), 1.65, .50
STAR_DRIFT_JITTER = 12
GLINT_SPIN, GLINT_SHRINK, GLINT_POP_FRAMES = (-8, 8), .90, 2

FADE_LEAD_IN, FADE_FRAMES = 2, 6
GLINT_DOT_FADE, GLINT_DOT_RADIUS = .45, 1
SIDE_LEAN = 7

effects = []

asset_dir = os.path.dirname(__file__)
if os.path.isdir(os.path.join(asset_dir, "assets", "ko_beam_assets")):
    asset_dir = os.path.join(asset_dir, "assets", "ko_beam_assets")
assets, tinted = {}, {}


def _load():
    if assets:
        return
    for name in ("beam", "streak", "glint"):
        assets[name] = pygame.image.load(os.path.join(asset_dir, name + ".png")).convert_alpha()


def _image(name, color):
    key = name, color
    if key not in tinted:
        tinted[key] = assets[name].copy()
        tinted[key].fill(color, special_flags=pygame.BLEND_RGB_MULT)
    return tinted[key]


def _draw_sprite(surface, name, pos, angle, scale, color, alpha=255, thickness=1):
    source = _image(name, color)
    size = max(1, round(source.get_width() * scale)), max(1, round(source.get_height() * scale * thickness))
    image = pygame.transform.rotozoom(pygame.transform.scale(source, size), -angle, 1)
    shade = max(0, min(255, int(alpha)))
    if shade < 255:
        image = image.copy()
        image.fill((shade, shade, shade), special_flags=pygame.BLEND_RGB_MULT)
    surface.blit(image, image.get_rect(center=(round(pos.x), round(pos.y))),
                 special_flags=pygame.BLEND_ADD)


def _draw_streak(surface, pos, angle, scale, color, fade, thickness):
    direction = pygame.Vector2(1, 0).rotate(angle)
    half_length = assets["streak"].get_width() * scale / 2
    half_width = max(1, assets["streak"].get_height() * scale * thickness / 2)
    tail, head = pos - direction * half_length, pos + direction * half_length
    color = tuple(round(channel * fade) for channel in color)
    glow = tuple(round(channel * .28) for channel in color)
    
    pygame.draw.line(surface, glow, tail, head, max(1, round(half_width * 2.5)))
    pygame.draw.line(surface, color, tail, head, max(1, round(half_width * 1.4)))


def _stars(source):
    for _ in range(BEAM_STAR_COUNT):
        middle_pos = source.origin.lerp(source.pos, random.uniform(*STAR_PATH))
        effects.append(Effect(middle_pos, source.angle + random.uniform(-STAR_DRIFT_JITTER, STAR_DRIFT_JITTER), STAR_LIFE,
                          random.uniform(*STAR_SPEED) * TRAVEL_SCALE,
                          random.uniform(*STAR_SCALE) * GLINT_SCALE * STAR_SIZE * EFFECT_SCALE,
                          random.choice(COLORS), "glint"))


class Effect:
    def __init__(self, center, angle, life, speed, scale, color, sprite, delay=0):
        self.pos = pygame.Vector2(center)
        self.origin = pygame.Vector2(center)
        self.angle, self.life, self.max_life = angle, life, life
        self.vel = pygame.Vector2(speed, 0).rotate(angle)
        self.scale, self.color, self.sprite = scale, color, sprite
        self.delay, self.spin = delay, random.uniform(*GLINT_SPIN)
        self.age, self.phase = 0, random.uniform(0, math.tau)

    def update(self):
        if self.delay:
            self.delay -= 1
            return
        self.life -= 1
        self.age += 1
        self.pos += self.vel
        self.vel *= SLOW

        if self.sprite == "glint":
            self.angle += self.spin
            self.scale *= GLINT_SHRINK
        elif self.sprite == "beam":
            if self.life < BEAM_SHRINK_AT:
                self.scale *= BEAM_SHRINK
            if self.life < STAR_FRAMES and random.random() < BEAM_STAR_CHANCE:
                _stars(self)

    def draw(self, surface):
        if self.delay:
            return
        fade = min(1, (self.life + FADE_LEAD_IN) / FADE_FRAMES)
        wave = math.sin(self.age * ACTIVITY_PULSE_SPEED + self.phase)
        pulse = 1 + wave * ACTIVITY_PULSE
        wobble = pygame.Vector2(ACTIVITY_WOBBLE * EFFECT_SCALE, 0).rotate(
            self.angle + 90) * wave
        draw_pos = self.pos + wobble

        if self.sprite == "streak":
            _draw_streak(surface, draw_pos, self.angle, self.scale, self.color,
                        fade * STREAK_BRIGHTNESS, STREAK_THICKNESS)
            return

        draw_scale = self.scale * pulse
        draw_angle = self.angle + wave * ACTIVITY_ANGLE_WOBBLE

        if self.sprite == "glint":
            pop = min(1, (self.max_life - self.life + 1) / GLINT_POP_FRAMES)
            _draw_sprite(surface, "glint", draw_pos, draw_angle, draw_scale * pop,
                        self.color, 255 * fade * pop)
            if fade > GLINT_DOT_FADE:
                pygame.draw.circle(surface, C_MIDDLE, (round(draw_pos.x), round(draw_pos.y)),
                                   max(1, round(GLINT_DOT_RADIUS * STAR_SIZE * EFFECT_SCALE * pulse)))
            return

        age = 1 - self.life / self.max_life
        thin = (BEAM_THICKNESS[0] + (BEAM_THICKNESS[1] - BEAM_THICKNESS[0]) * age) * pulse
        _draw_sprite(surface, "beam", draw_pos, draw_angle, draw_scale,
                    self.color, 255 * fade, thin)
        _draw_sprite(surface, "beam", draw_pos, draw_angle, draw_scale * BEAM_INNER_SCALE,
                    C_MIDDLE, 255 * fade, thin)


def start(center, target_angle=DEFAULT_ANGLE, cone_width=DEFAULT_CONE_WIDTH, side=DEFAULT_SIDE):
    target_angle += side * SIDE_LEAN
    center = pygame.Vector2(center)
    lane_normal = pygame.Vector2(1, 0).rotate(target_angle).rotate(90)
    for _ in range(SCATTER_COUNT):
        lane_center = center + lane_normal * random.uniform(*STREAK_LANE_OFFSET) * EFFECT_SCALE
        effects.append(Effect(lane_center, target_angle,
                          random.randint(*STREAK_LIFE), random.uniform(*STREAK_SPEED) * TRAVEL_SCALE,
                          random.uniform(*STREAK_SCALE) * STREAK_SIZE * EFFECT_SCALE,
                          random.choice(COLORS), "streak"))

    for color, scale in BEAM_LAYERS:
        color = random.choice(COLORS) if color is None else color
        effects.append(Effect(center, target_angle, BEAM_LIFE, random.uniform(*BEAM_SPEED) * TRAVEL_SCALE,
                          scale * BEAM_SIZE * EFFECT_SCALE, color, "beam", CORE_DELAY))


def update():
    for effect in effects[:]:
        effect.update()
    effects[:] = [effect for effect in effects if effect.life > 0]


def draw(surface):
    _load()
    for effect in effects:
        effect.draw(surface)