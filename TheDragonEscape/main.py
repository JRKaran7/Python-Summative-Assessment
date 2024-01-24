import os
import random
from enum import IntEnum, auto
import pygame.sprite
import asyncio

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500
FPS = 60
GRAVITY = 0.4

sprite = {}
audios = {}


def sprites_load():
    path = os.path.join("assets", "sprites")
    for file in os.listdir(path):
        sprite[file.split('.')[0]] = pygame.image.load(os.path.join(path, file))


def sprites_get(name):
    return sprite[name]


def load_audios():
    path = os.path.join("assets", "audios")
    for file in os.listdir(path):
        audios[file.split('.')[0]] = pygame.mixer.Sound(os.path.join(path, file))


def play_audio(name):
    audios[name].play()


class Layer(IntEnum):
    BACKGROUND = auto()
    OBSTACLE = auto()
    FLOOR = auto()
    DRAGON = auto()
    UI = auto()


class Back(pygame.sprite.Sprite):
    def __init__(self, index, *groups):
        self.image = sprites_get("gamebackground")
        self.rect = self.image.get_rect(topleft=(SCREEN_WIDTH * index, 0))
        super().__init__(*groups)

    def update(self):
        self.rect.x -= 3

        if self.rect.right <= 0:
            self.rect.x = SCREEN_WIDTH


class Dragon(pygame.sprite.Sprite):
    def __init__(self, *groups):
        self._layer = Layer.DRAGON

        self.images = [
            sprites_get("DM"),
            sprites_get("DT"),
            sprites_get("DD"),
            sprites_get("DMD"),
            sprites_get("DMT")
        ]

        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=(-50, 50))

        self.mask = pygame.mask.from_surface(self.image)

        self.flap = 0

        super().__init__(*groups)

    def update(self):
        self.images.insert(0, self.images.pop())
        self.image = self.images[0]

        self.flap += GRAVITY
        self.rect.y += self.flap

        if self.rect.x < 50:
            self.rect.x += 3

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.flap = 0
            self.flap -= 6
            play_audio("wave1")

    def check_collision(self, sprites):
        for sprite in sprites:
            if ((type(sprite) is Pole or type(sprite) is Floor) and sprite.mask.overlap(self.mask, (
                    self.rect.x - sprite.rect.x, self.rect.y - sprite.rect.y)) or
                    self.rect.bottom < 0):
                return True
        return False


class Floor(pygame.sprite.Sprite):
    def __init__(self, index, *groups):
        self._layer = Layer.FLOOR
        self.image = sprites_get("ground")
        self.rect = self.image.get_rect(bottomleft=(SCREEN_WIDTH * index, SCREEN_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        super().__init__(*groups)

    def update(self):
        self.rect.x -= 3

        if self.rect.right <= 0:
            self.rect.x = SCREEN_WIDTH


class GameOverMessage(pygame.sprite.Sprite):
    def __init__(self, *groups):
        self._layer = Layer.UI
        self.image = sprites_get("gameover")
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        super().__init__(*groups)


class GameStartMessage(pygame.sprite.Sprite):
    def __init__(self, *groups):
        self._layer = Layer.UI
        self.image = sprites_get("message")
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        super().__init__(*groups)


class Pole(pygame.sprite.Sprite):
    def __init__(self, *groups):
        self._layer = Layer.OBSTACLE
        self.gap = 110

        self.sprite = sprites_get("TOTEM_COLUMN")
        self.sprite_rect = self.sprite.get_rect()

        self.pipe_bottom = self.sprite
        self.pipe_bottom_rect = self.pipe_bottom.get_rect(topleft=(0, self.sprite_rect.height + self.gap))

        self.pipe_top = pygame.transform.flip(self.sprite, False, True)
        self.pipe_top_rect = self.pipe_top.get_rect(topleft=(0, 0))

        self.image = pygame.surface.Surface((self.sprite_rect.width, self.sprite_rect.height * 2 + self.gap),
                                            pygame.SRCALPHA)
        self.image.blit(self.pipe_bottom, self.pipe_bottom_rect)
        self.image.blit(self.pipe_top, self.pipe_top_rect)

        sprite_floor_height = sprites_get("ground").get_rect().height
        min_y = 200
        max_y = SCREEN_HEIGHT - sprite_floor_height - 100

        self.rect = self.image.get_rect(midleft=(SCREEN_WIDTH, random.uniform(min_y, max_y)))
        self.mask = pygame.mask.from_surface(self.image)

        self.passed = False

        super().__init__(*groups)

    def update(self):
        self.rect.x -= 3

        if self.rect.right <= 0:
            self.kill()

    def is_passed(self):
        if self.rect.x < 50 and not self.passed:
            self.passed = True
            return True
        return False


class Score(pygame.sprite.Sprite):
    def __init__(self, *groups):
        self._layer = Layer.UI
        self.value = 0
        self.image = pygame.surface.Surface((0, 0), pygame.SRCALPHA)

        self.__create()

        super().__init__(*groups)

    def __create(self):
        self.str_value = str(self.value)

        self.images = []
        self.width = 0

        for str_value_char in self.str_value:
            img = sprites_get(str_value_char)
            self.images.append(img)
            self.width += img.get_width()

        self.height = self.images[0].get_height()
        self.image = pygame.surface.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, 50))

        x = 0
        for img in self.images:
            self.image.blit(img, (x, 0))
            x += img.get_width()

    def update(self):
        self.__create()


async def run():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    column_create_event = pygame.USEREVENT
    running = True
    gameover = False
    gamestarted = False

    sprites_load()
    load_audios()

    sprites = pygame.sprite.LayeredUpdates()

    def create_sprites():
        Back(0, sprites)
        Back(1, sprites)
        Floor(0, sprites)
        Floor(1, sprites)

        return Dragon(sprites), GameStartMessage(sprites), Score(sprites)

    bird, game_start_message, score = create_sprites()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == column_create_event:
                Pole(sprites)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not gamestarted and not gameover:
                    gamestarted = True
                    game_start_message.kill()
                    pygame.time.set_timer(column_create_event, 1500)
                if event.key == pygame.K_ESCAPE and gameover:
                    gameover = False
                    gamestarted = False
                    sprites.empty()
                    bird, game_start_message, score = create_sprites()

            if not gameover:
                bird.handle_event(event)

        screen.fill('white')

        sprites.draw(screen)

        if gamestarted and not gameover:
            sprites.update()

        if bird.check_collision(sprites) and not gameover:
            gameover = True
            gamestarted = False
            GameOverMessage(sprites)
            pygame.time.set_timer(column_create_event, 0)
            play_audio("hit1")

        for sprite in sprites:
            if type(sprite) is Pole and sprite.is_passed():
                score.value += 1
                play_audio("point")

        pygame.display.update()
        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.display.update()


asyncio.run(run())
pygame.quit()
