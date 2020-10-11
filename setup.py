from pathlib import Path

from setuptools import find_packages, setup

HERE = Path(__file__).parent.resolve()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="riposte",
    use_scm_version={
        "root": str(HERE),
        "write_to": str(HERE / "riposte" / "_version.py"),
    },
    description=(
        "Package for wrapping applications inside "
        "a tailored interactive shell."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/fwkz/riposte",
    author="Mariusz Kupidura",
    author_email="f4wkes@gmail.com",
    packages=find_packages(),
    python_requires=">=3.6",
    extras_require={
        "dev": [
            "black",
            "flake8",
            "isort",
            "pytest",
            "setuptools_scm",
            "twine",
            "wheel",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: POSIX",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Shells",
    ],
)
