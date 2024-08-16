import json
import os
import urllib.request
from pprint import pprint
import numpy as np
import cv2
import pygame as pg
from pygame import Rect, Surface, mouse, MOUSEBUTTONDOWN
import pygame_gui
from pygame_gui import UIManager, UI_FILE_DIALOG_PATH_PICKED, UI_BUTTON_PRESSED, UI_DROP_DOWN_MENU_CHANGED, \
    UI_SELECTION_LIST_NEW_SELECTION
from pygame_gui.elements import UIWindow, UIPanel, UILabel, UIButton, UIDropDownMenu, UISelectionList
from pygame_gui.windows import UIFileDialog
from adj_image import adj_image
from manage_json_files import json_load, json_dump, json_update
from keras import models
from constant import *
from training import crop_img


class RightClick:
    def __init__(self, app, window_size):
        self.options_list = {'1', }
        self.selection = None
        self.window_size = np.array(window_size)

    def add_options_list(self, new_options_list):
        self.options_list = self.options_list.union(new_options_list)

    def remove_options_list(self, new_options_list):
        self.options_list = self.options_list - new_options_list

    def create_selection(self, mouse_pos, options_list):
        selection_size = (200, 6 + 20 * len(self.options_list))
        pos = np.minimum(mouse_pos, self.window_size - selection_size)
        self.selection = UISelectionList(
            Rect(pos, selection_size),
            item_list=options_list,
            manager=app.manager,
        )

    def kill(self):
        if self.selection:
            self.selection.kill()
            self.selection = None

    def events(self, events):
        for event in events:
            if event.type == UI_SELECTION_LIST_NEW_SELECTION:
                print(f"RightClick: {event.text}")
                self.kill()

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if self.selection and not self.selection.get_relative_rect().collidepoint(event.pos):
                        self.kill()
                elif event.button == 3:  # Right mouse button
                    self.kill()
                    if len(self.options_list) > 0:
                        if app.scale_and_offset_label.get_abs_rect().collidepoint(mouse.get_pos()):
                            self.create_selection(event.pos, {'save config', 'save mark'})
                        else:
                            self.create_selection(event.pos, self.options_list)


