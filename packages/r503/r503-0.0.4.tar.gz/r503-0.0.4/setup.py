from setuptools import setup, find_packages

DESCRIPTION = 'Fingerprint reader R503'
with open('README.md', 'r') as rdm:
    LONG_DESCRIPTION = rdm.read()
# LONG_DESCRIPTION = 'A package that allows a computer to direct interface with GROW R503 finger print sensor without using an external microcontroller'
VERSION = '0.0.4'
# Setting up
setup(
    name="r503",
    author="RoshanCS",
    version=VERSION,
    author_email="<roshan.cs790@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    url='https://github.com/rshcs/Grow-R503-Finger-Print',
    project_urls={
        'Tracker': 'https://github.com/rshcs/Grow-R503-Finger-Print/issues'
    },
    packages=find_packages(),
    license='MIT',
    install_requires=['pyserial'],
    keywords=['python', 'fingerprint', 'security', 'grow', 'r503', 'password'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
    ]
)