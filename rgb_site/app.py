from flask import Flask, render_template, send_file, url_for

import numpy as np
from io import BytesIO
from PIL import Image
from rgb import RGB

app = Flask(__name__)

def generate_simulation_frames():

    iterations = 2000
    speedup = 5
    size = 32
    image_size = 256
    growth_rate = .03
    predation_rate = .001
    predation_efficiency = .125
    sigma = .75

    Q = RGB(growth_rate, predation_rate, predation_efficiency, sigma)

    frame_shape = (size, size, 3)
    start_frame = 255 * np.random.rand(*(frame_shape))
    result = np.empty((iterations+1, *frame_shape), float)
    result[0] = start_frame
    for i in range(iterations):
        result[i+1] = Q.next_frame(result[i])

    # speedup by skipping frames
    result = result[::int(speedup)]

    # cap values in result at 255
    mask = result <= 255
    result *= mask
    result += 255 * (~mask)

    image_frame_data_array = result.astype(np.uint8)

    # resize if needed
    if size != image_size:
        img_h = img_w = image_size
        tile_len_h = img_h // result.shape[1]
        tile_len_w = img_w // result.shape[2]
        image_frame_data_array = np.repeat(image_frame_data_array, tile_len_h, 1)
        image_frame_data_array = np.repeat(image_frame_data_array, tile_len_w, 2)

    return [
        Image.fromarray(f)
        for f in image_frame_data_array
    ]

def get_bytes_from_frames(frames):
    frames = generate_simulation_frames()
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
    frames = generate_simulation_frames()
    sim_gif = get_bytes_from_frames(frames)
    return send_file(
        get_bytes_from_frames(frames),
        mimetype='image/gif',
        as_attachment=False,
        download_name='rbg_simulation.gif'
    )

@app.route("/simulator_page")
def simulator_page():
    return render_template('simulator_page.html')

@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
