import time
import urllib.request
from datetime import datetime, timedelta
import serial
import cv2
import numpy as np
from control_robot_window import Control_Robot_Window


class Robot:
    def __init__(self):
        self.ser = serial.Serial(port='COM12', baudrate=38400)
        print(f"Connected to: {self.ser.portstr}")

        self.current_position_vel = {'01': 0, '02': 0, '03': 0, '04': 0}
        self.send_data_last_datetime = datetime.now()
        self.buffer = bytearray()

    def LRC_calculation(self, message):
        sum_of_bytes = sum(int(message[i:i + 2], 16) for i in range(0, len(message), 2))
        error_check = f'{(0x100 - sum_of_bytes) & 0xFF:02X}'
        full_message = f':{message}{error_check}\r\n'.encode()
        return full_message

    def send_data_(self, slave_address: str, function_code: str, register_address: str, *args):
        while True:
            if datetime.now() - self.send_data_last_datetime > timedelta(milliseconds=20):
                self.send_data_last_datetime = datetime.now()
                message = f'{slave_address}{function_code}{register_address}'
                for data in args:
                    message += data
                message = self.LRC_calculation(message)
                print(f"Sending: {message} len(){len(message)}")
                self.ser.write(message)
                break

    def send_data(self, slave_address: str, function_code: str, register_address: str, *args):
        if slave_address == 'all':
            for addr in ['01', '02', '03', '04']:
                self.send_data_(addr, function_code, register_address, *args)
        else:
            self.send_data_(slave_address, function_code, register_address, *args)

    def jog(self, slave, positive_side, move):
        register = '0416' if positive_side else '0417'
        data = 'FF00' if move else '0000'
        self.send_data(slave, '05', register, data)
        self.current_position()

    def alarm_reset(self):
        print('Alarm reset+')
        self.send_data('all', '05', '0407', 'FF00')

        print('Alarm reset-')
        self.send_data('all', '05', '0407', '0000')

    def servo(self, on=True):
        if on:
            print('Servo ON')
            self.send_data('all', '05', '0403', 'FF00')
        else:
            print('Servo OFF')
            self.send_data('all', '05', '0403', '0000')

    def home(self):
        print('Home')
        self.send_data('all', '05', '040B', 'FF00')
        self.send_data('all', '05', '040B', '0000')

    def current_position(self):
        print('Read Current Position')
        self.send_data('all', '03', '9000', '0002')

    def move_to(self, row: int):
        self.send_data('all', '06', '9800', f'{row:04}')

    def set_to(self, slave: str, row: int, position: float, speed: float, acc: float, dec: float):
        '''
        :param slave: 01, 02, 03, 04
        :param row: NO.
        :param position: target_position(mm)
        :param speed: speed(mm/sec)
        :param acc: acceleration
        :param dec: deceleration
        :return:
        '''
        slave_address = slave
        function_code = '10'
        start_address = '1000'
        i_hex = f'{0x100 + row:03X}0'
        if len(i_hex) == 4:
            start_address = i_hex
        number_of_regis = '000F'
        number_of_bytes = '1E'
        changed_data_1 = '0000'
        changed_data_2 = '2710'  # todo # target position = 100 (mm) x 100 = 10000 → 2710
        position_hex = f'{int(position * 100):04X}'
        if len(position_hex) == 4:
            changed_data_2 = position_hex
        changed_data_3 = '0000'
        changed_data_4 = '000A'
        changed_data_5 = '0000'
        changed_data_6 = '4E20'  # todo # speed = 200 (mm/sec) x 100 = 20000 → 4E20
        speed_hex = f'{int(speed * 100):04X}'
        if len(speed_hex) == 4:
            changed_data_6 = speed_hex
        changed_data_7 = '0000'
        changed_data_81 = '1770'
        changed_data_82 = '0FA0'
        changed_data_9 = '0000'
        changed_data_10 = '0FA0'
        changed_data_11 = '0001'  # todo # acceleration =0.01 (G) x 100 = 1 → 0001
        acc_hex = f'{int(acc * 100):04X}'
        if len(acc_hex) == 4:
            changed_data_11 = acc_hex
        changed_data_12 = '001E'  # todo # deceleration =0.3 (G) x 100 = 30 → 001E
        dec_hex = f'{int(dec * 100):04X}'
        if len(dec_hex) == 4:
            changed_data_12 = dec_hex
        changed_data_13 = '0000'
        changed_data_14 = '0000'
        changed_data_15 = '0000'
        self.send_data(
            slave_address,
            function_code,
            start_address,
            number_of_regis,
            number_of_bytes,
            changed_data_1,
            changed_data_2,
            changed_data_3,
            changed_data_4,
            changed_data_5,
            changed_data_6,
            changed_data_7,
            changed_data_81,
            # changed_data_82,
            changed_data_9,
            changed_data_10,
            changed_data_11,
            changed_data_12,
            changed_data_13,
            changed_data_14,
            changed_data_15
        )

    def get_image(self):
        url = 'http://192.168.225.137:2000/image?source=video_capture&id=0'
        req = urllib.request.urlopen(url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)
        return img
        cv2.imwrite('Image from URL', img)

    def cap(self):
        self.move_to(1)
        time.sleep(3)
        image1 = self.get_image()

        self.move_to(2)
        time.sleep(2)
        image2 = self.get_image()

        self.move_to(3)
        time.sleep(2)
        image3 = self.get_image()

        self.move_to(4)
        time.sleep(2)
        image4 = self.get_image()

        self.move_to(5)
        time.sleep(2)
        image5 = self.get_image()

        cv2.imwrite('image1.png', image1)
        cv2.imwrite('image2.png', image2)
        cv2.imwrite('image3.png', image3)
        cv2.imwrite('image4.png', image4)
        cv2.imwrite('image5.png', image5)

        wh = image1.shape[1::-1]

        def y(p):
            return int(wh[1] * p)

        def x(p):
            return int(wh[0] * p)

        image = np.concatenate((
            image1[0:y(1), x(.2):x(.7)],
            image2[0:y(1), x(.2):x(.8)],
            image3[0:y(1), x(.2):x(.8)],
            image4[0:y(1), x(.0):x(1.)],
            image5[0:y(1), x(.4):x(.6)],
        ), axis=1)

        cv2.imwrite('image.png', image)
        cv2.imshow('img', cv2.resize(image, None, fx=0.2, fy=0.2, interpolation=cv2.INTER_CUBIC))
        cv2.waitKey(0)

    def evens(self, string):
        if len(string) == 17:
            if string[3:7] == '0304':  # read Current Position
                slave = string[1:3]
                vel = string[7:-2]
                print(slave, int(vel, 16))
                self.current_position_vel[slave] = int(vel, 16)

    def run(self):
        # read
        if self.ser.in_waiting:
            data_ = self.ser.read(self.ser.in_waiting)
            self.buffer.extend(data_)
            while b'\r\n' in self.buffer:
                message, self.buffer = self.buffer.split(b'\r\n', 1)
                if message.startswith(b':'):
                    print(f'receive: {message + b"\r\n"}')
                    string = message.decode()
                    self.evens(string)


def robot_run(command_queue, response_queue):
    import time
    import queue

    robot = Robot()
    running = True
    last_update_time = time.time()

    while running:
        try:
            command = command_queue.get(timeout=0.1)
            if command[0] == 'stop':
                running = False
            elif command[0] == 'jog':
                robot.jog(*command[1:])
            elif command[0] == 'alarm_reset':
                robot.alarm_reset()
            elif command[0] == 'servo':
                robot.servo(*command[1:])
            elif command[0] == 'home':
                robot.home()
            elif command[0] == 'current_position':
                robot.current_position()
            elif command[0] == 'move_to':
                robot.move_to(*command[1:])
            elif command[0] == 'set_to':
                robot.set_to(*command[1:])

            response_queue.put(f"Executed command: {command}")
        except queue.Empty:
            pass
        robot.run()

        # Send current position values every 100ms
        current_time = time.time()
        if current_time - last_update_time > 0.1:
            response_queue.put(('update_position', robot.current_position_vel))
            last_update_time = current_time


if __name__ == '__main__':
    robot = Robot()
    robot.cap()
