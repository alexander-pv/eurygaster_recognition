from setuptools import setup, find_packages

from queue_handler import __version__, LIBNAME

with open("requirements.txt", encoding="utf8") as f:
    required = f.read().splitlines()

setup(
    name=LIBNAME,
    version=__version__,
    packages=find_packages(
        include=[
            "queue_handler",
        ]
    ),
    description="Message broker handler that sends new Eurygaster spp. images to an external storage",
    python_requires=">=3.9",
    classifiers=[
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    install_requires=required,
)
