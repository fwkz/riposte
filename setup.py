from pathlib import Path

from setuptools import find_packages, setup

HERE = Path(__file__).parent.resolve()

setup(
    name="riposte",
    use_scm_version={
        "root": str(HERE),
        "write_to": str(HERE / "riposte" / "_version.py"),
    },
    description="REPL for humans",
    license="MIT",
    url="https://github.com/fwkz/riposte",
    author="Mariusz Kupidura",
    author_email="f4wkes@gmail.com",
    packages=find_packages(),
    python_requires=">=3.6",
    zip_safe=False,
    test_suite="tests",
    install_requires=[],
    extras_require={"dev": ["black", "flake8", "isort", "pytest"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Operating System :: POSIX",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Shells",
    ],
)
