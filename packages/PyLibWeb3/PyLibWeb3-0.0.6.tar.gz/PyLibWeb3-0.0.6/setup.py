from setuptools import setup, find_packages


VERSION = '0.0.6'
DESCRIPTION = 'A package that allows you to import your modules and libraries and updates them automatically.'

# Setting up
setup(
    name="PyLibWeb3",
    version=VERSION,
    author="Makeley",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests', 'colorama'],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)