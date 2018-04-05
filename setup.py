from distutils.core import setup

setup(
    name='riposte',
    version='0.0.1',
    packages=['riposte'],
    url='https://github.com/fwkz/riposte',
    license='MIT',
    author='Mariusz Kupidura',
    author_email='f4wkes@gmail.com',
    description='REPL for humans',
    extras_require={
        "dev": [
            "flake8",
            "pytest",
        ]
    }
)
