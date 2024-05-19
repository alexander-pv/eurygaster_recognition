from setuptools import setup, find_packages

from eurygaster_webpage import __version__, LIBNAME

with open("requirements.txt", encoding="utf8") as f:
    required = f.read().splitlines()

setup(
    name=LIBNAME,
    version=__version__,
    packages=find_packages(
        include=[
            "eurygaster_webpage",
            "eurygaster_webpage.info",
            "eurygaster_webpage.info.structures",
        ]
    ),
    description="Eurygaster spp. recognition webpage",
    python_requires=">=3.9",
    classifiers=[
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    install_requires=required,
    include_package_data=True,
)
