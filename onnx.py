"""ONNX Runtime inference wrapper."""

import cv2
import numpy as np
import onnxruntime

_MODEL_PATH = "models/model.onnx"
_INPUT_SIZE = 224

# ImageNet normalisation constants — model was trained with these.
_MEAN = np.array([0.485, 0.456, 0.406])
_STD = np.array([0.229, 0.224, 0.225])


class ONNX:
    """Loads `models/model.onnx` once and runs inference on demand."""

    def __init__(self) -> None:
        self.session = onnxruntime.InferenceSession(_MODEL_PATH)

    def _preprocess(self, image_path: str) -> np.ndarray:
        image = cv2.imread(image_path)
        resized = cv2.resize(image, (_INPUT_SIZE, _INPUT_SIZE))
        data = np.array(resized, dtype=np.float32) / 255.0
        data = (data - _MEAN) / _STD
        return np.expand_dims(data, axis=0)

    def process(self, image_file: str) -> np.ndarray:
        return self.session.run([], {"input": self._preprocess(image_file)})[0]
