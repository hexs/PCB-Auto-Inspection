from typing import Sequence
import pygame as pg
from pygame import Rect, Surface, mouse, MOUSEBUTTONDOWN
from pygame_gui.elements import UIImage
import pygame_gui
from pygame_gui import UIManager, UI_FILE_DIALOG_PATH_PICKED, UI_BUTTON_PRESSED, UI_DROP_DOWN_MENU_CHANGED, \
    UI_SELECTION_LIST_NEW_SELECTION
from pygame_gui.elements import UIWindow, UIPanel, UILabel, UIButton, UIDropDownMenu, UISelectionList, UIImage
from pygame_gui.windows import UIFileDialog


def putText(surface, text, xy, font_size=32, color=(0, 0, 0), bg_color=None, anchor='center', font=None):
    font_ = pg.font.Font(font, font_size)
    text_surface = font_.render(text, True, color, bg_color, wraplength=0)
    text_rect = text_surface.get_rect()
    setattr(text_rect, anchor, xy)
    surface.blit(text_surface, text_rect)



class PG_Text:
    def __init__(self, text='', xy=(0, 0), color=(0, 0, 0), bg_color=None, font=None, anchor='center'):
        self.text = text
        self.xy = xy
        self.font = font = pg.font.SysFont('Arial', 30) if font is None else font
        self.color = color
        self.bg_color = bg_color
        self.anchor = anchor
        self.update_text()

    def update_text(self):
        self.text_surface = self.font.render(self.text, True, self.color, self.bg_color)
        self.text_rect = self.text_surface.get_rect()
        setattr(self.text_rect, self.anchor, self.xy)

    def draw(self, surface):
        surface.blit(self.text_surface, self.text_rect)


class PG_Image:
    def __init__(self, rect: Rect, color=(255, 255, 255), manager=None, container=None):
        self.rect = rect
        self.color = color
        self.manager = manager
        self.container = container
        self.surface = Surface(rect.size)
        self.surface.fill(self.color)
        self.surface_image = UIImage(
            relative_rect=self.rect,
            image_surface=self.surface,
            manager=self.manager,
            container=self.container
        )
        self.texts = {}

    def add_text(self, name, text='', xy=(0, 0), color=(0, 0, 0), bg_color=None, font=None, anchor='center'):
        self.texts[name] = PG_Text(text, xy, color, bg_color, font, anchor)
        self.set_image()

    def update_text(self, name, **kwargs):
        if name not in self.texts.keys():
            self.add_text(name)

        text_obj = self.texts[name]
        for k, v in kwargs.items():
            setattr(text_obj, k, v)
        text_obj.update_text()
        self.set_image()

    def set_image(self):
        self.surface.fill(self.color)
        for text_obj in self.texts.values():
            text_obj.draw(self.surface)
        self.surface_image.set_image(self.surface)


if __name__ == '__main__':
    pg.init()
    window_size = (800, 600)
    window_surface = pg.display.set_mode(window_size)

    ui_manager = pygame_gui.UIManager(window_size)
    panel = pygame_gui.elements.UIPanel(
        relative_rect=pg.Rect((50, 50), (500, 400)),
        manager=ui_manager,
    )

    pg_image = PG_Image(Rect(20, 20, 400, 300), container=panel)
    pg_image.update_text('t1',
                         text='Click to change text!',
                         xy=(200, 150),
                         font=pg.font.SysFont('Arial', 30),
                         anchor='center')
    pg_image.surface_image.set_image(pg_image.surface)

    # Main game loop
    clock = pg.time.Clock()
    is_running = True
    click_count = 0

    while is_running:
        time_delta = clock.tick(60) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                is_running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click_count += 1
                    pg_image.update_text('t1', text=f"Clicked {click_count} times!")
            ui_manager.process_events(event)

        ui_manager.update(time_delta)
        window_surface.fill((255, 255, 255))
        ui_manager.draw_ui(window_surface)
        pg.display.update()
    pg.quit()
