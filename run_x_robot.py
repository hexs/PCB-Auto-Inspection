

if __name__ == '__main__':
    import sys
    import multiprocessing
    import time
    import socket
    import auto_inspection_x_robot
    import app
    from robot import robot_run

    multiprocessing.freeze_support()

    command_queue = multiprocessing.Queue()
    response_queue = multiprocessing.Queue()
    manager = multiprocessing.Manager()
    data = manager.dict()

    hostname = socket.gethostname()
    ipv4_address = socket.gethostbyname(hostname)
    data['ipv4_address'] = ipv4_address
    data['port'] = 5555
    data['events_from_web'] = []
    data['play'] = True

    inspection_process = multiprocessing.Process(target=auto_inspection_x_robot.main,
                                                 args=(command_queue, response_queue, data))
    robot_process = multiprocessing.Process(target=robot_run, args=(command_queue, response_queue))
    run_server_process = multiprocessing.Process(target=app.run_server, args=(data,))

    inspection_process.start()
    robot_process.start()
    run_server_process.start()

    inspection_process.join()
    run_server_process.join()

    sys.exit(0)
