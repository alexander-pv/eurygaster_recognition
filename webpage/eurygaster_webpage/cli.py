import argparse
import os


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="eurygaster webpage argument parser")
    parser.add_argument(
        "--webpage_port",
        type=int,
        default=int(os.environ.get("EURYGASTER_WEBPAGE_PORT", 4452)),
        help="Webpage port",
    )
    parser.add_argument(
        "--webpage_ip",
        type=str,
        default=os.environ.get("EURYGASTER_WEBPAGE_IP", "0.0.0.0"),
        help="Webpage ip",
    )
    parser.add_argument(
        "--inference_server",
        type=str,
        default=os.environ.get("INFERENCE_SERVER_ADDRESS", "http://localhost:3000"),
        help="str, inference server address, default: http://localhost:3000",
    )
    parser.add_argument(
        "--binary_threshold",
        type=float,
        default=0.5,
        help="float, binary model threshold",
    )
    parser.add_argument(
        "--tab_title",
        type=str,
        default="EurygasterRecognitionApp",
        help="str, tab title",
    )
    parser.add_argument(
        "--tab_icon",
        type=str,
        default="https://cdn-icons-png.flaticon.com/512/144/144932.png",
        help="str, tab icon url",
    )
    return parser.parse_args()
