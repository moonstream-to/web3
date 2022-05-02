from setuptools import find_packages, setup

with open("lootbox/version.txt") as ifp:
    VERSION = ifp.read().strip()

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

setup(
    name="lootbox",
    version=VERSION,
    packages=find_packages(),
    install_requires=[
        "alembic",
        "boto3",
        "eth-brownie",
        "fastapi",
        "psycopg2-binary",
        "pydantic",
        "sqlalchemy",
        "tqdm",
        "uvicorn",
        "web3",
    ],
    extras_require={
        "dev": [
            "black",
            "moonworm >= 0.1.14",
        ],
        "distribute": ["setuptools", "twine", "wheel"],
    },
    description="Command line interface for moonstream-engine.",
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
            "workers=workers.fetcher-worker:main",
        ]
    },
    include_package_data=True,
)
