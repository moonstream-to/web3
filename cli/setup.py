from setuptools import find_packages, setup

with open("enginecli/version.txt") as ifp:
    VERSION = ifp.read().strip()

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

setup(
    name="enginecli",
    version=VERSION,
    packages=find_packages(),
    install_requires=["boto3", "eth-brownie", "tqdm", "tabulate"],
    extras_require={
        "dev": ["black", "moonworm >= 0.3.0"],
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
