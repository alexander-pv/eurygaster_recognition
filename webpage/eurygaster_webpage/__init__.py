import os
import pathlib

__version__ = "1.4.0"
LIBNAME = "eurygaster_webpage"
ROOT = pathlib.Path(__file__).parent
SUPPORTED_LANG = os.listdir(os.path.join(ROOT, "info", "markdown"))
GITHUB = "https://github.com/alexander-pv/eurygaster_recognition/releases"
ISSUES = "https://github.com/alexander-pv/eurygaster_recognition/issues"
