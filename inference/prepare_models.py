import argparse
import os
import re
import sys

import bentoml
import onnx
import requests
from loguru import logger

import transform

CLASS_MAP = {
    "multiclass_calib_dyn": {
        0: "Eurygaster_austriaca",
        1: "Eurygaster_dilaticollis",
        2: "Eurygaster_integriceps",
        3: "Eurygaster_laeviuscula",
        4: "Eurygaster_maura",
        5: "Eurygaster_testudinaria",
    },
    "binary_calib_dyn": {0: "Eurygaster", 1: "Non_Eurygaster"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_name",
        nargs="+",
        help="Model name to download from GitHub",
        default=[
            "model_0d03affcc3fe4555217e01aee7d73fed7ebdf35a_binary_calib_dyn.onnx",
            "model_4fa9730aef422d53cf1ccb3db93da78d68991301_multiclass_calib_dyn.onnx",
        ],
    )
    parser.add_argument("--tag", help="GitHub release tag", default="v1.3.0")
    parser.add_argument(
        "--download_only", action="store_true", help="Download weights and stop"
    )
    return parser.parse_args()


def download_weights(download_path: str) -> None:
    """
    Download ONNX weights if necessary
    :param download_path: str
    :return: None
    """
    name = download_path.split(os.sep)[-1]
    if name not in os.listdir("./"):
        try:
            r = requests.get(download_path)
            open(name, "wb").write(r.content)
            logger.success(f"Downloaded model: {name} from: {download_path}")
        except ConnectionError as e:
            logger.error(f"Failed to download model {name} from  {download_path}.\n{e}")
    else:
        logger.info(f"Found stored model: {name}. Skip downloading")


def export_onnx_to_bentoml(onnx_filename: str) -> None:
    """
    Export model to BentoML
    :param onnx_filename: str, example: <name>.onnx
    :return: None
    """
    match = re.search(
        "model_([a-zA-Z0-9]+)_([a-zA-Z0-9_]+).onnx", onnx_filename
    ).groups()
    model_hash, model_name = match
    onnx_model = onnx.load(onnx_filename)
    metadata = {
        "image_size": 300,
        "img_normalize": {"mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]},
        "class_map": CLASS_MAP[model_name],
    }
    bentoml.onnx.save_model(
        name=f"eurygaster_{model_name}",
        model=onnx_model,
        signatures={
            "run": {"batchable": True},
        },
        labels={
            "owner": "alexander-pv",
            "model_hash": model_hash,
            "input_shape": onnx_model.graph.input[0].__str__(),
            "output_shape": onnx_model.graph.output[0].__str__(),
        },
        custom_objects={
            "preprocessor": transform.get_input_transform(
                metadata["image_size"], metadata["img_normalize"]
            )
        },
        external_modules=[transform],
        metadata=metadata,
    )
    logger.info(f"Exported model to BentoML: {onnx_filename}")


def main() -> None:
    args = parse_args()
    logger.debug(args)
    tag = args.tag
    onnx_filenames = args.model_name
    download_path = (
        f"https://github.com/alexander-pv/eurygaster_app/releases/download/{tag}/"
    )

    for onnx_name in onnx_filenames:
        download_weights(os.path.join(download_path, onnx_name))
        if args.download_only:
            pass
        else:
            export_onnx_to_bentoml(onnx_name)


if __name__ == "__main__":
    main()
