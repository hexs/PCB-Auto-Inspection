from manage_json_files import json_load
from flask import Flask, render_template, request
import logging
import multiprocessing
import socket
import urllib.request
import requests
import numpy as np
import cv2
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        button_name = request.form.get('button')
        if button_name:
            data = app.config['data']
            events_from_web = data['events_from_web']
            events_from_web.append(button_name)
            data['events_from_web'] = events_from_web
            logger.info(f"Button clicked: {button_name}")
    return render_template('index.html')


def run_server(data):
    app.config['data'] = data
    ipv4_address = data['ipv4_address']
    port = data['port']
    logger.info(f" * Running on http://{ipv4_address}:{port}")
    app.run(host=ipv4_address, port=port, debug=False, use_reloader=False)


def get_image(url):
    try:
        with urllib.request.urlopen(url) as req:
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        return cv2.imdecode(arr, -1)
    except Exception as e:
        logger.error(f"Error getting image: {e}")
        return None


def send_request(robot_url, endpoint, method='post', **kwargs):
    try:
        response = getattr(requests, method)(f"{robot_url}/api/{endpoint}", **kwargs)
        response.raise_for_status()
        logger.info(f"{endpoint.capitalize()} request sent successfully")
        return response.json() if method == 'get' else None
    except requests.RequestException as e:
        logger.error(f"Error sending {endpoint} request: {e}")
        return None


def robot_capture(data):
    def move_and_capture(row):
        send_request(data['robot_url'], "move_to", json={"row": row})
        time.sleep(2)
        return get_image(data['url_image'])

    if not data.get('xfunction'):
        return

    while data['play']:
        time.sleep(0.1)
        if data['robot capture'] == 'capture':
            send_request(data['robot_url'], "home")
            time.sleep(5)

            images = [move_and_capture(i) for i in range(1, 10)]
            send_request(data['robot_url'], "move_to", json={"row": 0})

            if not all(images):
                logger.error("Failed to capture all images")
                data['robot capture'] = 'capture error'
                continue

            wh = images[0].shape[1::-1]
            y = lambda p: int(wh[1] * p)
            x = lambda p: int(wh[0] * p)

            image = np.concatenate((
                np.concatenate((images[0][y(0):y(.5), x(.2):x(.7)], images[1][y(.5):y(1), x(.2):x(.7)]), axis=0),
                np.concatenate((images[2][y(0):y(.5), x(.4):x(.6)], images[3][y(.5):y(1), x(.4):x(.6)]), axis=0),
                np.concatenate((images[4][y(0):y(.5), x(.2):x(.8)], images[5][y(.5):y(1), x(.2):x(.8)]), axis=0),
                np.concatenate((images[6][y(0):y(.5), x(.0):x(.3)], images[7][y(.5):y(1), x(.0):x(.3)]), axis=0),
                np.concatenate((images[6][y(0):y(.5), x(.7):x(1.)], images[7][y(.5):y(1), x(.7):x(1.)]), axis=0),
            ), axis=1)

            image = np.concatenate((
                np.zeros([500, image.shape[1], 3], dtype=np.uint8),
                image
            ), axis=0)
            image[0:500, 1000:3048] = images[8][500:1000, :]

            data['robot capture image'] = image
            data['robot capture'] = 'capture ok'


def main():
    import auto_inspection

    multiprocessing.freeze_support()
    manager = multiprocessing.Manager()
    data = manager.dict()

    config = json_load('config.json')
    data.update(config)

    if not data['ipv4_address']:
        data['ipv4_address'] = socket.gethostbyname(socket.gethostname())

    data['events_from_web'] = []
    data['play'] = True
    data['robot capture'] = ''
    data['robot capture image'] = None

    processes = [
        multiprocessing.Process(target=auto_inspection.main, args=(data,)),
        multiprocessing.Process(target=run_server, args=(data,)),
        multiprocessing.Process(target=robot_capture, args=(data,))
    ]

    for process in processes:
        process.start()

    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Terminating processes.")
        for process in processes:
            process.terminate()
        for process in processes:
            process.join()


if __name__ == '__main__':
    main()
