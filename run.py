import signal


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

    hostname = socket.gethostname()
    ipv4_address = socket.gethostbyname(hostname)
    data['ipv4_address'] = ipv4_address
    data['port'] = 5555
    data['events_from_web'] = []
    data['play'] = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    inspection_process = multiprocessing.Process(target=auto_inspection.main, args=(data,))
    run_server_process = multiprocessing.Process(target=app.run_server, args=(data,))

    try:
        inspection_process.start()
        run_server_process.start()

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
