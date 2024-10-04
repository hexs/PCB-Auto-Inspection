from manage_json_files import json_load
import signal


def robot_capture(data):
    import urllib.request
    import requests
    import numpy as np
    import cv2
    import time

    def get_image():
        image_url = data['url_image']
        req = urllib.request.urlopen(image_url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)
        return img

    def send_request(endpoint, method='post', **kwargs):
        robot_url = data['robot_url']
        try:
            response = getattr(requests, method)(f"{robot_url}/api/{endpoint}", **kwargs)
            response.raise_for_status()
            print(f"{endpoint.capitalize()} request sent successfully")
            return response.json() if method == 'get' else None
        except requests.RequestException as e:
            print(f"Error sending {endpoint} request: {e}")
            return None

    def home():
        send_request("home", )

    def move_to(row):
        try:
            send_request("move_to", json={"row": row})
        except ValueError:
            print("Invalid row number")

    def y(p):
        return int(wh[1] * p)

    def x(p):
        return int(wh[0] * p)

    if data.get('xfunction') == '':
        return

    go_to_home = True
    while data['play']:
        time.sleep(0.1)
        # data['robot capture'] is '', 'capture', 'capture ok'
        if data['robot capture'] == 'capture':
            if go_to_home:
                go_to_home = False
                home()
                time.sleep(5)

            move_to(1)
            time.sleep(3)
            image1 = get_image()

            move_to(2)
            time.sleep(2)
            image2 = get_image()

            move_to(3)
            time.sleep(2)
            image3 = get_image()

            move_to(4)
            time.sleep(2)
            image4 = get_image()

            move_to(5)
            time.sleep(2)
            image5 = get_image()

            move_to(6)
            time.sleep(2)
            image6 = get_image()

            move_to(7)
            time.sleep(2)
            image7 = get_image()

            move_to(8)
            time.sleep(2)
            image8 = get_image()

            move_to(9)
            time.sleep(2)
            image9 = get_image()

            move_to(0)

            wh = image1.shape[1::-1]
            image = np.concatenate((
                np.concatenate((image1[y(0):y(.5), x(.2):x(.7)], image2[y(.5):y(1), x(.2):x(.7)]), axis=0),
                np.concatenate((image3[y(0):y(.5), x(.4):x(.6)], image4[y(.5):y(1), x(.4):x(.6)]), axis=0),
                np.concatenate((image5[y(0):y(.5), x(.2):x(.8)], image6[y(.5):y(1), x(.2):x(.8)]), axis=0),
                np.concatenate((image7[y(0):y(.5), x(.0):x(.3)], image8[y(.5):y(1), x(.0):x(.3)]), axis=0),
                np.concatenate((image7[y(0):y(.5), x(.7):x(1.)], image8[y(.5):y(1), x(.7):x(1.)]), axis=0),
            ), axis=1)

            wh = image.shape[1::-1]
            print(image9.shape)
            image = np.concatenate((
                np.zeros([500, wh[0], 3], np.uint8),
                image
            ), axis=0)
            image[0:500, 1000:3048] = image9[500:500 + 500, :]

            data['robot capture image'] = image
            data['robot capture'] = 'capture ok'


def signal_handler(signum, frame):
    global data
    print(f"Received signal {signum}. Initiating shutdown...")
    data['play'] = False


if __name__ == '__main__':
    import sys
    import multiprocessing
    import time
    import socket
    import auto_inspection
    import app

    multiprocessing.freeze_support()
    manager = multiprocessing.Manager()
    data = manager.dict()

    for k, v in json_load('config.json').items():
        data[k] = v

    if data['ipv4_address'] == '':
        hostname = socket.gethostname()
        ipv4_address = socket.gethostbyname(hostname)
        data['ipv4_address'] = ipv4_address
    data['events_from_web'] = []
    data['play'] = True
    data['robot capture'] = ''  # is '', 'capture', 'capture ok'
    data['robot capture image'] = None

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    inspection_process = multiprocessing.Process(target=auto_inspection.main, args=(data,))
    run_server_process = multiprocessing.Process(target=app.run_server, args=(data,))
    robot_capture_process = multiprocessing.Process(target=robot_capture, args=(data,))

    try:
        inspection_process.start()
        run_server_process.start()
        robot_capture_process.start()

        while data['play']:
            time.sleep(0.1)

    except Exception as e:
        print(f'An error occurred: {e}')

    finally:
        data['play'] = False

        if inspection_process.is_alive():
            inspection_process.terminate()
        if run_server_process.is_alive():
            run_server_process.terminate()

        inspection_process.join()
        run_server_process.join()

    sys.exit(0)
