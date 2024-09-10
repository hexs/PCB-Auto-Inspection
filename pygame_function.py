import pygame
import pygame_gui
import warnings


def putText(surface, text, xy, font_size=32, color=(0, 0, 0), bg_color=None, anchor='center', font=None):
    font_ = pygame.font.Font(font, font_size)
    text_surface = font_.render(text, True, color, bg_color, wraplength=0)
    text_rect = text_surface.get_rect()
    setattr(text_rect, anchor, xy)
    surface.blit(text_surface, text_rect)


''' font size upgrade '''

warnings.filterwarnings("ignore", category=UserWarning, module="pygame_gui.core.ui_font_dictionary")
warnings.filterwarnings("ignore", category=UserWarning, module="pygame_gui.core.text.html_parser")


class HTMLParser(pygame_gui.core.text.html_parser.HTMLParser):
    # font_sizes = {
    #     1: 8,
    #     1.5: 9,
    #     2: 10,
    #     2.5: 11,
    #     3: 12,
    #     3.5: 13,
    #     4: 14,
    #     4.5: 16,
    #     5: 18,
    #     5.5: 20,
    #     6: 24,
    #     6.5: 32,
    #     7: 48,
    #     8: 200  # add font data
    # }

    # or

    def _handle_font_tag(self, attributes, style):
        super()._handle_font_tag(attributes, style)
        if 'size' in attributes:
            if attributes['size'] is not None and len(attributes['size']) > 0:
                try:
                    font_size = int(attributes['size'])
                except ValueError or AttributeError:
                    font_size = self.default_style['font_size']
            else:
                font_size = self.default_style['font_size']
            style["font_size"] = font_size


class UITextBox(pygame_gui.elements.UITextBox):
    def _reparse_and_rebuild(self):
        self.parser = HTMLParser(self.ui_theme, self.combined_element_ids,
                                 self.link_style, line_spacing=self.line_spacing,
                                 text_direction=self.font_dict.get_default_font().get_direction())
        self.rebuild()
