from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="TonicPublisherAPI",
    version="0.1.4.2",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.5",
        "aiodns>=3.0.0",
    ],
    description="Async API wrapper for Tonic.com Publisher API v3",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
