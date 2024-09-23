import pygame
import pygame_gui


class Control_Robot_Window:
    def __init__(self, rect=None, manager=None, command_queue=None):
        self.rect = pygame.Rect((50, 50), (600, 300)) if rect is None else rect
        self.manager = manager
        self.command_queue = command_queue

        self.window = pygame_gui.elements.UIWindow(
            self.rect, self.manager,
            window_display_title='Control Robot'
        )
        self.set_button()
        self.current_position_vel = {'01': 0, '02': 0, '03': 0, '04': 0}

    def set_button(self):
        self.alarm_reset_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 5), (100, 30)), 'Alarm reset',
            container=self.window
        )
        self.servo_on_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 5), (100, 30)), 'Servo ON',
            container=self.window, anchors={'left_target': self.alarm_reset_button}
        )
        self.servo_off_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 5), (100, 30)), 'Servo OFF',
            container=self.window, anchors={'left_target': self.servo_on_button}
        )
        self.home_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 5), (100, 30)), 'Home',
            container=self.window, anchors={'left_target': self.servo_off_button}
        )
        self.current_position_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 5), (100, 30)), 'Current Position',
            container=self.window, anchors={'left_target': self.home_button}
        )

        self.s1_label = pygame_gui.elements.UILabel(
            pygame.Rect((5, 40), (100, 30)), 'S1: 0',
            container=self.window,
        )
        self.l1_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 40), (60, 30)), '<',
            container=self.window, anchors={'left_target': self.s1_label}
        )
        self.r1_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 40), (60, 30)), '>',
            container=self.window, anchors={'left_target': self.l1_button}
        )

        self.s2_label = pygame_gui.elements.UILabel(
            pygame.Rect((5, 70), (100, 30)), 'S2',
            container=self.window,
        )
        self.l2_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 70), (60, 30)), '<',
            container=self.window, anchors={'left_target': self.s2_label}
        )
        self.r2_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 70), (60, 30)), '>',
            container=self.window, anchors={'left_target': self.l2_button}
        )

        self.s3_label = pygame_gui.elements.UILabel(
            pygame.Rect((5, 100), (100, 30)), 'S3',
            container=self.window,
        )
        self.l3_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 100), (60, 30)), '<',
            container=self.window, anchors={'left_target': self.s3_label}
        )
        self.r3_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 100), (60, 30)), '>',
            container=self.window, anchors={'left_target': self.l3_button}
        )

        self.s4_label = pygame_gui.elements.UILabel(
            pygame.Rect((5, 130), (100, 30)), 'S4',
            container=self.window,
        )
        self.l4_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 130), (60, 30)), '<',
            container=self.window, anchors={'left_target': self.s4_label}
        )
        self.r4_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 130), (60, 30)), '>',
            container=self.window, anchors={'left_target': self.l4_button}
        )

        self.move_to_entry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((5, 170), (100, 30)),
            container=self.window, initial_text='0'
        )
        self.move_to_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 170), (100, 30)), 'move_to',
            container=self.window, anchors={'left_target': self.move_to_entry}
        )
        self.set_to_button = pygame_gui.elements.UIButton(
            pygame.Rect((5, 170), (100, 30)), 'set_to',
            container=self.window, anchors={'left_target': self.move_to_button}
        )

    def update_position_labels(self):
        self.s1_label.set_text(f"S1: {self.current_position_vel['01']}")
        self.s2_label.set_text(f"S2: {self.current_position_vel['02']}")
        self.s3_label.set_text(f"S3: {self.current_position_vel['03']}")
        self.s4_label.set_text(f"S4: {self.current_position_vel['04']}")

    def update_position(self, position_vel):
        self.current_position_vel = position_vel
        self.update_position_labels()

    def events(self, events):
        for event in events:
            if event.type == pygame_gui.UI_BUTTON_START_PRESS:
                print(event)
                # self.s1_label.set_text(robot.current_position_vel['01'])
                if event.ui_element == self.l1_button:
                    self.command_queue.put(('jog', '01', False, True))
                elif event.ui_element == self.r1_button:
                    self.command_queue.put(('jog', '01', True, True))
                elif event.ui_element == self.l2_button:
                    self.command_queue.put(('jog', '02', False, True))
                elif event.ui_element == self.r2_button:
                    self.command_queue.put(('jog', '02', True, True))
                elif event.ui_element == self.l3_button:
                    self.command_queue.put(('jog', '03', False, True))
                elif event.ui_element == self.r3_button:
                    self.command_queue.put(('jog', '03', True, True))
                elif event.ui_element == self.l4_button:
                    self.command_queue.put(('jog', '04', False, True))
                elif event.ui_element == self.r4_button:
                    self.command_queue.put(('jog', '04', True, True))

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                print(event)
                if event.ui_element == self.l1_button:
                    self.command_queue.put(('jog', '01', False, False))
                elif event.ui_element == self.r1_button:
                    self.command_queue.put(('jog', '01', True, False))
                elif event.ui_element == self.l2_button:
                    self.command_queue.put(('jog', '02', False, False))
                elif event.ui_element == self.r2_button:
                    self.command_queue.put(('jog', '02', True, False))
                elif event.ui_element == self.l3_button:
                    self.command_queue.put(('jog', '03', False, False))
                elif event.ui_element == self.r3_button:
                    self.command_queue.put(('jog', '03', True, False))
                elif event.ui_element == self.l4_button:
                    self.command_queue.put(('jog', '04', False, False))
                elif event.ui_element == self.r4_button:
                    self.command_queue.put(('jog', '04', True, False))

                elif event.ui_element == self.alarm_reset_button:
                    self.command_queue.put(('alarm_reset',))
                elif event.ui_element == self.servo_on_button:
                    self.command_queue.put(('servo', True))
                elif event.ui_element == self.servo_off_button:
                    self.command_queue.put(('servo', False))
                elif event.ui_element == self.home_button:
                    self.command_queue.put(('home',))
                elif event.ui_element == self.current_position_button:
                    self.command_queue.put(('current_position',))
                elif event.ui_element == self.move_to_button:
                    i = int(self.move_to_entry.get_text())
                    self.command_queue.put(('move_to', i))
                elif event.ui_element == self.set_to_button:
                    i = int(self.move_to_entry.get_text())
                    for slave, position in self.current_position_vel.items():
                        if position >= 0xFFFF:
                            continue
                        position_mm = position / 100
                        speed = 200
                        acc = dec = 0.05
                        self.command_queue.put(('set_to', slave, i, position_mm, speed, acc, dec))