class AutoInspection:
    def setup_theme(self):
        self.theme = {
            '#close_button': {
                "colours": {
                    "hovered_bg": "rgb(232,17,35)",
                }
            },
            '@panel_window.#title_bar': {
                "colours": {
                    "normal_bg": "rgb(229,243,255)",
                }
            },
            "button": {
                "colours": {
                    "normal_bg": "#F3F3F3",
                    "hovered_bg": "rgb(229,243,255)",
                    "disabled_bg": "#F3F3F3",
                    "selected_bg": "rgb(204,232,255)",
                    "active_bg": "rgb(204,232,255)",
                    "normal_text": "#000",
                    "hovered_text": "#000",
                    "selected_text": "#000",
                    "disabled_text": "#A6A6A6",
                    "active_text": "#000",
                    "normal_border": "#CCCCCC",
                    "hovered_border": "#A6A6A6",
                    "disabled_border": "#CCCCCC",
                    "selected_border": "#A6A6A6",
                    "active_border": "#0078D7",
                    "normal_text_shadow": "#00000000",
                    "hovered_text_shadow": "#00000000",
                    "disabled_text_shadow": "#00000000",
                    "selected_text_shadow": "#00000000",
                    "active_text_shadow": "#00000000"
                },
                "misc": {
                    "shape": "rounded_rectangle",
                    "shape_corner_radius": "4",
                    "border_width": "1",
                    "shadow_width": "0",
                    "tool_tip_delay": "1.0",
                    "text_horiz_alignment": "center",
                    "text_vert_alignment": "center",
                    "text_horiz_alignment_padding": "10",
                    "text_vert_alignment_padding": "5",
                    "text_shadow_size": "0",
                    "text_shadow_offset": "0,0",
                    "state_transitions": {
                        "normal_hovered": "0.2",
                        "hovered_normal": "0.2"
                    }
                }
            },
            "label": {
                "colours": {
                    "normal_text": "#000",
                },
                "misc": {
                    "text_horiz_alignment": "left"
                }
            },
            "window": {
                "colours": {
                    "dark_bg": "#F9F9F9",
                    "normal_border": "#888"
                },

                "misc": {
                    "shape": "rounded_rectangle",
                    #         "shape_corner_radius": "10",
                    #         "border_width": "1",
                    #         "shadow_width": "15",
                    #         "title_bar_height": "20"
                }
            },
            "panel": {
                "colours": {
                    "dark_bg": "#F9F9F9",
                    "normal_border": "#888"
                },
            },
            "selection_list": {
                "colours": {
                    "dark_bg": "#F9F9F9",
                    "normal_border": "#999999"
                },
            },
            "text_entry_line": {
                "colours": {
                    "dark_bg": "#fff",
                    "normal_text": "#000",
                    "text_cursor": "#000"
                },
            },

            "horizontal_slider": {
                "prototype": "#test_prototype_colours",

                "colours": {
                    "dark_bg": "rgb(240,240,240)"
                },
                "misc": {
                    "shape": "rounded_rectangle",
                    "shape_corner_radius": "10",
                    "shadow_width": "2",
                    "border_width": "1",
                    "enable_arrow_buttons": "1"
                }
            },
            "horizontal_slider.@arrow_button": {
                "misc": {
                    "shape": "rounded_rectangle",
                    "shape_corner_radius": "8",
                    "text_horiz_alignment_padding": "2"
                }
            },
            "horizontal_slider.#sliding_button": {
                "colours": {
                    "normal_bg": "#F55",
                    "hovered_bg": "#F00",
                },
                "misc": {
                    "shape": "ellipse",
                }
            }
        }
        self.theme.update({
            "drop_down_menu": {
                "misc": {
                    "shape": "rounded_rectangle",
                    "shape_corner_radius": "4",
                    "open_button_width": "0"
                },
            }
        })
        self.theme['@delete_button'] = self.theme['#close_button']
        return self.theme

    def update_scaled_img_surface(self):
        self.scaled_img_surface = pg.transform.scale(self.img_surface, (
            int(self.img_surface.get_width() * self.scale_factor),
            int(self.img_surface.get_height() * self.scale_factor)))
        self.img_size_vector = np.array(self.scaled_img_surface.get_size())

    def get_surface_form_np(self, np_img):
        self.img_surface = pg.image.frombuffer(np_img.tobytes(), np_img.shape[1::-1], "BGR")
        self.update_scaled_img_surface()

    def get_surface_form_url(self, url):
        try:
            req = urllib.request.urlopen(url)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            self.np_img = cv2.imdecode(arr, -1)
        except Exception as e:
            print(f"Error loading image: {e}")
            self.np_img = np.full((500, 500, 3), [0, 0, 230], dtype=np.uint8)  # Red image on error
        self.get_surface_form_np(self.np_img)

    def put_text(self, surface, text, font, xy, color, color2=(255, 255, 255), anchor='center'):
        text_surface = font.render(text, True, color, color2)
        text_rect = text_surface.get_rect()
        setattr(text_rect, anchor, xy)
        surface.blit(text_surface, text_rect)

    def show_rects_to_surface(self, frame_dict):
        for k, v in frame_dict.items():
            xywh = np.array(v.get('xywh'))
            xy = xywh[:2]
            wh = xywh[2:]
            x1y1 = xy - wh / 2
            x1y1_ = x1y1 * self.img_size_vector
            wh_ = wh * self.img_size_vector
            rect = Rect(x1y1_, wh_)

            # pg.draw.line(self.scaled_img_surface, (255, 255, 0), rect.midtop, rect.midbottom)
            # pg.draw.line(self.scaled_img_surface, (255, 255, 0), rect.midleft, rect.midright)
            pg.draw.rect(self.scaled_img_surface, v['color_rect'],
                         rect.inflate(v['width_rect'] * 2 + 1, v['width_rect'] * 2 + 1), v['width_rect'])

            # pg.draw.rect(self.scaled_img_surface, (200, 255, 0), rect, 1)
            pg.draw.line(self.scaled_img_surface, (0, 0, 100), rect.topleft, rect.topright)
            pg.draw.line(self.scaled_img_surface, (0, 0, 100), rect.bottomleft, rect.bottomright)
            pg.draw.line(self.scaled_img_surface, (0, 0, 100), rect.topleft, rect.bottomleft)
            pg.draw.line(self.scaled_img_surface, (0, 0, 100), rect.topright, rect.bottomright)

            if v.get('k'):
                wh = wh * v['k']
                x1y1 = xy - wh / 2
                x1y1_ = x1y1 * self.img_size_vector
                wh_ = wh * self.img_size_vector
                rect = Rect(x1y1_, wh_)

                pg.draw.rect(self.scaled_img_surface, (200, 255, 0), rect, 1)

        font = pg.font.Font(None, 16)
        for k, v in frame_dict.items():
            xywh = np.array(v.get('xywh'))
            xy = xywh[:2]
            wh = xywh[2:]
            x1y1 = xy - wh / 2
            x1y1_ = x1y1 * self.img_size_vector
            wh_ = wh * self.img_size_vector
            rect = Rect(x1y1_, wh_)

            text = f"{k}"
            if v.get('highest_score_name'):
                text += f" {v['highest_score_name']} {v['highest_score_percent']}"
            self.put_text(self.scaled_img_surface, text, font, rect.topleft, (0, 0, 255), anchor='bottomleft')

    def __init__(self):
        self.config = json_load('config.json', default={
            'device_note': 'PC, RP',
            'device': 'PC',
            'resolution_note': '1920x1080, 800x480',
            'resolution': '1920x1080',
            'model_name': '-',
            'fullscreen': True,
        })
        json_update('config.json', self.config)
        if self.config['resolution'] == '1920x1080':
            self.window_size = np.array([1920, 1080])
        else:
            self.window_size = np.array([800, 480])
        self.model_name = self.config['model_name']

        self.is_running = True
        self.np_img = np.full((2448, 3264, 3), [10, 100, 10], dtype=np.uint8)

        pg.init()
        pg.display.set_caption('Auto Inspection')
        self.clock = pg.time.Clock()

        self.display = pg.display.set_mode(self.window_size.tolist(), pg.FULLSCREEN if self.config['fullscreen'] else 0)
        self.manager = UIManager(self.display.get_size(), theme_path=self.setup_theme())
        self.right_click = RightClick(self, self.window_size.tolist())
        self.setup_ui()
        self.change_model()

    def change_model(self):
        if self.model_name == '-':
            self.adj_button.disable()
            self.predict_button.disable()
            self.frame_dict = {}
            self.model_dict = {}
            self.mark_dict = {}
        else:
            self.adj_button.enable()
            self.predict_button.enable()
            json_data = json_load(os.path.join('data', self.model_name, 'frames pos.json'))
            self.frame_dict = json_data['frames']
            self.model_dict = json_data['models']
            self.mark_dict = json_data['marks']
            for name, frame in self.frame_dict.items():
                frame['color_rect'] = (255, 220, 0)
                frame['width_rect'] = 2
                frame['highest_score_name'] = ''
                frame['highest_score_percent'] = ''
                if not frame.get('frame_name'):
                    frame['frame_name'] = name
            for name, frame in self.mark_dict.items():
                frame['color_rect'] = (200, 20, 100)
                frame['width_rect'] = 1
                frame['xy'] = np.array(frame['xywh'][:2])
                frame['wh'] = np.array(frame['xywh'][2:])
                frame['xywh_around'] = np.concatenate((frame['xy'], frame['wh'] * frame['k']))
            for name, model in self.model_dict.items():
                try:
                    model['model'] = models.load_model(fr'data/{self.model_name}/model/{name}.h5')
                except Exception as e:
                    print(f'{YELLOW}Error load model.h5.\n'
                          f'file error data/{self.model_name}/model/{name}.h5{ENDC}')
                    print(PINK, e, ENDC, sep='')
                # try:
                model.update(json_load(fr'data/{self.model_name}/model/{name}.json'))
                pprint(model)
                if model['model_class_names'] != model['class_names']:
                    print(f'{YELLOW}class_names       = {model['class_names']}')
                    print(f'model_class_names = {model['model_class_names']}{ENDC}')
                # except Exception as e:
                #     print(f'{YELLOW}function "load_model" error.\n'
                #           f'file error data/{self.model_name}/model/{name}.json{ENDC}')
                #     print(PINK, e, ENDC, sep='')

            config = json_load(os.path.join('data', self.model_name, 'model_config.json'))
            if config.get(self.config['resolution']):
                for k, v in config[self.config['resolution']].items():
                    if k == 'scale_factor':
                        self.scale_factor = v
                    elif k == 'img_offset':
                        self.img_offset = np.array(v)

    def predict(self):
        wh_ = np.array(self.np_img.shape[1::-1])
        print(self.model_dict)
        for name, frame in self.frame_dict.items():
            if self.model_dict[frame['model_used']].get('model'):  # มีไฟล์ model.h5
                model = self.model_dict[frame['model_used']]['model']
                model_class_names = self.model_dict[frame['model_used']]['model_class_names']
                print(model)
                xywh = frame['xywh']
                img_crop = crop_img(self.np_img, xywh)
                img_crop = cv2.cvtColor(img_crop, cv2.COLOR_BGR2RGB)
                img_array = img_crop[np.newaxis, :]
                predictions = model.predict_on_batch(img_array)

                predictions_score_list = predictions[0]  # [ -6.520611   8.118368 -21.86103   22.21528 ]
                exp_x = [1.2 ** x for x in predictions_score_list]
                percent_score_list = [round(x * 100 / sum(exp_x)) for x in exp_x]
                highest_score_number = np.argmax(predictions_score_list)  # 3

                highest_score_name = model_class_names[highest_score_number]
                highest_score_percent = percent_score_list[highest_score_number]

                frame['highest_score_name'] = highest_score_name
                frame['highest_score_percent'] = highest_score_percent

                if highest_score_name == 'ok':
                    frame['color_rect'] = (0, 255, 0)
                    frame['width_rect'] = 2
                else:
                    frame['color_rect'] = (255, 0, 0)
                    frame['width_rect'] = 3

    def panel0_setup(self):
        rect = Rect(10, 10, 50, 26) if self.config['resolution'] == '1920x1080' else Rect(10, 5, 50, 26)
        model_label = UILabel(rect, f'model:', self.manager)
        os.makedirs('data', exist_ok=True)
        model_data = os.listdir('data') + ['-']
        rect = Rect(10, 5, 300, 30) if self.config['resolution'] == '1920x1080' else Rect(10, 0, 300, 30)
        self.model_data_dropdown = UIDropDownMenu(model_data, '-', rect, self.manager, anchors={
            'left_target': model_label})
        rect = Rect(-50, 0, 50, 40) if self.config['resolution'] == '1920x1080' else Rect(-40, 0, 40, 30)
        self.close_button = UIButton(rect, f'X', self.manager, anchors={
            'top': 'top',
            'left': 'right',
            'bottom': 'top',
            'right': 'right'})
        rect = Rect(10, -30, 50, 26) if self.config['resolution'] == '1920x1080' else Rect(10, -24, 50, 26)
        self.fps_label = UILabel(rect, '', self.manager, anchors={
            'top': 'bottom',
            'left': 'left',
            'bottom': 'bottom',
            'right': 'left'
        })
        rect = Rect(10, -30, 170, 26) if self.config['resolution'] == '1920x1080' else Rect(10, -24, 170, 26)
        self.mouse_pos_label = UILabel(rect, '', self.manager, anchors={
            'top': 'bottom',
            'left': 'left',
            'bottom': 'bottom',
            'right': 'left',
            'left_target': self.fps_label
        })
        rect = Rect(10, -30, 150, 26) if self.config['resolution'] == '1920x1080' else Rect(10, -24, 150, 26)
        self.scale_and_offset_label = UILabel(rect, '', self.manager, anchors={
            'top': 'bottom',
            'left': 'left',
            'bottom': 'bottom',
            'right': 'left',
            'left_target': self.mouse_pos_label
        })

    def panel0_update(self, events):
        for event in events:
            if event.type == UI_BUTTON_PRESSED:
                if event.type == pg.QUIT:
                    self.is_running = False
                if event.ui_element == self.close_button:
                    self.is_running = False
            if event.type == UI_DROP_DOWN_MENU_CHANGED:
                self.model_name = self.model_data_dropdown.selected_option[0]
                self.change_model()

            if event.type == UI_SELECTION_LIST_NEW_SELECTION:  # right click and select click
                if self.model_name != '-':
                    if event.text == 'save config':
                        json_update(os.path.join('data', self.model_name, 'model_config.json'), {
                            f"{self.config['resolution']}": {
                                "scale_factor": self.scale_factor,
                                "img_offset": self.img_offset.tolist()
                            }
                        })
                    if event.text == 'save mark':
                        for name, mark in self.mark_dict.items():
                            xywh = mark['xywh']
                            img = crop_img(self.np_img, xywh)
                            cv2.imwrite(os.path.join('data', self.model_name, f'{name}.png'), img)

        t = f'pos: {pg.mouse.get_pos()} '
        t += 'panel1' if self.panel1_rect.collidepoint(pg.mouse.get_pos()) else ''
        t += 'panel2' if self.panel2_rect.collidepoint(pg.mouse.get_pos()) else ''
        self.fps_label.set_text(f'fps: {round(self.clock.get_fps())}')
        self.mouse_pos_label.set_text(t)
        self.scale_and_offset_label.set_text(f'{round(self.scale_factor, 2)} {self.img_offset.astype(int)}')

    def panel1_setup(self):
        self.panel1_rect = Rect(0, 40, 1347, 1010) \
            if self.config['resolution'] == '1920x1080' \
            else Rect(0, 30, 600, 430)
        self.panel1_surface = Surface(self.panel1_rect.size)

        self.scale_factor = 1
        self.img_offset = np.array([0, 0])

        self.moving = False

    def panel1_update(self, events):
        self.panel1_surface.fill((200, 200, 200))
        if self.panel1_rect.collidepoint(mouse.get_pos()):
            self.canter_img_pos = np.array(self.panel1_rect.size) / 2 + self.img_offset
            self.left_img_pos = self.canter_img_pos - self.img_size_vector / 2
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 2:
                    if self.panel1_rect.collidepoint(mouse.get_pos()):
                        self.moving = True

            if event.type == pg.MOUSEWHEEL:
                if self.panel1_rect.collidepoint(mouse.get_pos()):
                    factor = (1 + event.y / 10)

                    self.scale_factor *= factor
                    a = self.img_size_vector
                    a1 = mouse.get_pos() - self.left_img_pos
                    b = a * factor
                    b1 = a1 * factor
                    canter_img_pos_b = mouse.get_pos() - b1 + b / 2
                    offset = self.canter_img_pos - canter_img_pos_b
                    self.img_offset = self.img_offset - offset

                    # update img_size_vector
                    self.scaled_img_surface = pg.transform.scale(self.img_surface, (
                        int(self.img_surface.get_width() * self.scale_factor),
                        int(self.img_surface.get_height() * self.scale_factor)
                    ))
                    self.img_size_vector = np.array(self.scaled_img_surface.get_size())

            # moving
            if self.moving:
                if event.type == pg.MOUSEMOTION:  # move mouse
                    if event.buttons[1]:
                        self.img_offset += np.array(event.rel)
                if event.type == pg.MOUSEBUTTONUP and event.button == 2:
                    self.moving = False

        self.show_rects_to_surface(self.mark_dict)
        self.show_rects_to_surface(self.frame_dict)
        self.panel1_surface.blit(self.scaled_img_surface,
                                 ((self.panel1_rect.size - self.img_size_vector) / 2 + self.img_offset).tolist())

    def panel2_setup(self):
        self.panel2_rect = Rect(1347, 40, 1920 - 1347, 1010) \
            if self.config['resolution'] == '1920x1080' \
            else Rect(600, 30, 200, 430)
        self.panel2_surface = Surface(self.panel2_rect.size)

        if self.config['resolution'] == '1920x1080':
            self.capture_button = UIButton(Rect(1357, 50, 100, 50), 'Capture', self.manager, )
            self.auto_cap_button = UIButton(Rect(1357, 0, 100, 20), 'AutoCapture', self.manager, anchors={
                'top_target': self.capture_button
            })
            self.load_button = UIButton(Rect(10, 50, 100, 70), 'Load Image', self.manager, anchors={
                'left_target': self.capture_button
            })
            self.adj_button = UIButton(Rect(10, 50, 100, 70), 'Adj Image', self.manager, anchors={
                'left_target': self.load_button
            })
            self.predict_button = UIButton(Rect(10, 50, 100, 70), 'Predict', self.manager, anchors={
                'left_target': self.adj_button
            })
        else:
            self.capture_button = UIButton(Rect(605, 35, 60, 50), 'Capture', self.manager, )
            self.auto_cap_button = UIButton(Rect(605, 0, 60, 20), 'Auto', self.manager, anchors={
                'top_target': self.capture_button
            })
            self.load_button = UIButton(Rect(5, 35, 60, 70), 'Load Image', self.manager, anchors={
                'left_target': self.capture_button
            })
            self.adj_button = UIButton(Rect(5, 35, 60, 35), 'Adj Image', self.manager, anchors={
                'left_target': self.load_button
            })
            self.predict_button = UIButton(Rect(5, 0, 60, 35), 'Predict', self.manager, anchors={
                'left_target': self.load_button, 'top_target': self.adj_button
            })
        self.file_dialog = None
        self.adj_button.disable()
        self.predict_button.disable()

    def panel2_update(self, events):
        self.panel2_surface.fill((100, 100, 100))
        for event in events:
            if event.type == UI_BUTTON_PRESSED:
                if event.ui_element == self.capture_button:
                    self.auto_cap_button.set_text('AutoCapture')
                    self.get_surface_form_url('http://192.168.225.137:2000/image?source=video_capture&id=0')
                if event.ui_element == self.auto_cap_button:
                    self.auto_cap_button.set_text('AutoCapture' if self.auto_cap_button.text == 'Stop' else 'Stop')
                if event.ui_element == self.load_button:
                    self.auto_cap_button.set_text('AutoCapture')
                    rect = Rect(1360, 130, 440, 500) \
                        if self.config['resolution'] == '1920x1080' \
                        else Rect(200, 50, 400, 400)

                    if self.model_name == '-':
                        initial_file_path = 'data'
                    else:
                        initial_file_path = os.path.join('data', self.model_name)

                    self.file_dialog = UIFileDialog(rect, self.manager, 'Load Image...',
                                                    initial_file_path=initial_file_path,
                                                    allow_picking_directories=True,
                                                    allow_existing_files_only=True,
                                                    allowed_suffixes={".png", ".jpg"})
                if event.ui_element == self.adj_button:
                    print(self.mark_dict)
                    self.np_img = adj_image(self.np_img, self.model_name, self.mark_dict)
                if event.ui_element == self.predict_button:
                    self.predict()
            if event.type == UI_FILE_DIALOG_PATH_PICKED:
                if '.png' in event.text:
                    print(event.text)
                    self.np_img = cv2.imread(event.text)

        if self.auto_cap_button.text == 'Stop':
            self.get_surface_form_url('http://192.168.225.137:2000/image?source=video_capture&id=0')

    def setup_ui(self):
        self.panel0_setup()
        self.panel1_setup()
        self.panel2_setup()

    def handle_events(self):
        events = pg.event.get()
        self.panel0_update(events)
        self.panel1_update(events)
        self.panel2_update(events)
        for event in events:
            self.manager.process_events(event)
            if event.type != 1024:
                print(event)
            if event.type == 32870:
                self.manager.set_active_cursor(pg.SYSTEM_CURSOR_HAND)
            if event.type == 32871:
                self.manager.set_active_cursor(pg.SYSTEM_CURSOR_ARROW)

        self.right_click.events(events)

    def run(self):
        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0
            self.display.fill((220, 220, 220))
            self.get_surface_form_np(self.np_img)

            self.handle_events()

            self.display.blit(self.panel1_surface, self.panel1_rect.topleft)
            self.display.blit(self.panel2_surface, self.panel2_rect.topleft)

            self.manager.update(time_delta)
            self.manager.draw_ui(self.display)

            pg.display.update()


if __name__ == "__main__":
    app = AutoInspection()
    app.run()
