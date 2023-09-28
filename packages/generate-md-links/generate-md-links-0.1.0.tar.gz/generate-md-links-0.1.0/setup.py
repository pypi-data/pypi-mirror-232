from setuptools import setup, find_packages

setup(
    name="generate-md-links",
    version="0.1.0",
    author="xgh",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "generate-md-links = src.generate_MD_links:main",
        ]
    },
)
