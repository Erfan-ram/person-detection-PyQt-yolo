"""Setup script for Person Detection System."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="person-detection-pyqt-yolo",
    version="1.0.0",
    author="Erfan-ram",
    description="A robust desktop application for real-time person detection using PyQt6 and YOLO",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Erfan-ram/person-detection-PyQt-yolo",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Video :: Capture",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "person-detection=person_detection.main:main",
        ],
    },
    package_data={
        "person_detection": ["*.md"],
    },
    include_package_data=True,
    zip_safe=False,
)