from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bugscan-x",
    version="1.1.0",
    author="Ayan Rajpoot",
    author_email="ayanrajpoot2004@gmail.com",
    description="multifunctional tool for bug hunting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ayanrajpoot10/BugScanX",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[

    ],
    entry_points={
        "console_scripts": [
            "bugscanx=bugscanx.main:main_menu",
        ],
    },
    license="MIT",
)
