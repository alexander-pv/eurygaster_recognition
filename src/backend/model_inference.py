import os
from typing import Callable, Optional

import numpy as np
import onnxruntime as ort
from PIL.JpegImagePlugin import JpegImageFile
from scipy.special import softmax

import input_transform
import utils


class ONNXInference:

    def __init__(self, onnx_model_name: str, input_name: str, output_name: str,
                 preprocess: Callable[[np.array], np.array], class_map: dict):
        """
        Wrapper for ONNX model inference
        :param onnx_model_name:  str, "<model_name>.onnx"
        :param input_name: str
        :param output_name: str
        :param preprocess: function for input transformation, from torchvision.transform
        :param class_map: dict, class mapping: {class_id: class_name, ...}
        """
        self.onnx_model_name = onnx_model_name
        self.input_name = input_name
        self.output_name = output_name
        self.ort_sess = ort.InferenceSession(self.onnx_model_name)
        self.preprocess = preprocess
        self.class_map = class_map

    def run(self, image: JpegImageFile) -> np.array:
        """
        Run onnxruntime inference session
        :param image: Pillow JpegImageFile, image input
        :return:      np.array, softmax output
        """
        input_data = np.expand_dims(self.preprocess(image), 0)
        outputs = self.ort_sess.run(output_names=[self.output_name], input_feed={self.input_name: input_data})
        return softmax(outputs).ravel()


class EurygasterModels:

    def __init__(self, models_config: tuple, model_path: Optional[str] = None):
        """
        Wrapper for Eurygaster spp. models runtime
        :param models_config:
        """
        self.model_path = model_path
        self.models_config = models_config
        self.onnx_models = []
        utils.download_weights(model_path=self.model_path)
        self.build_models()

    def build_models(self) -> None:
        """
        Open onnxruntime inference sessions
        :return: List[ONNXInference, ONNXInference]
        """
        for config in self.models_config:
            self.onnx_models.append(
                ONNXInference(
                    onnx_model_name=os.path.join("backend", "onnx_model", config.model_name),
                    input_name="mobilenetv2_input",
                    output_name="mobilenetv2_output",
                    preprocess=input_transform.get_input_transform(
                        image_size=config.input_size, img_normalize=config.normalization
                    ),
                    class_map=config.class_map
                )
            )

    @staticmethod
    def get_confidence_dict(class_map: dict, model_output: np.array) -> dict:
        """
        Get confidence dict for a specific model
        :param class_map: dict
        :param model_output: np.array
        :return: dict
        """
        conf_dict = dict()
        for i, conf in enumerate(model_output):
            conf_dict.update({class_map[i]: "%.3f" % conf})
        return conf_dict

    def __call__(self, pil_image) -> list:
        outputs = []
        for model in self.onnx_models:
            outputs.append(
                self.get_confidence_dict(class_map=model.class_map, model_output=model.run(image=pil_image)
                                         )
            )
        return outputs
