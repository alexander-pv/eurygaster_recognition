import os
import pathlib

import bentoml
import numpy as np
import pytest
from PIL import Image


@pytest.mark.parametrize(
    "model", ["eurygaster_multiclass_calib_dyn", "eurygaster_binary_calib_dyn"]
)
@pytest.mark.parametrize("providers", [["CPUExecutionProvider"]])
class TestModel:
    test_input = np.random.randn(1, 3, 300, 300)

    def prepare_model(self, model: str, providers: list[str]):
        bento_model = bentoml.onnx.get(f"{model}:latest")
        print(bento_model, bento_model.custom_objects)
        runner = bento_model.with_options(providers=providers).to_runner()
        runner.init_local()
        return bento_model, runner

    def test_has_preprocessor(self, model: str, providers: list[str]):
        bento_model = bentoml.onnx.get(f"{model}:latest")
        preprocessor = bento_model.custom_objects.get("preprocessor", None)
        assert preprocessor is not None

    def test_image_preprocess(self, model: str, providers: list[str]):
        bento_model, runner = self.prepare_model(model, providers)
        preprocessor = bento_model.custom_objects.get("preprocessor", None)
        jpeg_image = Image.fromarray(self.test_input[0].astype(np.uint8), mode="RGB")
        assert isinstance(preprocessor(jpeg_image), np.ndarray)

    def test_has_null(self, model: str, providers: list[str]):
        _, runner = self.prepare_model(model, providers)
        output = runner.run.run(self.test_input)
        print(output, np.isnan(output).any())
        assert np.isnan(output).any() == np.bool_(0)

    def test_has_inf(self, model: str, providers: list[str]):
        _, runner = self.prepare_model(model, providers)
        output = runner.run.run(self.test_input)
        print(output, np.isnan(output).any())
        assert np.isinf(output).any() == np.bool_(0)

    def test_real_image(self, model: str, providers: list[str]):
        bento_model, runner = self.prepare_model(model, providers)
        preprocessor = bento_model.custom_objects.get("preprocessor", None)
        jpeg_image = Image.open(
            os.path.join(pathlib.Path(__file__).parent, "eurygaster_testudinaria.jpeg")
        )
        input_data = np.expand_dims(preprocessor(jpeg_image), 0)
        output = runner.run.run(input_data)
        class_id = np.argmax(output)
        class_name = bento_model.info.metadata["class_map"][class_id]
        print(output, class_name)
        assert class_name in ("Eurygaster", "Eurygaster_testudinaria")
