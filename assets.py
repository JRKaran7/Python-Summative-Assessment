import os
import pygame

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