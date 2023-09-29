from setuptools import setup, find_packages
from alx_tool.version import __version__

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="alx-tool",
    version=__version__,
    author="Amon Munyai",
    author_email="Amonmunyai11@gmail.com",
    description="A Python package for automating ALX School tasks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AmonMunyai/alx-tool",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=[
        "scrapy==2.5.1",
        "cryptography==3.4.8",
    ],
    entry_points={
        "console_scripts": [
            "alx-tool=alx_tool.__main__:main",
        ],
    },
)
