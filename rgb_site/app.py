from flask import (
    Flask,
    render_template,
    send_file,
    url_for,
    request,
)


import os
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from base64 import b64encode
from PIL import Image
from werkzeug.utils import secure_filename
from rgb import RGB, RGBField


app = Flask(__name__)
app.config['UPLOAD'] = '/upload'


# Float Fields
DEFAULT_GROWTH_RATE = .03
DEFAULT_PREDATION_RATE = .0003
DEFAULT_PREDATION_EFFICIENCY = .1
DEFAULT_SIGMA = 1

# Integer Fields
DEFAULT_ITERATIONS = 2500
DEFAULT_FRAMESKIP = 5
DEFAULT_X_TILES = 32
DEFAULT_Y_TILES = 32
DEFAULT_TILE_SIZE = 1
DEFAULT_IMAGE_HEIGHT = 400
DEFAULT_IMAGE_WIDTH = 400

DEFAULT_KWARGS = {
    "growth_rate": DEFAULT_GROWTH_RATE,
    "predation_rate": DEFAULT_PREDATION_RATE,
    "predation_efficiency": DEFAULT_PREDATION_EFFICIENCY,
    "sigma": DEFAULT_SIGMA,
    "iterations": DEFAULT_ITERATIONS,
    "frameskip": DEFAULT_FRAMESKIP,
    "x_tiles": DEFAULT_X_TILES,
    "y_tiles": DEFAULT_Y_TILES,
    "tile_size": DEFAULT_TILE_SIZE,
    "image_height": DEFAULT_IMAGE_HEIGHT,
    "image_width": DEFAULT_IMAGE_WIDTH,
}


def generate_single_pixel_graph(
        growth_rate = DEFAULT_GROWTH_RATE,
        predation_rate = DEFAULT_PREDATION_RATE,
        predation_efficiency = DEFAULT_PREDATION_EFFICIENCY,
        iterations = DEFAULT_ITERATIONS,
        **kwargs
    ):

    Q = RGB(
        growth_rate=growth_rate,
        predation_rate=predation_rate,
        predation_efficiency=predation_efficiency,
    )

    start_pixel = 255 * np.random.rand(3)
    result = np.empty((iterations, 3), float)
    result[0] = start_pixel
    for i in range(1, iterations):
        result[i] = Q.next_pixel(result[i-1])

    fix, ax = plt.subplots()
    N = np.arange(len(result))
    r_result = result[:, 0]
    g_result = result[:, 1]
    b_result = result[:, 2]
    ax.plot(N, r_result, label='red', color='red')
    ax.plot(N, g_result, label='green', color='green')
    ax.plot(N, b_result, label='blue', color='blue')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    return buffer


