from setuptools import setup

VERSION = "1.0.6"

DESCRIPTION = "The database for unstructured data and AI apps"
AUTHOR = "BerryDB"
URL = "https://app.berrydb.io"

setup(
    name="berrydb",
    version=VERSION,
    description=DESCRIPTION,
    url=URL,
    author=AUTHOR,
    license="Proprietary",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "requests",
        "openai",
        "langchain",
        "tiktoken",
        "faiss-cpu",
        "jq"
    ],
    classifiers=[
        "License :: Other/Proprietary License",
    ],
    py_modules=["BerryDB", "utils", "loaders", "embeddings"]
)
