import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
name="AutoTransferMachine",
version="0.0.2",
author="hudan717",
author_email="dahupt@gmail.com",
description="PT自动转载工具",
long_description=long_description,
long_description_content_type="text/markdown",
url="https://github.com/Ethan930717/AutoTransferMachine",
packages=setuptools.find_packages(),
License='MIT',
install_requires=[
"ffmpeg",
"mediainfo",
"maketorrent",
"loguru",
"pyyaml",
"doubaninfo",
"requests",
"beautifulsoup4",
"lxml",
"cloudscraper",
"qbittorrent-api",
"openpyxl",
"torf",
"typing",
"pathlib",
"progress"
],
)