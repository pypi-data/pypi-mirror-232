from setuptools import setup

# Read the README.md file with UTF-8 encoding
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="datanexus",
    version="0.0.8",
    description="A dataset module for your projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ethan Barr",
    author_email="ethanwbarr07@gmail.com",
    packages=["datanexus"],
    install_requires=[
        "Requests==2.28.2"
    ],
)
