from setuptools import find_packages, setup

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

setup(
    name="lootbox",
    version="0.0.2",
    packages=find_packages(),
    install_requires=["boto3", "bugout", "eth-brownie", "fastapi", "pydantic", "tqdm","uvicorn", "web3"],
    extras_require={
        "dev": [
            "black",
            "moonworm >= 0.1.14",
        ],
        "distribute": ["setuptools", "twine", "wheel"],
    },
    description="Command line interface to the Unicorn milk bottler contract",
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
            "lootbox=lootbox.cli:main",
        ]
    },
    include_package_data=True,
)
