from pathlib import Path

from setuptools import find_packages, setup

HERE = Path(__file__).parent.resolve()

setup(
    name="riposte",
    use_scm_version={
        "root": str(HERE),
        "write_to": str(HERE / "riposte" / "_version.py"),
    },
    packages=find_packages(),
    url="https://github.com/fwkz/riposte",
    license="MIT",
    author="Mariusz Kupidura",
    author_email="f4wkes@gmail.com",
    description="REPL for humans",
    setup_requires=[
        "setuptools_scm",
    ],
    install_requires=[],
    extras_require={
        "dev": [
            "flake8",
            "pexpect",
            "pytest",
            "unify",
            "isort",
        ]
    },
    classifiers=[
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",

        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
    ],
)
