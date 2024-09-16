from flask import Flask, render_template, request

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
            print(f"Button clicked: {button_name}")
    return render_template('index.html')


def run_server(data):
    import logging
    log = logging.getLogger('werkzeug')
    log.disabled = True

    app.config['data'] = data
    ipv4_address = data['ipv4_address']
    port = data['port']
    print(f" * Running on http://{ipv4_address}:{port}")
    app.run(host=ipv4_address, port=port, debug=True, use_reloader=False)
