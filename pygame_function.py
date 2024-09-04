import pygame


def putText(surface, text, xy, font_size=32, color=(0, 0, 0), bg_color=None, anchor='center', font=None):
    font_ = pygame.font.Font(font, font_size)
    text_surface = font_.render(text, True, color, bg_color, wraplength=0)
    text_rect = text_surface.get_rect()
    setattr(text_rect, anchor, xy)
    surface.blit(text_surface, text_rect)
