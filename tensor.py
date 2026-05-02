"""TensorFlow (frozen graph) classifier for moth species."""

import numpy as np
import tensorflow as tf
from PIL import Image

from utils import (
    convert_to_opencv,
    crop_center,
    resize_down_to_max_dim,
    resize_to_square,
    update_orientation,
)

_MODEL_PATH = "models/model.pb"
_LABELS_PATH = "models/labels.txt"
_INPUT_NODE = "Placeholder:0"
_OUTPUT_LAYER = "loss:0"


class Tensor:
    """Custom-Vision-style classifier loaded from a frozen TensorFlow graph."""

    def __init__(self) -> None:
        graph_def = tf.compat.v1.GraphDef()
        with tf.io.gfile.GFile(_MODEL_PATH, "rb") as f:
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name="")
        with open(_LABELS_PATH, "rt") as lf:
            self.labels = [line.strip() for line in lf]

    def process(self, image_path: str) -> str:
        """Return the label with the highest probability for `image_path`."""
        image = Image.open(image_path)
        image = update_orientation(image)
        image = convert_to_opencv(image)
        image = resize_down_to_max_dim(image, max_dim=1600)

        # Crop the largest centred square, then downscale to 256×256 so the
        # model receives a stable canvas regardless of the input frame size.
        h, w = image.shape[:2]
        min_dim = min(w, h)
        image = crop_center(image, min_dim, min_dim)
        image = resize_to_square(image, side=256)

        with tf.compat.v1.Session() as sess:
            input_shape = sess.graph.get_tensor_by_name(_INPUT_NODE).shape.as_list()
        network_input_size = input_shape[1]
        image = crop_center(image, network_input_size, network_input_size)

        with tf.compat.v1.Session() as sess:
            try:
                prob_tensor = sess.graph.get_tensor_by_name(_OUTPUT_LAYER)
                predictions = sess.run(prob_tensor, {_INPUT_NODE: [image]})
            except KeyError:
                return f"Couldn't find classification output layer: {_OUTPUT_LAYER}."

        return self.labels[int(np.argmax(predictions))]
