import os
import time
import urllib.request
from datetime import datetime
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

from auto_inspection import AutoInspection
from control_robot_window import Control_Robot_Window


class AutoInspectionxRobot(AutoInspection):
    def __init__(self):
        super().__init__()
        self.robot_window = None

    def panel0_setup(self):
        super().panel0_setup()
        is_full_hd = self.config['resolution'] == '1920x1080'
        self.autoinspection_button.kill()
        # bottom left
        anchors = {'top': 'bottom', 'left': 'right', 'bottom': 'bottom', 'right': 'right'}
        self.autoinspection_button = UIButton(
            Rect(-220, -30, 220, 30) if is_full_hd else Rect(-220, -20, 220, 20),
            f'Auto Inspection 0.2.2 x Robot', self.manager,
            object_id=ObjectID(class_id='@auto_inspection_button', object_id='#buttom_bar'),
            anchors=anchors
        )

    def panel0_update(self, events, command_queue):
        super().panel0_update(events)

        for event in events:
            if event.type == UI_BUTTON_PRESSED:
                if event.ui_element == self.autoinspection_button:
                    self.robot_window = Control_Robot_Window(None, self.manager, command_queue)

    def panel2_update(self, events, command_queue, data):
        def get_image():
            url = 'http://192.168.225.137:2000/image?source=video_capture&id=0'
            req = urllib.request.urlopen(url)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            img = cv2.imdecode(arr, -1)
            return img
            cv2.imwrite('Image from URL', img)

        def capture_button():
            command_queue.put(('move_to', 1))
            time.sleep(3)
            image1 = get_image()

            command_queue.put(('move_to', 2))
            time.sleep(2)
            image2 = get_image()

            command_queue.put(('move_to', 3))
            time.sleep(2)
            image3 = get_image()

            command_queue.put(('move_to', 4))
            time.sleep(2)
            image4 = get_image()

            command_queue.put(('move_to', 5))
            time.sleep(2)
            image5 = get_image()

            command_queue.put(('home',))

            wh = image1.shape[1::-1]

            def y(p):
                return int(wh[1] * p)

            def x(p):
                return int(wh[0] * p)

            image = np.concatenate((
                image1[0:y(1), x(.2):x(.7)],
                image2[0:y(1), x(.4):x(.6)],
                image3[0:y(1), x(.2):x(.8)],
                image4[0:y(1), x(.0):x(.3)],
                image4[0:y(1), x(.7):x(1.)],
                # image5[0:y(1), x(.4):x(.6)],
            ), axis=1)

            wh = image.shape[1::-1]
            print(wh)
            print(image5.shape)
            image = np.concatenate((
                np.zeros([500, wh[0], 3], np.uint8),
                image
            ), axis=0)
            image[0:500, 1000:3048] = image5[500:500+500, :]
            # image5[y(.4):y(.6),:]

            cv2.imwrite('image.png', image)

            self.np_img = image.copy()
            self.get_surface_form_np(self.np_img)
            self.reset_frame()
            self.set_name_for_debug()

        is_full_hd = self.config['resolution'] == '1920x1080'

        for event in data.get('events_from_web') or []:
            if event == 'Capture':
                capture_button()

            if event == 'Predict':
                self.predict()
        data['events_from_web'] = []

        for event in events:
            if event.type == UI_BUTTON_PRESSED:
                if event.ui_element == self.capture_button:
                    capture_button()

                if event.ui_element == self.load_button:
                    self.auto_cap_button.set_text('Auto')

                    self.file_dialog = UIFileDialog(
                        Rect(1360, 130, 440, 500) if is_full_hd else Rect(200, 50, 400, 400),
                        self.manager, 'Load Image...', {".png", ".jpg"},
                        'data' if self.model_name == '-' else os.path.join('data', self.model_name),
                        allow_picking_directories=True,
                        allow_existing_files_only=True,
                        object_id=ObjectID(class_id='@file_dialog', object_id='#open_img_other'),
                    )

                if event.ui_element == self.predict_button:
                    self.predict()
            if event.type == UI_FILE_DIALOG_PATH_PICKED:
                # from Load Image
                if event.ui_object_id == '#open_img_other':
                    if '.png' in event.text:
                        print(event.text)
                        self.np_img = cv2.imread(event.text)
                        self.reset_frame()
                        self.set_name_for_debug()
                # from Open Image
                if event.ui_object_id == '#open_img_full':
                    if '.png' in event.text:
                        print('from open_data', event.text)
                        self.np_img = cv2.imread(event.text)
                        self.reset_frame()
                        self.set_name_for_debug(os.path.split(event.text)[1].replace('.png', ''))

        if self.auto_cap_button.text == 'Stop':
            self.get_surface_form_url(self.config['url_image'])

    def handle_events(self, command_queue, data):
        events = pg.event.get()
        self.panel0_update(events, command_queue)
        self.panel1_update(events)
        self.panel2_update(events, command_queue, data)
        if self.robot_window:
            self.robot_window.events(events)
        for event in events:
            self.manager.process_events(event)
            # if event.type != 1024:
            #     print(event)
            if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
                self.manager.set_active_cursor(pg.SYSTEM_CURSOR_HAND)
            if event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
                self.manager.set_active_cursor(pg.SYSTEM_CURSOR_ARROW)

        self.right_click.events(events)

    def run(self, command_queue, response_queue, data):
        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0
            self.display.fill((220, 220, 220))
            self.get_surface_form_np(self.np_img)

            self.handle_events(command_queue, data)

            self.display.blit(self.panel1_surface, self.panel1_rect.topleft)

            self.manager.update(time_delta)
            self.manager.draw_ui(self.display)

            pg.display.update()

        data['play'] = False


def main(command_queue, response_queue, data={}):
    app = AutoInspectionxRobot()
    app.run(command_queue, response_queue, data)
