from typing import Tuple, Dict, Optional
import numpy as np
import pygame
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.core import IContainerLikeInterface

# Constants
DEFAULT_FONT = 'Arial'
DEFAULT_FONT_SIZE = 30
DEFAULT_COLOR = (0, 0, 0)
DEFAULT_BG_COLOR = None
DEFAULT_ANCHOR = 'center'


def gradient_surface(rect: pygame.Rect,
                     start_color: Tuple[int, int, int],
                     end_color: Tuple[int, int, int]) -> pygame.Surface:
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    for x in range(rect.w):
        r = start_color[0] + (end_color[0] - start_color[0]) * (x / rect.w)
        g = start_color[1] + (end_color[1] - start_color[1]) * (x / rect.w)
        b = start_color[2] + (end_color[2] - start_color[2]) * (x / rect.w)
        pygame.draw.line(surface, (r, g, b), (x, 0), (x, rect.h))
    return surface


def rounded_gradient_surface(rect: pygame.Rect,
                             start_color: Tuple[int, int, int],
                             end_color: Tuple[int, int, int],
                             corner_radius: int,
                             edge_thickness: int = 1,
                             edge_color: Tuple[int, int, int] = (0, 0, 0)) -> pygame.Surface:
    surface = gradient_surface(rect, start_color, end_color)
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255), rect, border_radius=corner_radius)
    surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(surface, edge_color, rect, width=edge_thickness, border_radius=corner_radius)
    return surface


class PG_Text:
    def __init__(self, text='', xy=(0, 0),
                 color: Tuple[int, int, int] = DEFAULT_COLOR,
                 bg_color: Optional[Tuple[int, int, int]] = DEFAULT_BG_COLOR,
                 font_name: str = DEFAULT_FONT,
                 font_size: Optional[int] = DEFAULT_FONT_SIZE,
                 font=None,
                 anchor: str = DEFAULT_ANCHOR):
        self.text = text
        self.xy = xy
        self.color = color
        self.bg_color = bg_color
        self.font_name = font_name
        self.font_size = font_size
        self.font = pygame.font.SysFont(font_name, font_size) if font is None else font
        self.anchor = anchor
        self.update_text()

    def update_text(self):
        self.text_surface = self.font.render(self.text, True, self.color, self.bg_color)
        self.text_rect = self.text_surface.get_rect()
        setattr(self.text_rect, self.anchor, self.xy)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.text_surface, self.text_rect)


class TextBoxSurface:
    def __init__(self, rect: pygame.Rect,
                 start_color=(180, 240, 255),
                 end_color=(180, 220, 255),
                 corner_radius=10, edge_thickness=2,
                 edge_color=(130, 170, 255),
                 manager: Optional[UIManager] = None,
                 container: Optional[IContainerLikeInterface] = None,
                 ):
        self.rect = rect
        self.manager = manager
        self.container = container
        self.start_color = start_color
        self.end_color = end_color
        self.corner_radius = corner_radius
        self.edge_thickness = edge_thickness
        self.edge_color = edge_color
        self.texts: Dict[str, PG_Text] = {}

        self.surface = rounded_gradient_surface(
            self.rect.move_to(x=0, y=0),
            start_color,
            end_color,
            corner_radius,
            edge_thickness,
            edge_color
        )

        self.image_element = pygame_gui.elements.UIImage(
            relative_rect=self.rect,
            image_surface=self.surface,
            manager=manager,
            container=container
        )
        self.clear()

    def clear(self):
        self.text_surface = self.surface.copy()

    def add_text(self, name: str, text='',
                 xy: Optional[Tuple[int, int]] = None,
                 color: Tuple[int, int, int] = DEFAULT_COLOR,
                 bg_color: Optional[Tuple[int, int, int]] = DEFAULT_BG_COLOR,
                 font_name: str = DEFAULT_FONT,
                 font_size: Optional[int] = DEFAULT_FONT_SIZE,
                 font: Optional[pygame.font.Font] = None,
                 anchor: str = DEFAULT_ANCHOR):
        xy = np.array(self.rect.size) / 2 if xy is None else xy
        self.texts[name] = PG_Text(text, xy, color, bg_color, font_name, font_size, font, anchor)
        self.set_image()

    def update_text(self, name: str, **kwargs):
        if name not in self.texts:
            self.add_text(name)

        text_obj = self.texts[name]
        for k, v in kwargs.items():
            setattr(text_obj, k, v)
        text_obj.update_text()
        self.set_image()

    def set_image(self):
        self.clear()
        for text_obj in self.texts.values():
            text_obj.draw(self.text_surface)
        self.image_element.set_image(self.text_surface)


def main():
    pygame.init()
    window_size = (800, 600)
    display = pygame.display.set_mode(window_size)
    pygame.display.set_caption('UIImage Example')
    manager = pygame_gui.UIManager(window_size)

    ###  example 1  ###
    textbox1 = TextBoxSurface(pygame.Rect(100, 100, 300, 100), manager=manager)
    textbox1.update_text('Text', text='Hello World')

    ###  example 2  ###
    windows = pygame_gui.elements.UIWindow(pygame.Rect(100, 200, 600, 500), manager=manager)
    textbox2 = TextBoxSurface(pygame.Rect(100, 100, 300, 100), container=windows)
    textbox2.update_text('Text', text='My World')
    ###############

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                textbox1.update_text('Text', text='Hello')

            manager.process_events(event)

        manager.update(time_delta)

        display.fill((255, 255, 255))
        manager.draw_ui(display)

        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
