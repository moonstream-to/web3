from setuptools import find_packages, setup

with open("engineapi/version.txt") as ifp:
    VERSION = ifp.read().strip()

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

setup(
    name="engineapi",
    version=VERSION,
    packages=find_packages(),
    install_requires=[
        "alembic",
        "boto3",
        "eip712",
        "fastapi",
        "psycopg2-binary",
        "pydantic",
        "sqlalchemy",
        "tqdm",
        "uvicorn",
        "web3",
    ],
    extras_require={
        "dev": ["black"],
        "distribute": ["setuptools", "twine", "wheel"],
    },
    description="Command line interface for Moonstream Engine API",
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
            "engineapi=engineapi.cli:main",
        ]
    },
    include_package_data=True,
)