def generate_simulation_frames(
        start_image = None,
        growth_rate = DEFAULT_GROWTH_RATE,
        predation_rate = DEFAULT_PREDATION_RATE,
        predation_efficiency = DEFAULT_PREDATION_EFFICIENCY,
        sigma = DEFAULT_SIGMA,
        iterations = DEFAULT_ITERATIONS,
        frameskip = DEFAULT_FRAMESKIP,
        x_tiles = DEFAULT_X_TILES,
        y_tiles = DEFAULT_Y_TILES,
        tile_size = DEFAULT_TILE_SIZE,
        **kwargs
    ):

    Q = RGBField(
        growth_rate=growth_rate,
        predation_rate=predation_rate,
        predation_efficiency=predation_efficiency,
        sigma=sigma,
    )

    frame_shape = (x_tiles, y_tiles, 3)
    if start_image is None:
        start_frame = 255 * np.random.rand(*(frame_shape))
    else:
        start_image = start_image.resize(frame_shape[:2])
        start_frame = np.asarray(start_image)

    n_frames = iterations // frameskip
    result = np.empty((n_frames, *frame_shape), float)
    result[0] = current_frame = start_frame
    for i in range(1, iterations):
        current_frame = Q.next_frame(current_frame)
        if i % frameskip == 0:
            result[i // frameskip] = current_frame

    # cap values in result at 255
    mask = result <= 255
    result *= mask
    result += 255 * (~mask)

    image_frame_data_array = result.astype(np.uint8)

    if tile_size > 1:
        image_frame_data_array = np.repeat(image_frame_data_array, tile_size, 1)
        image_frame_data_array = np.repeat(image_frame_data_array, tile_size, 2)

    return [
        Image.fromarray(f)
        for f in image_frame_data_array
    ]


def gif_bytes(frames):
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


def clean_kwargs(d):
    return {
        k: type(DEFAULT_KWARGS[k])(v)
        for k, v in d.items()
        if v and k in DEFAULT_KWARGS
    }


def get_thumbnail_b64(image, size=(64, 64)):
    image = image.resize(size)
    buffer = BytesIO()
    image.save(buffer, 'JPEG')
    buffer.seek(0)
    return b64encode(buffer.read()).decode('utf-8')


@app.route("/get_simulator_gif")
def get_simulator_gif():
    sim_kwargs = clean_kwargs(request.args)
    if upload_fname := request.args.get('upload_fname', None):
        sim_kwargs['start_image'] = Image.open(
            os.path.join(app.config['UPLOAD'], upload_fname)
        )
    frames = generate_simulation_frames(**sim_kwargs)
    return send_file(
        gif_bytes(frames),
        mimetype='image/gif',
        as_attachment=False,
        download_name='rgb_simulation.gif'
    )


@app.route("/image_upload_simulator", methods = ['GET', 'POST'])
def image_upload_simulator():

    form_data = {**DEFAULT_KWARGS}

    if request.method == 'POST':

        show_image = True
        form_data |= {k: v for k, v in request.form.items() if v}

        # If new image upload
        if (f := request.files.get('uploaded_image', None)) and f.filename:
            h = str(abs(hash(f.read())))
            f.seek(0)
            filename = secure_filename(f.filename)
            form_data["display_fname"] = filename
            form_data["upload_fname"] = f'{h}_{filename}'
            f.save(os.path.join(app.config['UPLOAD'], form_data["upload_fname"]))
            f.seek(0)
            with Image.open(f) as img:
                thumbnail = get_thumbnail_b64(img)

        # If no new image, but previous image exists
        elif (upload_fname := request.form.get('upload_fname', None)) \
        and upload_fname in os.listdir(app.config['UPLOAD']):
            img_path = os.path.join(app.config['UPLOAD'], upload_fname)
            with Image.open(img_path) as img:
                thumbnail = get_thumbnail_b64(img)

        else:
            show_image = False
            thumbnail = None

        return render_template(
            'image_upload_simulator.html',
            show_image=show_image,
            thumbnail=thumbnail,
            img_kwargs=form_data,
            **form_data,
        )

    return render_template('image_upload_simulator.html', **form_data)


@app.route("/random_simulator", methods=['GET', 'POST'])
def random_simulator():
    form_data = {**DEFAULT_KWARGS}
    show_image = False
    if request.method == 'POST':
        form_data |= {k: v for k, v in request.form.items() if v}
        show_image = True
    return render_template(
        'random_simulator.html',
        show_image=show_image,
        img_kwargs=form_data,
        **form_data
    )


@app.route("/get_single_pixel_graph")
def get_single_pixel_graph():
    kwargs = clean_kwargs(request.args)
    graph_png_bytes = generate_single_pixel_graph(**kwargs)
    return send_file(
        graph_png_bytes,
        mimetype='image/png',
        as_attachment=False,
        download_name='single_pixel_graph.png'
    )


@app.route("/single_pixel_simulator", methods=['GET', 'POST'])
def single_pixel_simulator():
    form_data = {**DEFAULT_KWARGS}
    show_image = False
    if request.method == 'POST':
        form_data |= {k: v for k, v in request.form.items() if v}
        show_image = True
    return render_template(
        'single_pixel_simulator.html',
        show_image=show_image,
        img_kwargs=form_data,
        **form_data
    )


@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
