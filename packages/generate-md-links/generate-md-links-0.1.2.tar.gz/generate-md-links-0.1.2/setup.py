from setuptools import setup, find_packages

setup(
    name="generate-md-links",
    version="0.1.2",
    author="xgh",
    packages=find_packages(),
    description="Generate Markdown links for specified files.",
    long_description=open("README.md", encoding="utf8").read(),
    url="https://gitee.com/763593659/generate_-md_links",
    entry_points={
        "console_scripts": [
            "x-generate-md-links = src.generate_MD_links:main",
        ]
    },
)
