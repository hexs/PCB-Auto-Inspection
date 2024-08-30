import pygame


def puttext(surface, text, pos, font_size=32, color=(255, 255, 255), background=None):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color, background)
    text_rect = text_surface.get_rect(topleft=pos)
    surface.blit(text_surface, text_rect)