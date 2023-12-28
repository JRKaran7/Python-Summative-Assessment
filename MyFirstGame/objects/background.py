import pygame.sprite

import assets
import configs
from layer import Layer


class Back(pygame.sprite.Sprite):
    def __init__(self, index, *groups):
        self.image = assets.sprites_get("gamebackground")
        self.rect = self.image.get_rect(topleft=(configs.SCREEN_WIDTH * index, 0))
        super().__init__(*groups)

    def update(self):
        self.rect.x -= 3

        if self.rect.right <= 0:
            self.rect.x = configs.SCREEN_WIDTH
