# setup.py
# Legacy compatibility for PyFBB

from setuptools import setup, find_packages

setup(
    name="pyfbb",
    version="0.1.2",
    description="F6FBB packet radio BBS forwarding library",
    author="Kris Kirby, KE4AHR",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pyserial; platform_system != 'Windows'",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Ham Radio",
    ],
)
