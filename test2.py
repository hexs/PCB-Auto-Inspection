import lgpio
import time
from datetime import datetime
import requests
import threading

OUT1 = 4
OUT2 = 17
OUT3 = 18
OUT4 = 27
BUTTON_LED = 22
OUT6 = 23
RESET_EM = 24
OUT8 = 25

AREA1 = 21
AREA2 = 20
L_BUTTON = 19
R_BUTTON = 16
IN4 = 13
IN3 = 12
IN2 = 6
ALARM = 5

h = lgpio.gpiochip_open(0)
led_blinking = False
led_blinking_time = 0.3
l_button_press = None
r_button_press = None

input_pins = [AREA1, AREA2, L_BUTTON, R_BUTTON, IN4, IN3, IN2, ALARM]
output_pins = [OUT1, OUT2, OUT3, OUT4, BUTTON_LED, OUT6, RESET_EM, OUT8]

for pin in input_pins:
    lgpio.gpio_claim_input(h, pin)

for pin in output_pins:
    lgpio.gpio_claim_output(h, pin)


# Helper functions
def robot_send_request(endpoint, method='post', **kwargs):
    url = 'http://127.0.0.1:2001'
    response = getattr(requests, method)(f"{url}/api/{endpoint}", **kwargs)
    response.raise_for_status()
    print(f"{endpoint.capitalize()} request sent successfully")
    return response.json() if method == 'get' else None


def home():
    robot_send_request("home")


def alarm_reset():
    robot_send_request("alarm_reset")


def read(pin):
    return lgpio.gpio_read(h, pin)


def status_Robot():
    url = 'http://127.0.0.1:2002/status_robot'
    r = requests.get(url)
    return r.text


def start_run():
    url = 'http://127.0.0.1:2002'
    payload = {"button": "Capture&Predict"}
    requests.post(url, data=payload)


def write(pin, status):
    lgpio.gpio_write(h, pin, status)


def blink_led():
    global led_blinking, led_blinking_time
    while led_blinking:
        write(BUTTON_LED, 1)
        time.sleep(led_blinking_time)
        write(BUTTON_LED, 0)
        time.sleep(led_blinking_time)


def led_blink(blink_time=None):
    global led_blinking, led_blinking_time
    if blink_time:
        led_blinking_time = blink_time  # Convert ms to seconds
    if not led_blinking:
        led_blinking = True
        threading.Thread(target=blink_led, daemon=True).start()


def led_off():
    global led_blinking
    led_blinking = False
    write(BUTTON_LED, 0)


def led_on():
    global led_blinking
    led_blinking = False
    write(BUTTON_LED, 1)


# Initialization
write(RESET_EM, 1)
time.sleep(0.2)
write(RESET_EM, 0)
time.sleep(0.2)

alarm_reset()
home()
led_on()

# Main loop
step = 1
while True:
    status_robot = status_Robot()
    l_button = read(L_BUTTON)
    r_button = read(R_BUTTON)
    print(step, read(AREA1), read(AREA2), l_button, r_button, status_robot)

    if step == 1:
        if status_robot == '':
            # ..._button == 0 is press button
            if read(L_BUTTON) == 1:
                l_button_press = None
            if read(R_BUTTON) == 1:
                r_button_press = None

            if l_button == 0 and l_button_press is None:
                l_button_press = datetime.now()
            if r_button == 0 and r_button_press is None:
                r_button_press = datetime.now()

            if l_button_press is not None and r_button_press is not None:
                time_difference = (abs(l_button_press - r_button_press)).total_seconds()
                if time_difference < 0.5:
                    start_run()
                    led_blink(0.4)
                    step += 1
                else:
                    led_blink(0.05)

    elif step == 2:
        if status_robot == 'capture':
            step += 1

    elif step == 3:
        if status_robot == '':
            step = 1
            led_on()

    time.sleep(0.1)
