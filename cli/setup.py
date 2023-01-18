import os
from setuptools import find_packages, setup

with open("enginecli/version.txt") as ifp:
    VERSION = ifp.read().strip()

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

# eth-brownie should be installed as a library so that it doesn't pin version numbers for all its dependencies
# and wreak havoc on the install.
# NOTE: We first implemented this here - https://github.com/G7DAO/contracts/blob/2c04437633e574ae01b45b16f33694cb4a01b7a3/game7ctl/setup.py
os.environ["BROWNIE_LIB"] = "1"

setup(
    name="enginecli",
    version=VERSION,
    packages=find_packages(),
    install_requires=["boto3", "eth-brownie", "moonworm", "tqdm", "tabulate"],
    extras_require={
        "dev": ["black", "isort"],
        "distribute": ["setuptools", "twine", "wheel"],
    },
    description="Moonstream Engine CLI for blockchain operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Moonstream",
    author_email="engineering@moonstream.to",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "enginecli=enginecli.cli:main",
        ]
    },
    include_package_data=True,
)
