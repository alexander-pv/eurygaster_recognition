import os
from subprocess import call

from eurygaster_webpage import ROOT, LIBNAME
from eurygaster_webpage.cli import parse_args
from eurygaster_webpage.logger import prepare_logger
from loguru import logger

if __name__ == "__main__":
    args = parse_args()
    prepare_logger(
        LIBNAME, os.getenv("LOGURU_LEVEL", "DEBUG"), os.getenv("LOGURU_INIT", True)
    )
    webpage_path = os.path.join(ROOT, "page_manager.py")
    command = f"streamlit run {webpage_path} "
    if args.server_port:
        command += f"--server.port {args.server_port} "
    if args.server_ip:
        command += f"--server.address {args.server_ip} "
    if args.server_max_upload_size:
        command += f"--server.maxUploadSize {args.server_max_upload_size} "
    command += os.getenv("SERVER_ADD_ARGS", "")
    command += (
        " -- "
        + f"--inference_server {args.inference_server} "
        + f"--binary_threshold {args.binary_threshold} "
        + f"--tab_title {args.tab_title} "
        + f"--tab_icon {args.tab_icon} "
    )
    logger.debug(f"CLI command: {command}")
    call(command, shell=True)
