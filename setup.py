from setuptools import find_packages, setup

setup(
    name="riposte",
    version="0.0.1",
    packages=find_packages(),
    url="https://github.com/fwkz/riposte",
    license="MIT",
    author="Mariusz Kupidura",
    author_email="f4wkes@gmail.com",
    description="REPL for humans",
    install_requires=[],
    extras_require={
        "dev": [
            "flake8",
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
