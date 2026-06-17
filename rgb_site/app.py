from flask import Flask, render_template, send_file, url_for, request

import numpy as np
from io import BytesIO
from PIL import Image
from rgb import RGB

app = Flask(__name__)

ITERATIONS = 2800
FRAMESKIP = 5
N_TILES_X = 32
N_TILES_Y = 32
IMAGE_H = 256
IMAGE_W = 256

DEFAULT_GROWTH_RATE = .03
DEFAULT_PREDATION_RATE = .001
DEFAULT_PREDATION_EFFICIENCY = .125
DEFAULT_SIGMA = .75

DEFAULT_SIMULATOR_KWARGS = {
    "growth_rate": DEFAULT_GROWTH_RATE,
    "predation_rate": DEFAULT_PREDATION_RATE,
    "predation_efficiency": DEFAULT_PREDATION_EFFICIENCY,
    "sigma": DEFAULT_SIGMA,
}

def generate_simulation_frames(
        growth_rate=None,
        predation_rate=None,
        predation_efficiency=None,
        sigma=None,
    ):

    if growth_rate is None:
        growth_rate = DEFAULT_GROWTH_RATE
    if predation_rate is None:
        predation_rate = DEFAULT_PREDATION_RATE
    if predation_efficiency is None:
        predation_efficiency = DEFAULT_PREDATION_EFFICIENCY
    if sigma is None:
        sigma = DEFAULT_SIGMA

    Q = RGB(growth_rate, predation_rate, predation_efficiency, sigma)

    frame_shape = (N_TILES_X, N_TILES_Y, 3)
    start_frame = 255 * np.random.rand(*(frame_shape))
    result = np.empty((ITERATIONS+1, *frame_shape), float)
    result[0] = start_frame
    for i in range(ITERATIONS):
        result[i+1] = Q.next_frame(result[i])

    # speedup by skipping frames
    result = result[::int(FRAMESKIP)]

    # cap values in result at 255
    mask = result <= 255
    result *= mask
    result += 255 * (~mask)

    image_frame_data_array = result.astype(np.uint8)

    tile_len_h = IMAGE_H // N_TILES_X
    tile_len_w = IMAGE_W // N_TILES_Y
    if tile_len_h > 1:
        image_frame_data_array = np.repeat(image_frame_data_array, tile_len_h, 1)
    if tile_len_w > 1:
        image_frame_data_array = np.repeat(image_frame_data_array, tile_len_w, 2)

    return [
        Image.fromarray(f)
        for f in image_frame_data_array
    ]

def get_bytes_from_frames(frames):
    buffer = BytesIO()
    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration = 32,
        loop=0
    )
    buffer.seek(0)
    return buffer

@app.route("/get_simulator_gif")
def get_simulator_gif():
    kwargs = dict(request.args)
    kwargs = {k: float(v) for k, v in kwargs.items() if v}
    frames = generate_simulation_frames(**kwargs)
    return send_file(
        get_bytes_from_frames(frames),
        mimetype='image/gif',
        as_attachment=False,
        download_name='rgb_simulation.gif'
    )

@app.route("/simulator_page", methods=['GET', 'POST'])
def simulator_page():
    form_data = {**DEFAULT_SIMULATOR_KWARGS}
    show_image = False
    if request.method == 'POST':
        form_data = dict(request.form)
        show_image = True
    return render_template('simulator_page.html', show_image=show_image, **form_data)

@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
