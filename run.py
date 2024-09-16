import multiprocessing
import socket

import main
import app

if __name__ == '__main__':
    multiprocessing.freeze_support()
    manager = multiprocessing.Manager()
    data = manager.dict()

    data['step'] = 0
    hostname = socket.gethostname()
    ipv4_address = socket.gethostbyname(hostname)
    data['ipv4_address'] = ipv4_address
    data['port'] = 5555
    data['events_from_web'] = []

    inspection_process = multiprocessing.Process(target=main.main, args=(data,))
    run_server_process = multiprocessing.Process(target=app.run_server, args=(data,))

    inspection_process.start()
    run_server_process.start()

    inspection_process.join()
    run_server_process.join()
