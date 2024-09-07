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
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIDropDownMenu, UISelectionList
from pygame_gui.windows import UIFileDialog
from keras import models

from constant import *
from adj_image import adj_image
from manage_json_files import json_load, json_update
from theme import theme
from training import crop_img
from TextBoxSurface import TextBoxSurface, gradient_surface
from pygame_function import putText
import os
import urllib.request
from pprint import pprint


class RightClick:
    def __init__(self, app, window_size):
        self.app = app
        self.options_list = set()
        self.selection = None
        self.window_size = np.array(window_size)

    def add_options_list(self, new_options_list):
        self.options_list = self.options_list.union(new_options_list)

    def remove_options_list(self, new_options_list):
        self.options_list = self.options_list - new_options_list

    def create_selection(self, mouse_pos, options_list):
        if len(options_list) > 0:
            selection_size = (200, 6 + 25 * len(options_list))
            pos = np.minimum(mouse_pos, self.window_size - selection_size)
            self.selection = UISelectionList(
                Rect(pos, selection_size),
                item_list=options_list,
                manager=self.app.manager,
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
                    if self.app.scale_and_offset_label.get_abs_rect().collidepoint(mouse.get_pos()):
                        self.create_selection(event.pos, {'save config', 'save mark'})
                    elif self.app.panel1_rect.collidepoint(mouse.get_pos()):
                        self.create_selection(event.pos, {'zoom to fit'})
                    else:
                        self.create_selection(event.pos, self.options_list)


class AutoInspection:

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
                text += f"\n{v['highest_score_name']} {v['highest_score_percent']}"
            putText(self.scaled_img_surface, text, rect.topleft, 16, (0, 0, 255), (255, 255, 255), anchor='bottomleft')

    def __init__(self):
        self.config = json_load('config.json', default={
            'device_note': 'PC, RP',
            'device': 'PC',
            'resolution_note': '1920x1080, 800x480',
            'resolution': '1920x1080',
            'model_name': '-',
            'fullscreen': True,
            'url_image': 'http://192.168.225.137:2000/image?source=video_capture&id=0',
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
        self.manager = UIManager(self.display.get_size(), theme_path=theme)
        self.right_click = RightClick(self, self.window_size.tolist())
        self.setup_ui()
        self.change_model()

        self.pass_n = 0
        self.fail_n = 0

    def reset_frame(self):
        for name, frame in self.frame_dict.items():
            frame['color_rect'] = (255, 220, 0)
            frame['width_rect'] = 2
            frame['highest_score_name'] = ''
            frame['highest_score_percent'] = ''
            if not frame.get('frame_name'):
                frame['frame_name'] = name
        self.res_textbox.update_text('res', text='-', color=(0, 0, 0))
        self.setup_NG_details()

    def setup_NG_details(self):
        size_font = 6 if self.config['resolution'] == '1920x1080' else 4
        formatted_text = ""
        for k, v in self.frame_dict.items():
            if v.get('highest_score_name') in ['', 'OK']:
                continue
            text = f"{k} {v['highest_score_name']} {v['highest_score_percent']}"
            formatted_text += f"<font color='#FF0000' size={size_font}>{text}</font><br>"
        self.text_box.set_text(formatted_text)

    def update_status(self):
        self.setup_NG_details()
        self.passrate_textbox.update_text('Pass', text=f': {self.pass_n}')
        self.passrate_textbox.update_text('Fail', text=f': {self.fail_n}')
        self.passrate_textbox.update_text('Pass rate', text=
        f': {self.pass_n / (self.pass_n + self.fail_n) * 100:.2f}%' if self.pass_n or self.fail_n else ':  -')

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
            self.reset_frame()
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
            self.pass_n = self.fail_n = 0
            self.update_status()

        self.res_textbox.update_text('res', text='-')
        self.setup_NG_details()

    def predict(self):
        self.res_textbox.update_text('res', text='Wait', color=(255, 255, 0))
        self.manager.draw_ui(self.display)
        pg.display.update()

        res_surface_text = 'OK'
        wh_ = np.array(self.np_img.shape[1::-1])
        print(self.model_dict)
        for name, frame in self.frame_dict.items():
            if self.model_dict[frame['model_used']].get('model'):  # มีไฟล์ model.h5
                model = self.model_dict[frame['model_used']]['model']
                model_class_names = self.model_dict[frame['model_used']]['model_class_names']
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

                for k, v in frame['res_show'].items():
                    if highest_score_name in v:
                        highest_score_name = k

                frame['highest_score_name'] = highest_score_name
                frame['highest_score_percent'] = highest_score_percent

                if highest_score_name == 'OK':
                    frame['color_rect'] = (0, 255, 0)
                    frame['width_rect'] = 2
                else:
                    frame['color_rect'] = (255, 0, 0)
                    frame['width_rect'] = 3
                    res_surface_text = 'NG'

        if res_surface_text == 'OK':
            self.pass_n += 1
            self.res_textbox.update_text('res', text='OK', color=(0, 255, 0))
        else:
            self.fail_n += 1
            self.res_textbox.update_text('res', text='NG', color=(255, 0, 0))
        self.update_status()

    def panel0_setup(self):
        is_full_hd = self.config['resolution'] == '1920x1080'
        self.logo_button = UIButton(
            Rect(5, 5, 30, 30) if is_full_hd else Rect(5, 5, 20, 20),
            'DX', self.manager,
            object_id=ObjectID(class_id='@logo_button', object_id='#logo_button'),
        )
        rect = Rect(15, 0, 60, 40) if is_full_hd else Rect(10, 0, 60, 30)
        self.model_label = UILabel(
            rect, f'Model:', self.manager,
            object_id=ObjectID(class_id='@model_label', object_id='#model_label'),
            anchors={
                'top': 'top',
                'left': 'left',
                'bottom': 'top',
                'right': 'left',
                'left_target': self.logo_button}
        )
        os.makedirs('data', exist_ok=True)
        model_data = os.listdir('data') + ['-']
        rect = Rect(10, 5, 300, 30) if is_full_hd else Rect(10, 0, 200, 30)
        self.model_data_dropdown = UIDropDownMenu(model_data, '-', rect, self.manager, anchors={
            'left_target': self.model_label})
        rect = Rect(-50, 0, 50, 40) if is_full_hd else Rect(-40, 0, 40, 30)
        self.close_button = UIButton(
            rect, f'X', self.manager,
            object_id=ObjectID(class_id='@close_button', object_id='#close_button'),
            anchors={
                'top': 'top',
                'left': 'right',
                'bottom': 'top',
                'right': 'right'}
        )
        self.minimize_button = UIButton(
            rect, f'—', self.manager,
            object_id=ObjectID(class_id='@minimize_button', object_id='#minimize_button'),
            anchors={
                'top': 'top',
                'left': 'right',
                'bottom': 'top',
                'right': 'right',
                'right_target': self.close_button}
        )

        rect = Rect(10, -30, 100, 26) if is_full_hd else Rect(10, -24, 100, 26)
        anchors = {
            'top': 'bottom',
            'left': 'left',
            'bottom': 'bottom',
            'right': 'left'
        }
        self.fps_label = UILabel(rect, '', self.manager, anchors=anchors)
        self.mouse_pos_label = UILabel(rect, '', self.manager, anchors=anchors | {'left_target': self.fps_label})
        self.scale_and_offset_label = UILabel(rect, '', self.manager,
                                              anchors=anchors | {'left_target': self.mouse_pos_label})
        self.autoinspection_button = UIButton(
            Rect(-150, -30, 150, 30), f'Auto Inspection 0.2.1', self.manager,
            object_id=ObjectID(class_id='@auto_inspection', object_id='#auto_inspection_button'),
            anchors={
                'top': 'bottom',
                'left': 'right',
                'bottom': 'bottom',
                'right': 'right'}
        )

    def panel0_update(self, events):
        is_full_hd = self.config['resolution'] == '1920x1080'
        if is_full_hd:
            self.display.blit(gradient_surface(Rect(0, 0, 720, 40), (150, 200, 255), (255, 250, 230)), (0, 0))
            self.display.blit(gradient_surface(Rect(0, 0, 1200, 40), (255, 250, 230), (211, 229, 250)), (720, 0))

        for event in events:
            if event.type == UI_BUTTON_PRESSED:
                if event.type == pg.QUIT:
                    self.is_running = False
                if event.ui_element == self.close_button:
                    self.is_running = False
                if event.ui_element == self.minimize_button:
                    pg.display.iconify()
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

                    if event.text == 'zoom to fit':
                        data = json_load(os.path.join('data', self.model_name, 'model_config.json'), {
                            f"{self.config['resolution']}": {
                                "scale_factor": 1,
                                "img_offset": [0, 0]
                            }
                        })
                        self.scale_factor = data[self.config['resolution']]['scale_factor']
                        self.img_offset = np.array(data[self.config['resolution']]['img_offset'])

        t = f'{pg.mouse.get_pos()}'
        t += ' 1' if self.panel1_rect.collidepoint(pg.mouse.get_pos()) else ''
        t += ' 2' if self.panel2_rect.collidepoint(pg.mouse.get_pos()) else ''
        self.fps_label.set_text(f'fps: {round(self.clock.get_fps())}')
        self.mouse_pos_label.set_text(t)
        self.scale_and_offset_label.set_text(f'{round(self.scale_factor, 2)} {self.img_offset.astype(int)}')

    def panel1_setup(self):
        is_full_hd = self.config['resolution'] == '1920x1080'
        self.panel1_rect = Rect(0, 40, 1347, 1010) if is_full_hd else Rect(0, 30, 600, 430)
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
        is_full_hd = self.config['resolution'] == '1920x1080'
        self.panel2_up_rect = Rect(1347, 40, 573, 90) if is_full_hd else Rect(600, 30, 200, 30)
        self.panel2_up = UIPanel(self.panel2_up_rect, manager=self.manager)

        self.panel2_rect = Rect(1347, 127, 573, 923) if is_full_hd else Rect(600, 30, 200, 430)
        self.panel2 = UIPanel(self.panel2_rect, manager=self.manager)

        if is_full_hd:
            self.capture_button = UIButton(Rect(10, 10, 100, 50), 'Capture', container=self.panel2_up, )
            self.auto_cap_button = UIButton(Rect(10, 0, 100, 20), 'Auto', container=self.panel2_up, anchors={
                'top_target': self.capture_button
            })
            self.load_button = UIButton(Rect(10, 10, 100, 70), 'Load Image', container=self.panel2_up, anchors={
                'left_target': self.capture_button
            })
            self.adj_button = UIButton(Rect(10, 10, 100, 70), 'Adj Image', container=self.panel2_up, anchors={
                'left_target': self.load_button
            })
            self.predict_button = UIButton(Rect(10, 10, 100, 70), 'Predict', container=self.panel2_up, anchors={
                'left_target': self.adj_button
            })
        else:
            self.capture_button = UIButton(Rect(350, 0, 60, 30), 'Capture', manager=self.manager, )
            self.auto_cap_button = UIButton(Rect(0, 0, 40, 30), 'Auto', manager=self.manager, anchors={
                'left_target': self.capture_button
            })
            self.load_button = UIButton(Rect(10, 0, 100, 30), 'Load Image', manager=self.manager, anchors={
                'left_target': self.auto_cap_button
            })
            self.adj_button = UIButton(Rect(10, 0, 70, 30), 'Adj Image', manager=self.manager, anchors={
                'left_target': self.load_button
            })
            self.predict_button = UIButton(Rect(0, 0, 70, 30), 'Predict', manager=self.manager, anchors={
                'left_target': self.adj_button,
            })
        self.file_dialog = None
        self.adj_button.disable()
        self.predict_button.disable()

        self.res_textbox = TextBoxSurface(
            Rect((self.panel2_rect.w - 300) / 2, 12, 300, 150) if is_full_hd \
                else Rect((self.panel2_rect.w - 150) / 2, 5, 150, 80),
            (230, 230, 200), (230, 230, 255),
            container=self.panel2,
        )
        self.res_textbox.add_text(
            'res', text='-', color=(0, 0, 0),
            font=pg.font.Font('font/M_PLUS_Rounded_1c/MPLUSRounded1c-Medium.ttf', 130 if is_full_hd else 50)
        )

        self.passrate_textbox = TextBoxSurface(
            Rect((self.panel2_rect.w - 550) / 2, 170, 550, 180) if is_full_hd \
                else Rect((self.panel2_rect.w - 190) / 2, 90, 190, 90),
            (230, 230, 255), (230, 230, 200),
            container=self.panel2
        )

        self.passrate_textbox.add_text(
            'Pass_', 'Pass',
            (50, 10) if is_full_hd else (10, 0),
            (0, 255, 0),
            font=pg.font.Font('font/M_PLUS_Rounded_1c/MPLUSRounded1c-Medium.ttf', 40 if is_full_hd else 20),
            anchor='topleft'
        )
        self.passrate_textbox.add_text(
            'Pass', text=': 0',
            xy=(300, 10) if is_full_hd else (100, 0),
            color=(0, 255, 0),
            font=pg.font.Font('font/M_PLUS_Rounded_1c/MPLUSRounded1c-Medium.ttf', 40 if is_full_hd else 20),
            anchor='topleft'
        )
        self.passrate_textbox.add_text(
            'Fail_', text='Fail',
            xy=(50, 60) if self.config['resolution'] == '1920x1080' else (10, 30),
            color=(255, 0, 0),
            font=pg.font.Font('font/M_PLUS_Rounded_1c/MPLUSRounded1c-Medium.ttf', 40 if is_full_hd else 20),
            anchor='topleft'
        )
        self.passrate_textbox.add_text(
            'Fail', text=': 0',
            xy=(300, 60) if is_full_hd else (100, 30),
            color=(255, 0, 0),
            font=pg.font.Font('font/M_PLUS_Rounded_1c/MPLUSRounded1c-Medium.ttf', 40 if is_full_hd else 20),
            anchor='topleft'
        )
        self.passrate_textbox.add_text(
            'Pass rate_', text='Pass rate',
            xy=(50, 110) if is_full_hd else (10, 60),
            color=(0, 0, 0),
            font=pg.font.Font('font/M_PLUS_Rounded_1c/MPLUSRounded1c-Medium.ttf', 40 if is_full_hd else 20),
            anchor='topleft'
        )
        self.passrate_textbox.add_text(
            'Pass rate', text=': -%',
            xy=(300, 110) if is_full_hd else (100, 60),
            color=(0, 0, 0),
            font=pg.font.Font('font/M_PLUS_Rounded_1c/MPLUSRounded1c-Medium.ttf', 40 if is_full_hd else 20, ),
            anchor='topleft'
        )

        # Create a UITextBox inside the panel
        self.text_box = pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=Rect(((self.panel2_rect.w - 550) / 2, 357), (550, 555)) if is_full_hd \
                else Rect((self.panel2_rect.w - 190) / 2, 180, 190, 240),
            container=self.panel2
        )

    def panel2_update(self, events):
        is_full_hd = self.config['resolution'] == '1920x1080'
        # self.panel2_surface.fill((100, 100, 100))
        for event in events:
            if event.type == UI_BUTTON_PRESSED:
                if event.ui_element == self.capture_button:
                    self.auto_cap_button.set_text('Auto')
                    self.get_surface_form_url(self.config['url_image'])
                    self.reset_frame()
                if event.ui_element == self.auto_cap_button:
                    self.auto_cap_button.set_text('Auto' if self.auto_cap_button.text == 'Stop' else 'Stop')
                if event.ui_element == self.load_button:
                    self.auto_cap_button.set_text('Auto')

                    self.file_dialog = UIFileDialog(
                        Rect(1360, 130, 440, 500) if is_full_hd else Rect(200, 50, 400, 400),
                        self.manager, 'Load Image...', {".png", ".jpg"},
                        'data' if self.model_name == '-' else os.path.join('data', self.model_name),
                        allow_picking_directories=True,
                        allow_existing_files_only=True,
                    )
                if event.ui_element == self.adj_button:
                    print(self.mark_dict)
                    self.np_img = adj_image(self.np_img, self.model_name, self.mark_dict)
                    self.reset_frame()
                if event.ui_element == self.predict_button:
                    self.predict()
            if event.type == UI_FILE_DIALOG_PATH_PICKED:
                if '.png' in event.text:
                    print(event.text)
                    self.np_img = cv2.imread(event.text)
                    self.reset_frame()

        if self.auto_cap_button.text == 'Stop':
            self.get_surface_form_url(self.config['url_image'])

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

            self.manager.update(time_delta)
            self.manager.draw_ui(self.display)

            pg.display.update()


def main():
    app = AutoInspection()
    app.run()


if __name__ == "__main__":
    main()
