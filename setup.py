from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def get_version():
    version_ns = {}
    with open("bugscanx/__version__.py", "r", encoding="utf-8") as f:
        exec(f.read(), version_ns)
    return version_ns["__version__"]

setup(
    name="bugscan-x",
    version=get_version(),
    author="Ayan Rajpoot",
    author_email="ayanrajpoot2004@gmail.com",
    url="https://github.com/Ayanrajpoot10/bugscan-x",
    description="multifunctional tool for bug host hunting",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "bugscanx=bugscanx.main:main_menu",
        ],
    },
)
