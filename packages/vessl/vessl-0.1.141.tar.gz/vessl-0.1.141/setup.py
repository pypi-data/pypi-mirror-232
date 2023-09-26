import os
from importlib.machinery import SourceFileLoader

import setuptools

version = (
    SourceFileLoader(
        "vessl._version",
        os.path.join(
            "vessl",
            "_version.py",
        ),
    )
    .load_module()
    .__VERSION__
)

with open("README.md") as fh:
    long_description = fh.read()

requirements = [
    "boto3>=1.18.9",
    "click>=8.0.1",
    "cloudpickle==1.6.0",
    "docker>=6.0.1",
    "fastapi==0.78.0",
    "inquirer>=3.1.3",
    "kubernetes==24.2.0",
    "paramiko==2.11.0",
    "python-dateutil>=2.8.1",
    "requests>=2.0.0",
    "requests-futures>=1.0.0",
    "sentry-sdk>=1.1.0",
    "schema>=0.7.4",
    "shortuuid>=1.0.1",
    "sshpubkeys==3.3.1",
    "terminaltables>=3.1.0",
    "timeago==1.0.15",
    "toml==0.10.1",
    "tqdm<5.0.0,>=4.61.2",
    "psutil==5.9.5",
    "pynvml==11.0.0",
    "PyYAML==6.0.1",
    "humanfriendly==10.0",
    "uvicorn>=0.16.0",
    "halo==0.0.31",
    "python-dotenv==1.0.0",
]

media_requirements = ["numpy", "Pillow>=8.0.0", "soundfile", "wave"]

setuptools.setup(
    name="vessl",
    version=version,
    author="VESSL AI Dev Team",
    author_email="contact@vessl.ai",
    description="A library and CLI for VESSL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "vessl=vessl.cli._main:cli",
            "vsl=vessl.cli._main:cli",
        ],
    },
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    extras_require={"media": media_requirements},
)
