from setuptools import setup


def readme():
    with open('README.md') as file:
        _readme = file.read()

    return _readme


setup(
    name='epic_games_free',
    version='0.1.4',
    author='liner',
    author_email='contact.liner999@gmail.com',
    description='An Epic Games Store free games API wrapper',
    long_description=readme(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=['epic_games_free'],
    url='https://github.com/r-liner/epic_games_free/',
    package_data={'epic_free_games': ["VERSION"]},
    include_package_data=True,
    install_requires=['requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
